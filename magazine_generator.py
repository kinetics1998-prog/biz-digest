#!/usr/bin/env python3
"""
📰 BIZ DIGEST — Magazine Generator (Bloomberg Style)
Утро: генерирует HTML-журнал + шлёт ссылку в Telegram
Вечер: шлёт 1-2 топ-новости текстом в Telegram
"""

import json, os, re, sys
from datetime import datetime
from pathlib import Path

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
DATA_DIR = Path(__file__).parent / "data"
MAGAZINE_DIR = Path(__file__).parent / "magazines"
GITHUB_PAGES_URL = os.environ.get("GITHUB_PAGES_URL", "")

RUBRICS = {
    "business":   {"name": "БІЗНЕС",      "color": "#c44536"},
    "money":      {"name": "ГРОШІ",       "color": "#1d9e75"},
    "tech":       {"name": "ТЕХНОЛОГІЇ",   "color": "#185fa5"},
    "psychology": {"name": "ПСИХОЛОГІЯ",   "color": "#7b4e8a"},
    "markets":    {"name": "РИНКИ",        "color": "#854f0b"},
    "lifehacks":  {"name": "ЛАЙФХАКИ",     "color": "#3b6d11"},
}

RUBRIC_KEYWORDS = {
    "money": ["грн","гривн","долар","євро","курс","банк","кредит","інвестиц","накопич","фінанс","оренд","ціни","подорож","бюджет","зарплат","пенсі"],
    "tech": ["google","ai","штучн","інтелект","gemini","claude","стартап","додаток","застосунок","кібер","wordpress","дрон","цифров","програм","software","tech"],
    "psychology": ["кадров","мотивац","команд","лідер","кар'єр","психолог","втом","стрес","баланс","вигоран","жінок","жінки","робоч"],
    "markets": ["ринок","ринки","аналітик","млрд","млн","зростан","експорт","імпорт","агросектор","прибут","виробництв","холдинг","індекс","інфляц"],
    "lifehacks": ["лайфхак","порад","як ","секрет","спосіб","корисн","продуктивн","ефективн","правил","помилк"],
    "business": ["компанія","бізнес","підприєм","бренд","маркет","продаж","клієнт","партнер","угод","засновник","CEO","ресторан","магазин"],
}

def detect_rubric(article):
    text = (article.get("title","") + " " + article.get("summary","")).lower()
    scores = {}
    for rubric, keywords in RUBRIC_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in text)
        if score > 0: scores[rubric] = score
    if scores: return max(scores, key=scores.get)
    cat = article.get("category","")
    if cat in ("UA_TECH","WORLD_TECH"): return "tech"
    if cat == "UA_ECON": return "markets"
    return "business"

def clean_html(text):
    text = re.sub(r'<[^>]+>', '', text)
    for old, new in [("&amp;","&"),("&#8217;","'"),("&#38;","&"),("&nbsp;"," ")]:
        text = text.replace(old, new)
    return text.replace("\n"," ").strip()

def select_articles(articles, count=7):
    for a in articles: a["_rubric"] = detect_rubric(a)
    seen, top = set(), []
    for target in ["business","money","tech","psychology","markets","lifehacks"]:
        for a in articles:
            if a["_rubric"] == target and target not in seen:
                top.append(a); seen.add(target); break
    for a in articles:
        if len(top) >= count: break
        if a not in top: top.append(a)
    return top[:count]

def render_card(article, index):
    r = RUBRICS.get(article.get("_rubric","business"), RUBRICS["business"])
    title = clean_html(article["title"])
    summary = clean_html(article.get("summary",""))[:220]
    if len(summary) >= 220: summary = summary[:summary.rfind(" ")] + "..."
    source = article["source"].replace("\U0001f1fa\U0001f1e6 ","").replace("\U0001f30d ","")
    link = article["link"]
    bg = "#faf8f5" if index % 2 == 1 else "#ffffff"
    return f'''<article style="background:{bg};border-left:3px solid {r['color']};padding:18px 18px 18px 22px;{'border-radius:10px 10px 0 0;margin-top:14px;' if index==1 else ''}{'border-radius:0 0 10px 10px;' if index==7 else ''}">
<div style="display:flex;align-items:baseline;gap:10px;margin-bottom:5px;">
<span style="font-size:10px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:{r['color']};">{r['name']}</span>
<span style="font-size:10px;color:#999;">{index:02d}</span></div>
<h2 style="font-family:'Playfair Display',Georgia,serif;font-size:17px;font-weight:700;line-height:1.32;color:#1a1a1a;margin-bottom:6px;">{title}</h2>
<p style="font-size:13px;line-height:1.65;color:#555;margin-bottom:10px;">{summary}</p>
<div style="display:flex;justify-content:space-between;align-items:center;padding-top:8px;border-top:1px solid rgba(0,0,0,0.05);">
<a href="{link}" style="font-size:12px;font-weight:700;color:{r['color']};text-decoration:none;" target="_blank">Читати →</a>
<span style="font-size:11px;color:#aaa;">{source}</span></div>
</article>'''

