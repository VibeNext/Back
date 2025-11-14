import os
import asyncio
from typing import AsyncGenerator, List, Dict, Optional

from google import genai
from google.genai import types

# 클라이언트 전역 1회 생성
_client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

MODEL_ID = "gemini-live-2.5-flash-preview"


async def stream_from_gemini(
    prompt: str,
    history: Optional[List[Dict]] = None,
    system_instruction: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    """
    Gemini Live API에서 텍스트를 스트리밍으로 받아오는 헬퍼.

    history 형식 예시:
    [
      {"sender": "user", "content": "안녕"},
      {"sender": "model", "content": "안녕하세요~"},
      ...
    ]
    """

    config = {
        "response_modalities": ["TEXT"],
        "system_instruction": system_instruction or "You are a helpful assistant.",
        "generation_config": {
            "temperature": 0.7,
            "max_output_tokens": 1024,
        },
    }

    try:
        async with _client.aio.live.connect(model=MODEL_ID, config=config) as session:
            # 1) history + 이번 prompt를 하나의 turns 리스트로 구성
            turns: List[types.Content] = []

            if history:
                for msg in history:
                    role = "user" if msg.get("sender") == "user" else "model"
                    text = (msg.get("content") or "").strip()
                    if not text:
                        continue

                    turns.append(
                        types.Content(
                            role=role,
                            parts=[types.Part(text=text)],
                        )
                    )

            # 이번 사용자 입력
            turns.append(
                types.Content(
                    role="user",
                    parts=[types.Part(text=prompt)],
                )
            )

            # 2) 한 번에 전송 + 턴 종료 (여기서부터 생성 시작)
            await session.send_client_content(
                turns=turns,
                turn_complete=True,
            )

            # 3) 응답 스트리밍 받기
            async for chunk in session.receive():
                # 최신 SDK는 chunk.text 편의 필드도 있음
                if getattr(chunk, "text", None):
                    yield chunk.text
                    continue

                sc = getattr(chunk, "server_content", None)
                if not sc:
                    continue

                model_turn = getattr(sc, "model_turn", None)
                if not model_turn:
                    continue

                for part in model_turn.parts or []:
                    text = getattr(part, "text", None)
                    if text:
                        yield text

    except Exception as e:
        print(f"Error in stream_from_gemini: {e}")
