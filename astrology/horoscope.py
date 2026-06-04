"""
Zodiac horoscope ranking — for fun / 星座占いランキング(おたのしみ)

A light-hearted daily fortune generator. Given a date, it deterministically
ranks the 12 zodiac signs 1st–12th (the same date always yields the same
ranking, like a daily horoscope site) and assigns each a score, a lucky
colour, a lucky item and a short message.

This is entertainment only — not a prediction of anything. Standard library
only.
"""

import datetime
import random
from dataclasses import dataclass

# (Japanese name, English name, (start_month, start_day), (end_month, end_day))
ZODIAC = [
    ("牡羊座", "Aries", (3, 21), (4, 19)),
    ("牡牛座", "Taurus", (4, 20), (5, 20)),
    ("双子座", "Gemini", (5, 21), (6, 21)),
    ("蟹座", "Cancer", (6, 22), (7, 22)),
    ("獅子座", "Leo", (7, 23), (8, 22)),
    ("乙女座", "Virgo", (8, 23), (9, 22)),
    ("天秤座", "Libra", (9, 23), (10, 23)),
    ("蠍座", "Scorpio", (10, 24), (11, 22)),
    ("射手座", "Sagittarius", (11, 23), (12, 21)),
    ("山羊座", "Capricorn", (12, 22), (1, 19)),
    ("水瓶座", "Aquarius", (1, 20), (2, 18)),
    ("魚座", "Pisces", (2, 19), (3, 20)),
]

LUCKY_COLORS = ["赤", "青", "緑", "黄", "紫", "白", "黒", "金", "銀", "桃", "橙", "水色"]
LUCKY_ITEMS = [
    "コーヒー", "観葉植物", "手帳", "イヤホン", "お守り", "新しい靴",
    "チョコレート", "傘", "ハンカチ", "腕時計", "マグカップ", "万年筆",
]
MESSAGES = {
    "high": [
        "絶好調！思い切った行動が吉と出ます。",
        "幸運が舞い込む一日。笑顔を大切に。",
        "周囲からの評価が高まる予感。自信を持って。",
    ],
    "mid": [
        "穏やかな運気。マイペースが成功のカギ。",
        "小さな幸せに気づける一日になりそう。",
        "焦らず一歩ずつ進めば道は開けます。",
    ],
    "low": [
        "今日は無理せず充電の日に。",
        "慎重な行動が吉。早めの休息を。",
        "ペースダウンして自分を労わって。",
    ],
}


@dataclass
class Fortune:
    rank: int
    sign: str
    sign_en: str
    score: int
    lucky_color: str
    lucky_item: str
    message: str


def sign_for_date(month: int, day: int) -> str:
    """Return the Japanese zodiac-sign name for a birth month/day."""
    for jp, _en, (sm, sd), (em, ed) in ZODIAC:
        if sm <= em:  # range within a single calendar year
            if (month, day) >= (sm, sd) and (month, day) <= (em, ed):
                return jp
        else:  # Capricorn wraps across the new year
            if (month, day) >= (sm, sd) or (month, day) <= (em, ed):
                return jp
    raise ValueError(f"invalid date: {month}/{day}")


def daily_ranking(date: datetime.date | None = None) -> list[Fortune]:
    """Deterministic 1st–12th ranking of all signs for the given date."""
    date = date or datetime.date.today()
    rng = random.Random(date.toordinal())

    scored = []
    for jp, en, _s, _e in ZODIAC:
        score = rng.randint(20, 100)
        scored.append((score, jp, en))
    scored.sort(reverse=True)  # highest score = 1st place

    fortunes = []
    for rank, (score, jp, en) in enumerate(scored, start=1):
        tier = "high" if rank <= 4 else "mid" if rank <= 8 else "low"
        fortunes.append(Fortune(
            rank=rank,
            sign=jp,
            sign_en=en,
            score=score,
            lucky_color=rng.choice(LUCKY_COLORS),
            lucky_item=rng.choice(LUCKY_ITEMS),
            message=rng.choice(MESSAGES[tier]),
        ))
    return fortunes


def rank_of(sign: str, date: datetime.date | None = None) -> Fortune:
    """Look up a single sign's fortune for the date."""
    for fortune in daily_ranking(date):
        if sign in (fortune.sign, fortune.sign_en):
            return fortune
    raise ValueError(f"unknown sign: {sign!r}")


if __name__ == "__main__":
    today = datetime.date(2026, 6, 4)
    print(f"🔮 {today} の星座占いランキング\n")
    for f in daily_ranking(today):
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(f.rank, f"{f.rank:2d}位")
        print(f"{medal} {f.sign:　<5s} {f.score:3d}点  "
              f"ラッキーカラー:{f.lucky_color}  アイテム:{f.lucky_item}")
        print(f"      {f.message}")

    print("\n--- 個別ルックアップ / single lookup ---")
    me = rank_of(sign_for_date(6, 4), today)  # someone born June 4 -> 双子座
    print(f"6月4日生まれ({me.sign})は本日 {me.rank}位、{me.score}点！")
