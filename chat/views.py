from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def chat_test(request, history_id: str):
    return render(request, "chat_test.html", {"history_id": history_id})