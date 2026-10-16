"""5·6단계 — AI에게 주는 지침(system prompt). 지침을 바꾸면 같은 AI가 다르게 답한다.

- 확인: uv run pytest tests/test_prompts.py
"""

from places import place_text

# V1: 아무 정보도 안 준다 → AI가 그럴듯한 식당·메뉴를 지어낸다 (5단계)
SYSTEM_PROMPT_V1 = "너는 점심 메뉴를 추천하는 봇이다. 짧게 한국어로 답한다."

# 명령이 아닌 말이 왔을 때: 무슨 말이든 일반 대화 (텔레그램은 글자 수 제한이 있어 짧게)
SYSTEM_PROMPT_CHAT = "너는 텔레그램에서 대화하는 친절한 봇이다. 무슨 말이든 한국어로 짧게 답한다."


def build_prompt_v2(weather, meals):
    """V2: 나에 대한 정보를 준다 (6단계).

    - weather: 날씨 한 줄 글 (예: "비, 12.0°C, 강수 3.0mm") · meals: db.recent_meals()의 [(시각, 메뉴), ...]
    - 지침에 "지금 캠퍼스 날씨: …"와 "사용자가 최근에 먹은 것: …"(없으면 "기록 없음")을 넣는다
    - 날씨와 최근 먹은 것을 고려해 메뉴 하나를 이유와 함께 추천하게 한다
    - 식당 이름은 말하지 않게 한다 ("너는 이 동네 식당을 모른다")
    """
    if meals:
        eaten = ", ".join(f"{menu}({eaten_at})" for eaten_at, menu in meals)
    else:
        eaten = "기록 없음"
    return (
        "너는 점심 메뉴를 추천하는 봇이다. 짧게 한국어로 답한다.\n"
        f"지금 캠퍼스 날씨: {weather}\n"
        f"사용자가 최근에 먹은 것: {eaten}\n"
        "날씨와 최근에 먹은 것을 고려해서 메뉴 하나를 이유와 함께 추천한다. "
        "최근에 먹은 메뉴는 피한다.\n"
        "너는 이 동네 식당을 모른다. 식당 이름은 절대 말하지 않는다."
    )


def build_prompt_v3(weather, meals, found):
    """V3: + 캠퍼스 주변 식당 목록에서 질문에 맞게 찾은 것(found, places.search 결과)을 준다 (6단계).

    - V2의 날씨·최근 먹은 것 + 찾은 식당을 places.place_text로 한 줄씩
    - 찾은 식당이 없으면 "(질문에 맞는 식당을 목록에서 찾지 못했다)"라고 적는다 (안 적으면 AI가 빈자리를 지어낸다)
    - 이 목록 안에서만 하나 골라 추천하고, 출처 링크를 같이 알려 주게 한다. 없으면 없다고 말하게 한다
    """
    if meals:
        eaten = ", ".join(f"{menu}({eaten_at})" for eaten_at, menu in meals)
    else:
        eaten = "기록 없음"
    if found:
        places = "\n".join(place_text(place) for place in found)
    else:
        places = "(질문에 맞는 식당을 목록에서 찾지 못했다)"
    return (
        "너는 캠퍼스 주변 점심 식당을 추천하는 봇이다. 짧게 한국어로 답한다.\n"
        f"지금 캠퍼스 날씨: {weather}\n"
        f"사용자가 최근에 먹은 것: {eaten}\n"
        f"질문에 맞는 캠퍼스 주변 식당 목록:\n{places}\n"
        "위 목록 안에서만 식당 하나를 골라 이유와 함께 추천하고, 그 식당의 출처 링크를 같이 알려 준다. "
        "목록에 없는 식당은 절대 지어내지 않는다. "
        "목록에서 찾지 못했다면 못 찾았다고 솔직하게 말한다."
    )
