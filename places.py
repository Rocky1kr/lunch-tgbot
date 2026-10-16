"""6단계 — 캠퍼스 주변 식당 목록을 읽고, 질문에 맞는 식당을 찾는다

- places_sample.csv: 카카오맵에서 모은 40곳 (2026-10-15~16 기준)
- 열: 이름, 분류, 대표 메뉴, 영업시간, 주소, 캠퍼스에서 직선거리(m), 출처
- 확인: uv run pytest tests/test_places.py
"""
import csv


def load_places(path):
    """CSV 파일을 [{"이름": ..., "분류": ..., ...}, ...]로 읽는다.

    - 첫 줄(열 이름)을 열쇠로 쓴다 (csv.DictReader)
    - encoding="utf-8" (안 적으면 Windows에서 한글이 깨진다)
    """
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def search(question, places, limit=5):
    """질문에 맞는 식당을 찾는다 (간단한 키워드 검색).

    - 질문을 띄어쓰기로 나누고 두 글자 이상 단어만 쓴다
    - 이름 · 분류 · 대표 메뉴를 이어 붙인 글에 단어가 들어 있으면 1점씩
    - 1점 이상인 식당을 점수 높은 순으로 limit개. 점수가 같으면 목록 순서대로
    """
    words = [w for w in question.split() if len(w) >= 2]
    scored = []
    for place in places:
        text = place["이름"] + place["분류"] + place["대표 메뉴"]
        score = sum(1 for w in words if w in text)
        if score >= 1:
            scored.append((score, place))
    scored.sort(key=lambda pair: -pair[0])  # sort는 같은 점수끼리 원래 순서를 지킨다
    return [place for _, place in scored[:limit]]


def place_text(place):
    """식당 하나를 AI 지침에 넣을 한 줄로.

    모양: "{이름}({분류}) — 대표 메뉴: {대표 메뉴} · 영업: {영업시간} · 캠퍼스에서 직선 {거리}m · 출처: {출처}"
    """
    return (
        f"{place['이름']}({place['분류']}) — 대표 메뉴: {place['대표 메뉴']}"
        f" · 영업: {place['영업시간']}"
        f" · 캠퍼스에서 직선 {place['캠퍼스에서 직선거리(m)']}m"
        f" · 출처: {place['출처']}"
    )
