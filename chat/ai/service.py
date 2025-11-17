import json
import asyncio
from urllib.parse import parse_qs

from asgiref.sync import sync_to_async
from django.apps import apps
from django.contrib.auth.models import AnonymousUser



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
     
@sync_to_async
def get_history(history_id: str):
    SolutionHistory = apps.get_model("solutions", "SolutionHistory")
    return SolutionHistory.objects.get(pk=history_id)

@sync_to_async
def load_recent_history(history_id: str, limit: int = 30):
    Message = apps.get_model("solutions", "Message")
    qs = (
        Message.objects
        .filter(solution_history_id=history_id)
        .order_by("-created_at")[:limit]
        .values("sender", "content")
    )
    items = list(qs)
    items.reverse()
    
    history = []
    for item in items:
        sender_code = item["sender"]
        content = item["content"] or ""
        role = "user" if sender_code == 0 else "model"
        
        history.append({
            "sender": role,
            "content": content,
        })
    
    return history


@sync_to_async
def save_message(history_id: str, content: str, sender: int):
    """
    sender: 0=user, 1=ai
    """
    SolutionHistory = apps.get_model("solutions", "SolutionHistory")
    Message = apps.get_model("solutions", "Message")

    sh = SolutionHistory.objects.get(pk=history_id)

    return Message.objects.create(
        solution_history=sh,
        sender=sender,
        content=content,
    )