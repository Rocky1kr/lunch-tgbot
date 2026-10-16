"""5단계 — AI에게 묻는다 (OpenAI)

- .env: AI_PROVIDER=openai · OPENAI_API_KEY=(강사가 알려준 반 공용 키) · AI_MODEL=gpt-6-luna
- AI_PROVIDER=fake 면 인터넷·키 없이 고정 답 (수업 중 네트워크가 끊겨도 흐름 확인용)
- 확인: uv run pytest tests/test_ai.py
"""

import os

import openai

FAKE_ANSWER = "[fake] 비 오는 날엔 따뜻한 김치찌개 어때요?"


def ask_ai(system, user_text):
    """지침(system)과 사용자의 말(user_text)을 AI에게 주고 답 글자를 돌려준다.

    - AI_PROVIDER가 비어 있거나 "fake"면 FAKE_ANSWER
    - "openai"면 OpenAI Responses API: client.responses.create(model=AI_MODEL, instructions=system,
      input=user_text, max_output_tokens=1000, reasoning={"effort": "low"}) → response.output_text
    - AI_MODEL이 없으면 "AI_MODEL이 .env에 없어요." · OPENAI_API_KEY가 없으면 "OPENAI_API_KEY가 .env에 없어요."
    - openai.APIError가 나도 봇이 죽지 않게: 터미널에 오류를 찍고 "AI가 지금 답을 못 해요. 잠시 뒤에 다시 물어봐 주세요."
    - 성공하면 터미널에 [토큰] 입력 … · 출력 … 을 찍는다 (토큰 = 요금의 단위)
    """
    provider = os.getenv("AI_PROVIDER", "")
    if provider in ("", "fake"):
        return FAKE_ANSWER
    if provider != "openai":
        return "AI_PROVIDER는 openai 또는 fake 여야 해요."

    model = os.getenv("AI_MODEL")
    if not model:
        return "AI_MODEL이 .env에 없어요."
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "OPENAI_API_KEY가 .env에 없어요."

    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.responses.create(
            model=model,
            instructions=system,
            input=user_text,
            max_output_tokens=1000,
            reasoning={"effort": "low"},
        )
    except openai.APIError as e:
        print("[AI 오류]", e)
        return "AI가 지금 답을 못 해요. 잠시 뒤에 다시 물어봐 주세요."

    print(f"[토큰] 입력 {response.usage.input_tokens} · 출력 {response.usage.output_tokens}")
    return response.output_text
