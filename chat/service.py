import json
import asyncio
from urllib.parse import parse_qs

from asgiref.sync import sync_to_async
from django.apps import apps
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache


from asgiref.sync import sync_to_async
from django.apps import apps


CACHE_TTL = 60 * 10 

@sync_to_async
def get_system_instruction(history_id: str) -> str:
    """
    SolutionHistory -> mission.ai_prompt, mission.question_text를 가져오고,
    없으면 디폴트 프롬프트 리턴.
    """
    SolutionHistory = apps.get_model("solutions", "SolutionHistory")

    try:
        sh = SolutionHistory.objects.select_related("mission").get(pk=history_id)
        mission = getattr(sh, "mission", None)

        if mission is not None:
            ai_prompt = getattr(mission, "ai_prompt", "") or ""
            question_text = getattr(mission, "question_text", "") or ""
            answer_assets = getattr(mission, "answer_assets", "") or ""
            question_hint = getattr(mission, "question_hint", "") or ""

            ai_prompt = ai_prompt.strip()
            question_text = question_text.strip()
            answer_assets = answer_assets.strip()

            if ai_prompt and question_text:
                    return (
                f"{ai_prompt}\n\n" 
                f"question_text: {question_text}\n" 
                f"answer_assets: {answer_assets}\n"
                f"question_hint: {question_hint}"
                )

            if ai_prompt:
                return ai_prompt

            if question_text:
                return (
                    "You are a helpful assistant for this app.\n\n"
                    f"question_text: {question_text}"
                )

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
    cache_key = f"chat_history:{history_id}"
    history = cache.get(cache_key)

    # 1) 캐시에 이미 있으면 그대로 리턴
    if history is not None:
        return history

    # 2) 캐시에 없으면 DB에서 최근 N개 가져와서 캐시에 저장
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

    cache.set(cache_key, history, CACHE_TTL)
    return history

@sync_to_async
def save_message(history_id: str, content: str, sender: int):
    """
    sender: 0=user, 1=ai
    """
    SolutionHistory = apps.get_model("solutions", "SolutionHistory")
    Message = apps.get_model("solutions", "Message")

    sh = SolutionHistory.objects.get(pk=history_id)

    msg = Message.objects.create(
        solution_history=sh,
        sender=sender,
        content=content,
    )

    cache_key = f"chat_history:{history_id}"
    history = cache.get(cache_key)

    if history is not None:
        role = "user" if sender == 0 else "model"

        history.append({
            "sender": role,
            "content": content or "",
        })

        # 최근 30개만 유지
        if len(history) > 30:
            history = history[-30:]

        cache.set(cache_key, history, CACHE_TTL)

    return msg