def generate_magazine(articles):
    now = datetime.now()
    date_str = now.strftime("%d.%m.%Y")
    days = ["Понеділок","Вівторок","Середа","Четвер","П'ятниця","Субота","Неділя"]
    edition = "Ранковий випуск" if now.hour < 14 else "Вечірній випуск"
    top = select_articles(articles, 7)
    rubric_set = set(a.get("_rubric","business") for a in top)
    pills = "".join(f'<span style="font-size:10px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;padding:5px 14px;color:#8899aa;border:0.5px solid #334;">{RUBRICS[r]["name"]}</span>' for r in ["business","money","tech","psychology","markets","lifehacks"] if r in rubric_set)
    cards = "".join(render_card(a, i) for i, a in enumerate(top, 1))

    return f'''<!DOCTYPE html>
<html lang="uk"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>BIZ DIGEST — {date_str}</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
<style>*{{box-sizing:border-box;margin:0;padding:0}}body{{background:#f0ece6;font-family:'DM Sans',system-ui,sans-serif;-webkit-font-smoothing:antialiased}}article+article{{border-top:0.5px solid rgba(0,0,0,0.06)}}@media(max-width:480px){{article{{padding:14px 14px 14px 18px!important}}h2{{font-size:15px!important}}}}</style></head>
<body>
<header style="background:#1b2838;color:#f5ebe0;padding:2.5rem 1.5rem;text-align:center;border-radius:0 0 16px 16px;">
<div style="font-size:10px;letter-spacing:0.3em;text-transform:uppercase;color:#5a6a7a;margin-bottom:14px;">Business digest for entrepreneurs</div>
<h1 style="font-family:'Playfair Display',serif;font-size:clamp(2.2rem,8vw,3.5rem);font-weight:900;line-height:1.05;">BIZ DIGEST</h1>
<p style="font-family:'Playfair Display',serif;font-size:14px;font-style:italic;color:#8899aa;margin-top:6px;">{edition}</p>
<p style="font-size:11px;color:#556;margin-top:14px;">{days[now.weekday()]}, {date_str} · {len(articles)} матеріалів</p>
<div style="display:flex;flex-wrap:wrap;justify-content:center;gap:0;margin-top:18px;">{pills}</div>
</header>
<main style="max-width:640px;margin:0 auto;padding:0 12px 2rem;">{cards}</main>
<footer style="text-align:center;padding:1.5rem 1rem 2.5rem;">
<div style="font-size:2.5rem;font-weight:900;color:#1b2838;">{len(articles)}</div>
<div style="font-family:'Playfair Display',serif;font-style:italic;color:#888;font-size:14px;margin-top:4px;">матеріалів зібрано сьогодні</div>
<div style="font-size:10px;color:#aaa;letter-spacing:0.15em;text-transform:uppercase;margin-top:16px;">BIZ DIGEST · {date_str}</div>
</footer></body></html>'''

def send_telegram(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID: return
    import urllib.request, urllib.parse
    data = urllib.parse.urlencode({"chat_id":TELEGRAM_CHAT_ID,"text":text,"parse_mode":"HTML","disable_web_page_preview":"true"}).encode()
    try:
        req = urllib.request.Request(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", data=data)
        with urllib.request.urlopen(req, timeout=10) as resp:
            r = json.loads(resp.read())
            if r.get("ok"): print("Telegram: OK")
    except Exception as e: print(f"Telegram: {e}")

def morning_mode(articles):
    """Утро: журнал + ссылка в Telegram"""
    html = generate_magazine(articles)
    MAGAZINE_DIR.mkdir(parents=True, exist_ok=True)
    filename = datetime.now().strftime("%Y-%m-%d") + ".html"
    (MAGAZINE_DIR / filename).write_text(html, encoding="utf-8")
    print(f"Magazine: {MAGAZINE_DIR / filename}")

    repo = os.environ.get("GITHUB_REPOSITORY","kinetics1998-prog/biz-digest")
    if GITHUB_PAGES_URL:
        url = f"{GITHUB_PAGES_URL}/magazines/{filename}"
    else:
        url = f"https://htmlpreview.github.io/?https://github.com/{repo}/blob/main/magazines/{filename}"

    text = (
        f"Доброго ранку.\n\n"
        f"<b>BIZ DIGEST</b> · {datetime.now().strftime('%d.%m.%Y')}\n\n"
        f"{len(articles)} матеріалів з {len(set(a['source'] for a in articles))} джерел\n\n"
        f"<a href=\"{url}\">Відкрити журнал →</a>"
    )
    send_telegram(text)

def evening_mode(articles):
    """Вечер: 2 топ-новости текстом"""
    for a in articles: a["_rubric"] = detect_rubric(a)
    # Берём 2 самые свежие бизнес-новости
    biz = [a for a in articles if a["_rubric"] in ("business","money","markets")]
    if len(biz) < 2: biz = articles
    top2 = biz[:2]

    lines = ["<b>BIZ DIGEST</b> · вечірнє\n"]
    for i, a in enumerate(top2, 1):
        title = clean_html(a["title"])
        summary = clean_html(a.get("summary",""))[:150]
        if len(summary) >= 150: summary = summary[:summary.rfind(" ")] + "..."
        r = RUBRICS.get(a.get("_rubric","business"), RUBRICS["business"])
        source = a["source"].replace("\U0001f1fa\U0001f1e6 ","").replace("\U0001f30d ","")
        lines.append(f"<b>{r['name']}</b>\n{title}\n<i>{summary}</i>\n<a href=\"{a['link']}\">Читати →</a> · {source}\n")

    send_telegram("\n".join(lines))

def main():
    data_files = sorted(DATA_DIR.glob("202*.json"), reverse=True)
    if not data_files: print("No data"); sys.exit(1)
    articles = json.loads(data_files[0].read_text(encoding="utf-8"))
    if not articles: print("Empty"); sys.exit(1)
    print(f"Articles: {len(articles)}")

    mode = "morning"
    if "--evening" in sys.argv: mode = "evening"
    elif "--morning" in sys.argv: mode = "morning"
    else: mode = "morning" if datetime.now().hour < 14 else "evening"

    if mode == "morning":
        morning_mode(articles)
    else:
        evening_mode(articles)

if __name__ == "__main__":
    main()
