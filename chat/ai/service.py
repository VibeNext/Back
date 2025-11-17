import json
import asyncio
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.apps import apps
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model

from chat.ai.genhelper import stream_from_gemini

# chat/ai/service.py
from asgiref.sync import sync_to_async
from django.apps import apps


@sync_to_async
def get_system_instruction(history_id: str) -> str:
    """
    SolutionHistory -> mission.ai_prompt 가져오고,
    없으면 디폴트 프롬프트 리턴.
    """
    SolutionHistory = apps.get_model("solutions", "SolutionHistory")

    try:
        sh = SolutionHistory.objects.select_related("mission").get(pk=history_id)
        mission = getattr(sh, "mission", None)
        prompt = getattr(mission, "ai_prompt", None)
        if prompt:
            return prompt.strip()
    except SolutionHistory.DoesNotExist:
        pass

    return "You are a helpful assistant for this app."


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