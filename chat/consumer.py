# chat/consumers.py
import json
import asyncio
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.apps import apps
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from chat.ai.service import (
    get_system_instruction,
    user_can_access,
    get_history,
    load_recent_history,
    save_message,
)

from chat.ai.genhelper import stream_from_gemini


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        path = self.scope.get("path")
        query = self.scope.get("query_string")
        user = self.scope.get("user")

        print("=== CONNECT CALLED ===")
        print("PATH:", path, "QUERY:", query, "USER:", user)

        history_id = self.scope.get("url_route", {}).get("kwargs", {}).get("history_id")
        print("history_id from url_route:", history_id)

        if not history_id:
            print("[CONNECT] NO HISTORY_ID -> close 4400")
            await self.close(code=4400)
            return

        try:
            sh = await get_history(history_id)
            print("[CONNECT] FOUND SolutionHistory:", sh.pk)
        except Exception as e:
            print("[CONNECT] get_history ERROR:", repr(e))
            await self.close(code=4404)
            return

        self.history_id = str(sh.pk)

        self.system_instruction = await get_system_instruction(self.history_id)

        await self.accept()
        await self.send_json({
            "type": "system",
            "message": "connected",
            "history_id": self.history_id
        })



    async def disconnect(self, close_code):
        # 진행 중인 AI 스트림이 있으면 취소
        ai_task = getattr(self, "ai_task", None)
        if ai_task and not ai_task.done():
            ai_task.cancel()

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
        await save_message(self.history_id, message, sender=0)

        # 내 화면에 바로 표시
        await self.send_json({"type": "message", "user": username, "message": message})

        deltas = []
        error_text = None

        # AI context 유지용
        try:
            history = []
            history = await load_recent_history(self.history_id, limit=30)

            print("[AI] start prompt:", repr(message))

            async for chunk in stream_from_gemini(
                prompt=message,
                history=history,
                system_instruction=self.system_instruction,
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
                await save_message(self.history_id, full, sender=1)
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

    async def send_json(self, payload: dict):
        await self.send(text_data=json.dumps(payload))