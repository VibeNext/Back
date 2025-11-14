# chat/consumers.py
import json
import asyncio
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.apps import apps
from django.contrib.auth.models import AnonymousUser
from chat.ai.genhelper import stream_from_gemini
from django.contrib.auth import get_user_model

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("WS PATH:", self.scope.get("path"), "QUERY:", self.scope.get("query_string"))

        # ws/Solution/<history_id>/chat/  (history_id = nanoid)
        self.history_id = self.scope['url_route']['kwargs']['history_id']
        self.ai_task = None
        
        # ✅ mock 플래그 파싱
        query = parse_qs(self.scope.get("query_string", b"").decode())
        self.mock = query.get("mock", ["0"])[0] in ("1", "true", "True")

        # 권한 체크
        # if not await self.user_can_access(self.scope.get("user"), self.history_id):
        #     await self.close(code=4403)
        #    return
        
        if self.mock:
            # ✅ 개발 모드: 권한/DB 건너뛰고 즉시 수락
            await self.accept()
            await self.send_json({"type": "system", "message": "connected (mock=True)"})
            return

        await self.accept()
        await self.send_json({"type": "system", "message": "connected"})
        await self.send_json({"type": "message", "user": "ai", "message": "[TEST] hello from server"})

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

        # DB 저장
        if not self.mock:
            await self.save_message(self.history_id, user, message, sender=0)

        # 2) 내 화면에 바로 표시
        await self.send_json({"type": "message", "user": username, "message": message})

        # 3) AI 생각중 표시
        await self.send_json({"type": "ai_thinking", "user": "ai"})

        deltas = []
        error_text = None

        try:
            history = []
            if not self.mock:
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

            print("[AI] final:", repr(full))
            await self.send_json({"type": "message", "user": "ai", "message": full})

            if not self.mock:
                try:
                    await self.save_message(self.history_id, None, full, sender=1)
                except Exception as se:
                    print("[AI] save_message EXC:", se)

            await self.send_json({"type": "ai_done", "user": "ai"})
 
    

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
                await self.save_message(self.history_id, None, full_text, sender="assistant")

            # 최종 한 번만 전송
            await self.send_json({"type": "message", "user": "ai", "message": full_text})
            await self.send_json({"type": "ai_done", "user": "ai"})

        except asyncio.CancelledError:
            # 새 사용자 메시지로 이전 스트림 취소된 경우
            pass

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
        solutionHistory = apps.get_model("solutions", "SolutionHistory")
        User = get_user_model()

        # 1) owner 결정: 로그인 유저가 있으면 그거, 아니면 mock 유저
        if user and getattr(user, "is_authenticated", False):
            owner = user
        else:
            # 🔥 여기 email은 아까 shell에서 만든 mock 유저 이메일이랑 맞추기
            owner = User.objects.get(email="mock@example.com")

        sh, created = solutionHistory.objects.get_or_create(
            pk=history_nanoid,
            defaults={"user": owner},
        )
        return sh
    
    @sync_to_async
    def load_recent_history(self, history_nanoid, limit=20):
        Message = apps.get_model("solutions", "Message")
        qs = (Message.objects
              .filter(solution_history_id=history_nanoid)
              .order_by('-created_at')[:limit]
              .values("sender", "content"))
        items = list(qs)
        items.reverse()  # 오래된 것부터
        return items

    @sync_to_async
    def get_system_instruction(self) -> str:
        # 초기 프롬프트
        return "You are a helpful assistant. Answer briefly and clearly."

    @sync_to_async
    def save_message(self, history_nanoid, user, content: str, sender: str):
        solutionHistory = apps.get_model("solutions", "SolutionHistory")
        Message = apps.get_model("solutions", "Message")
        User = get_user_model()

        # 1) owner 결정: 실제 로그인 유저가 있으면 그걸 쓰고,
        #    아니면 mock 유저로 대체
        if user and getattr(user, "is_authenticated", False):
            owner = user
        else:
            owner = User.objects.get(email="mock@example.com")

        # 2) SolutionHistory 없으면 자동 생성
        sh, _ = solutionHistory.objects.get_or_create(
            pk=history_nanoid,
            defaults={"user": owner},
        )

        # 3) Message 저장
        return Message.objects.create(
            solution_history=sh,
            sender=sender,      # 'user' / 'ai'
            content=content,
        )

    
    @sync_to_async
    def save_message(self, history_nanoid, user, content: str, sender: str):
        solutionHistory = apps.get_model("solutions", "SolutionHistory")
        Message = apps.get_model("solutions", "Message")

        # 🔹 기존: sh = solutionHistory.objects.get(pk=history_nanoid)
        # 🔹 변경: 없으면 새로 생성
        sh, user= solutionHistory.objects.get_or_create(
            pk=history_nanoid,
            defaults={
                "user": user if user and not isinstance(user, AnonymousUser) and user.is_authenticated else None,
                "mission_id": 13, # 기본값 설정
            }
        )

        return Message.objects.create(
            solution_history=sh,
            sender=sender,      # 'user' / 'ai'
            content=content,
        )
    async def send_json(self, payload: dict):
        await self.send(text_data=json.dumps(payload))

