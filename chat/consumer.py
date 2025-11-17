# chat/consumers.py
import json
import asyncio
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.apps import apps
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model

from chat.ai.genhelper import stream_from_gemini


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("WS PATH:", self.scope.get("path"), "QUERY:", self.scope.get("query_string"))

        history_id = self.scope.get("url_route", {}).get("kwargs", {}).get("history_id")

        if not history_id:
            # history_id 없으면 바로 연결 종료
            await self.close(code=4400)
            return

        user = self.scope.get("user")

        # 권한 체크 쓰려면 여기서
        # if not await self.user_can_access(user, history_id):
        #     await self.close(code=4403)
        #     return

        # 2) 이미 만들어져 있는 history만 조회
        try:
            sh = await self.get_or_create_history(history_id, user)
        except Exception as e:
            # SolutionHistory 없으면 바로 끊어버림
            print("get_or_create_history error:", e)
            await self.close(code=4404)
            return

        self.history_id = str(sh.pk)

        await self.accept()
        await self.send_json({
            "type": "system",
            "message": "connected",
            "history_id": self.history_id
        })


    async def disconnect(self, close_code):
        # 진행 중인 AI 스트림이 있으면 취소
        if self.ai_task and not self.ai_task.done():
            self.ai_task.cancel()

    async def receive(self, text_data=None, bytes_data=None):
        # 클라이언트가 보낸 메시지 파싱
        try:
            data = json.loads(text_data or "{}")
        except json.JSONDecodeError:
            data = {"message": (text_data or "").strip()}

        message = (data.get("message") or "").strip()
        if not message:
            return

        user = self.scope.get("user")
        username = user.username if user and user.is_authenticated else "anonymous"

        # 사용자 메시지 DB 저장
        await self.save_message(self.history_id, user, message, sender=0)

        # 내 화면에 바로 표시
        await self.send_json({"type": "message", "user": username, "message": message})

        deltas = []
        error_text = None

        # AI context 유지용
        try:
            history = []
            history = await self.load_recent_history(self.history_id, limit=20)

            print("[AI] start prompt:", repr(message))

            async for chunk in stream_from_gemini(
                prompt=message,
                history=history,
                system_instruction="You are a helpful assistant for this app.",
            ):
                if not chunk:
                    continue
                deltas.append(chunk)
                print("[AI] delta:", repr(chunk))
                await self.send_json({"type": "ai_delta", "delta": chunk})

        except Exception as e:
            # 예외라도 최종 메시지는 내려가게
            error_text = f"(AI error) {e.__class__.__name__}: {e}"
            print("[AI] EXC:", error_text)

        finally:
            full = "".join(deltas).strip()
            if error_text and not full:
                full = error_text
            if not full:
                # 모델이 빈값 준 경우에도 사용자 화면엔 뭔가 보이게
                full = "[AI returned empty response]"

            # AI 최종 메시지 전송
            print("[AI] final:", repr(full))
            await self.send_json({"type": "message", "user": "ai", "message": full})

            try:
                await self.save_message(self.history_id, None, full, sender=1)
            except Exception as se:
                print("[AI] save_message EXC:", se)

 
 # ---------------- 내부 헬퍼들 ----------------
    def _get_owner(self, user):
        """
        실제 로그인 유저가 있으면 그걸 쓰고,
        아니면 mock 유저(개발용)를 owner로 사용.
        """
        User = get_user_model()
        if user and not isinstance(user, AnonymousUser) and getattr(user, "is_authenticated", False):
            return user
        # TODO: 운영에서는 anonymous 정책에 맞게 처리
        return User.objects.get(email="mock@example.com")
    

    async def _run_ai_stream(self, prompt: str):
        """AI 응답을 스트리밍으로 받아 조각을 모은 뒤, 최종 한 번만 전송."""
        try:
            history = []
            system_instruction = "You are a helpful assistant."

            # 실제 모드면 최근 히스토리 로드
            if not self.mock:
                history = await self.load_recent_history(self.history_id, limit=20)
                system_instruction = await self.get_system_instruction()

            deltas = []
            
            async for chunk in stream_from_gemini(prompt, history=history, system_instruction=system_instruction):
                deltas.append(chunk)

            full_text = "".join(deltas).strip()

            # DB에 AI 답변 저장
            if not self.mock:
                await self.save_message(self.history_id, None, full_text, sender=1)

            # 최종 한 번만 전송
            await self.send_json({"type": "message", "user": "ai", "message": full_text})
            await self.send_json({"type": "ai_done", "user": "ai"})

        except asyncio.CancelledError:
            # 새 사용자 메시지로 이전 스트림 취소된 경우
            pass
        
    def _get_or_create_history_sync(self, history_nanoid, user=None):
        SolutionHistory = apps.get_model("solutions", "SolutionHistory")
        # 자동 생성 안 하고, pk로만 조회
        return SolutionHistory.objects.get(pk=history_nanoid)


    # ---------------- 권한 & DB I/O ----------------

    @sync_to_async
    def user_can_access(self, user, history_nanoid) -> bool:
        solutionHistory = apps.get_model("solutions", "SolutionHistory")
        try:
            sh = solutionHistory.objects.select_related("user").get(pk=history_nanoid)
        except solutionHistory.DoesNotExist:
            return False

        if user is None or isinstance(user, AnonymousUser):
            return False

        # 소유자만 입장 허용
        # return user == getattr(sh, "user", None)

    @sync_to_async
    def get_or_create_history(self, history_nanoid, user):
        return self._get_or_create_history_sync(history_nanoid, user)
    
    @sync_to_async
    def load_recent_history(self, history_nanoid, limit=20):
        """
        Gemini에 넘길 history 형식:
        [
          {"sender": "user", "content": "..."},   # sender: 'user' or 'model'
          {"sender": "model", "content": "..."},
          ...
        ]
        """
        Message = apps.get_model("solutions", "Message")
        qs = (
            Message.objects
            .filter(solution_history_id=history_nanoid)
            .order_by('-created_at')[:limit]
            .values("sender", "content")   # sender: int (0=user, 1=ai)
        )
        items = list(qs)
        items.reverse()  # 오래된 것부터

        history = []
        for item in items:
            sender_code = item["sender"]
            content = item["content"] or ""

            # Gemini role: 'user' / 'model'
            role = "user" if sender_code == 0 else "model"

            history.append({
                "sender": role,
                "content": content,
            })

        return history

    @sync_to_async
    def save_message(self, history_nanoid, user, content: str, sender: int):
        """
        sender: 0=user, 1=ai (Message 모델의 IntegerField choices와 맞춰야 함)
        """
        solutionHistory = apps.get_model("solutions", "SolutionHistory")
        Message = apps.get_model("solutions", "Message")

        # history가 없으면 자동 생성 (owner 포함)
        sh = self._get_or_create_history_sync(history_nanoid, user)

        return Message.objects.create(
            solution_history=sh,
            sender=sender,      # 0 or 1
            content=content,
        )

    async def send_json(self, payload: dict):
        await self.send(text_data=json.dumps(payload))