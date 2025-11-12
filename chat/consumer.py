# chat/consumers.py
import json
import asyncio
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.apps import apps
from django.contrib.auth.models import AnonymousUser

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # ws/solutions/<history_id>/chat/  (history_id = nanoid)
        self.history_id = self.scope['url_route']['kwargs']['history_id']
        self.ai_task = None

        # 권한 체크
        if not await self.user_can_access(self.scope.get("user"), self.history_id):
            await self.close(code=4403)
            return

        await self.accept()
        await self.send_json({"type": "system", "message": "connected"})

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

        # 1) 사용자 메시지 저장
        await self.save_message(self.history_id, user, message, sender="user")

        # 2) 내 화면에 바로 표시
        await self.send_json({"type": "message", "user": username, "message": message})

        # 3) AI 생각중 표시
        await self.send_json({"type": "ai_thinking", "user": "ai"})

        # 4) 기존 스트림이 돌고 있으면 취소(또는 큐잉으로 바꿔도 됨)
        if self.ai_task and not self.ai_task.done():
            self.ai_task.cancel()

        # 5) AI 스트림 시작
        self.ai_task = asyncio.create_task(self._run_ai_stream(message))

    async def _run_ai_stream(self, prompt: str):
        """AI 응답을 스트리밍으로 받아 조각을 모은 뒤, 최종 한 번만 전송."""
        try:
            # 최근 히스토리(역순 정렬 → 다시 뒤집어 과거→현재 순서로)
            history = await self.load_recent_history(self.history_id, limit=20)
            # 초기 프롬프트
            system_prompt = await self.get_system_prompt()

            deltas = []
            # 실제 구현에서는 Gemini Live API
            async for chunk in stream_from_gemini(prompt, history=history, system_prompt=system_prompt):
                deltas.append(chunk)

            full_text = "".join(deltas).strip()

            # DB에 AI 답변 저장
            await self.save_message(self.history_id, None, full_text, sender="ai")

            # 최종 한 번만 전송
            await self.send_json({"type": "message", "user": "ai", "message": full_text})
            await self.send_json({"type": "ai_done", "user": "ai"})

        except asyncio.CancelledError:
            # 새 사용자 메시지로 이전 스트림 취소된 경우
            pass

    # ---------------- 권한 & DB I/O ----------------

    @sync_to_async
    def user_can_access(self, user, history_nanoid) -> bool:
        SolutionHistory = apps.get_model("solution", "SolutionHistory")
        try:
            sh = SolutionHistory.objects.select_related("owner").get(pk=history_nanoid)
        except SolutionHistory.DoesNotExist:
            return False

        if user is None or isinstance(user, AnonymousUser):
            return False

        # 소유자만 입장 허용
        return user == getattr(sh, "owner", None)

    @sync_to_async
    def load_recent_history(self, history_nanoid, limit=20):
        Messages = apps.get_model("solution", "Messages")
        qs = (Messages.objects
              .filter(solution_history_id=history_nanoid)
              .order_by('-created_at')[:limit]
              .values("sender", "content"))
        items = list(qs)
        items.reverse()  # 오래된 것부터
        return items

    @sync_to_async
    def get_system_prompt(self) -> str:
        # 초기 프롬프트
        return "You are a helpful assistant. Answer briefly and clearly."

    @sync_to_async
    def save_message(self, history_nanoid, user, content: str, sender: str):
        SolutionHistory = apps.get_model("solution", "SolutionHistory")
        Messages = apps.get_model("solution", "Messages")
        sh = SolutionHistory.objects.get(pk=history_nanoid)
        return Messages.objects.create(
            solution_history=sh,                      
            sender=user if user and user.is_authenticated else None,
            sender=sender,                                # 'user' / 'ai'
            content=content,                          # 메시지 내용
        )

    async def send_json(self, payload: dict):
        await self.send(text_data=json.dumps(payload))


# ----- Gemini Live API로 -----
async def stream_from_gemini(prompt: str, history=None, system_prompt: str = ""):
    # history, system_prompt를 모델 호출 시 컨텍스트로 사용하도록 구현
    fake = ["답변", " 을", " 준비", " 중...", " 완료!"]
    for c in fake:
        await asyncio.sleep(0.05)
        yield c
