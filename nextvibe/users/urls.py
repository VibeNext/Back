from django.urls import path
from django.http import JsonResponse

def me(_): return JsonResponse({"status": "ok"})

urlpatterns = [
    path("me/", me),
]
