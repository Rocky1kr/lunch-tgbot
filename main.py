# 텔레그램이 보내 주는 메시지를 받는 서버 (webhook)
import html
import json
import os
import random
import re
from ai import ask_ai
from prompts import build_prompt_v3

import requests
from dotenv import load_dotenv
from fastapi import FastAPI

from weather import weather_text, get_weather, describe
from places import load_places, search
import db

load_dotenv()
URL = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}"

MENUS = ["라면", "햄버거", "마라탕", "샐러드"]

app = FastAPI()
conn = db.connect()
  # 웹 서버 앱
PLACES = load_places("places_sample.csv")
NEWS_URL = "https://news.hada.io/"
# 이 사이트는 기본 요청을 거절(403)해서, 브라우저인 것처럼 보내야 한다
NEWS_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9",                     
}

                                                             
def news_text():
    """GeekNews 첫 화면의 1~10번 글을 '번호. 제목 + 링크' 글자로 만든다."""
    try:                                                     
        response = requests.get(NEWS_URL, headers=NEWS_HEADERS, timeout=5)
        response.raise_for_status()  # 200이 아니면 에러로
    except requests.RequestException as e:
        print(f"[뉴스 오류] {e}")
        return "지금은 뉴스를 가져오지 못했어요."

    # 글 하나는 <a href='링크' ... class='topic-title-link'><h2 ...>제목</h2> 모양이다
    rows = re.findall(
        r"<a href='([^']+)'[^>]*class='topic-title-link'><h2[^>]*>(.*?)</h2>",
        response.text,
    )
    if not rows:
        return "뉴스 목록을 찾지 못했어요. 사이트 모양이 바뀐 것 같아요."

    lines = []
    for number, (link, title) in enumerate(rows[:10], start=1):  # 앞 10개만
        lines.append(f"{number}. {html.unescape(title)}\n{html.unescape(link)}")
    return "GeekNews 인기 글 TOP 10\n\n" + "\n\n".join(lines)
@app.post("/")  # 텔레그램이 메시지(JSON)를 이 주소로 POST 해 준다 (webhook)
def webhook(body: dict):
    # print(json.dumps(body, indent=2, ensure_ascii=False))  # 받은 JSON 전체를 보고 싶으면 앞의 #을 지운다
    message = body.get("message", {})
    if "text" not in message:  # 사진·스티커처럼 글자가 아닌 메시지는 받기만 한다
        return {"ok": True}

    chat_id = message["chat"]["id"]  # 누구에게 답할지 (JSON의 message › chat › id)
    text = message["text"]           # 보낸 글자 (JSON의 message › text)
    print("[받음]", text)

    # /로 시작하면 명령, 아니면 메아리
    if text == "/start":
        output = "안녕하세요! 오늘 뭐 먹지? 봇입니다. /help 로 사용법을 보세요."
    elif text == "/help":
        output = "/lunch 점심 메뉴 하나\n/lotto 로또 번호 6개\n/weather 지금 캠퍼스 날씨\n그 밖의 말은 따라 해요"
    elif text == "/lunch":
        output = random.choice(MENUS)
    elif text == "/lotto":
        numbers = random.sample(range(1, 46), 6)  # 1~45 중 겹치지 않게 6개 뽑기
        numbers.sort()                            # 작은 숫자부터 정렬
        output = "이번 주 행운의 번호: " + ", ".join(str(n) for n in numbers)
    elif text == "/weather":
        output = weather_text()
    elif text == "/news":
        output = news_text()
    elif text.startswith("/ate"):
        menu = text[4:].strip()  # "/ate 김치찌개" → "김치찌개"
        if menu == "":
            output = "/ate 김치찌개 처럼 먹은 메뉴를 같이 적어 주세요."
        else:
            db.save_meal(conn, menu, db.now())
            output = f"기록했어요: {menu}"
    elif text == "/history":
        meals = db.recent_meals(conn)
        if meals == []:
            output = "아직 기록이 없어요. /ate 김치찌개 처럼 적어 보세요."
        else:
            lines = [f"{eaten_at}  {menu}" for eaten_at, menu in meals]
            output = "최근에 먹은 것\n" + "\n".join(lines)
    elif text.startswith("/"):
        output = "모르는 명령이에요. /help 를 보내 보세요."
    else:
        weather = get_weather()
        weather_line = describe(weather) if weather else "날씨 정보 없음"
        meals = db.recent_meals(conn)
        found = search(text, PLACES)
        system = build_prompt_v3(weather_line, meals, found)
        output = ask_ai(system, text)  # GPT가 목록 안에서만 대답

    requests.get(f"{URL}/sendMessage", params={"chat_id": chat_id, "text": output})  # 답장 보내기
    print("[보냄]", output)
    return {"ok": True}  # 200 OK = 잘 받았다. 중간에 에러로 멈추면(500) 텔레그램이 같은 메시지를 다시 보낸다
