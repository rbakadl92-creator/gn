import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_sofr_rates():
    url = "https://www.global-rates.com/en/interest-rates/sofr/"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")
    rows = []
    for table in soup.find_all("table"):
        for tr in table.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) == 2:
                date_txt = tds[0].text.strip()
                rate_txt = tds[1].text.strip().replace("%","").strip()
                try:
                    datetime.strptime(date_txt, "%m-%d-%Y")
                    rows.append((date_txt, float(rate_txt)))
                except:
                    pass
    rows.sort(key=lambda x: datetime.strptime(x[0], "%m-%d-%Y"), reverse=True)
    return rows[0][0], rows[0][1], rows[1][0], rows[1][1]

def add_biz_days(date_str, n):
    d = datetime.strptime(date_str, "%m-%d-%Y")
    added = 0
    while added < n:
        d += timedelta(days=1)
        if d.weekday() < 5:
            added += 1
    return d.strftime("%Y-%m-%d")

if __name__ == "__main__":
    today_date, today_rate, prev_date, prev_rate = get_sofr_rates()
    RESERVE = 0.10
    SPREAD  = 4.50
    total      = round(today_rate + RESERVE + SPREAD, 2)
    prev_total = round(prev_rate  + RESERVE + SPREAD, 2)
    apply_date = add_biz_days(today_date, 2)

    print(f"오늘 SOFR: {today_rate}% ({today_date})")
    print(f"전일 SOFR: {prev_rate}% ({prev_date})")

    subject = f"[{apply_date}] 28042 DB미국광통신망선순위대출펀드 변동금리 업데이트 요청"
    body = f"""안녕하십니까 대체투자2팀 변규남 입니다

28042 DB미국광통신망선순위대출펀드의 Note (Wyyerd Group) 종목에 대한 변동금리 업데이트 요청 드립니다.

  - 종목: Note (Wyyerd Group)
  - 금리: {total}% (직전 영업일* Overnight SOFR ({today_rate:.2f}%) + Reserve Rate ({RESERVE:.2f}%) + Spread Rate ({SPREAD:.2f}%), 변경 전: {prev_total:.2f}%)
  - 금리 적용일: {apply_date}
    (* 미국과의 시차 및 금리 업데이트 주기로 국내 기준 약 2영업일 차이 발생)

이상 내용 확인 후 처리 부탁 드립니다

감사합니다

변규남 드림"""

    GMAIL_USER = os.environ["GMAIL_USER"]
    GMAIL_PASS = os.environ["GMAIL_PASS"]
    TO_EMAIL   = os.environ["TO_EMAIL"]

    msg = MIMEMultipart()
    msg["From"]    = GMAIL_USER
    msg["To"]      = TO_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, TO_EMAIL, msg.as_string())
    print("✅ 발송 완료")
