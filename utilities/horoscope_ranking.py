"""
星座占いランキング / Zodiac fortune ranking (stdlib only, no external dependencies)

その日の日付をシードに使うため、同じ日付なら結果は常に同じになります。
Uses the date as a random seed, so the same date always yields the same ranking.
"""

import random
from dataclasses import dataclass
from datetime import date

# 12星座 (名前, 期間) / The 12 zodiac signs (name, date range)
ZODIAC_SIGNS = [
    "おひつじ座", "おうし座", "ふたご座", "かに座",
    "しし座", "おとめ座", "てんびん座", "さそり座",
    "いて座", "やぎ座", "みずがめ座", "うお座",
]

LUCKY_COLORS = [
    "赤", "青", "黄", "緑", "紫", "白", "黒", "金", "銀", "桃", "橙", "水色",
]

LUCKY_ITEMS = [
    "ハンカチ", "腕時計", "観葉植物", "コーヒー", "イヤホン", "手帳",
    "キャンドル", "傘", "写真", "クッション", "本", "お守り",
]

MESSAGES = [
    "新しい挑戦が実を結ぶ一日。直感を信じて動きましょう。",
    "人とのつながりが幸運を運びます。笑顔を忘れずに。",
    "少し立ち止まって休息を。無理は禁物の日です。",
    "努力が認められるとき。自信を持って前へ。",
    "思いがけない嬉しい知らせがありそう。",
    "丁寧な行動が信頼を生みます。基本に忠実に。",
    "金運good。ただし衝動買いには注意を。",
    "創造力が冴える日。アイデアをメモしておきましょう。",
    "周囲への感謝を伝えると運気上昇。",
    "ペースを守れば物事がスムーズに進みます。",
    "学びのチャンス到来。気になることに飛び込んで。",
    "心穏やかに過ごせる一日。好きな音楽を聴いて。",
]


@dataclass
class Fortune:
    rank: int
    sign: str
    score: int  # 1〜100
    lucky_color: str
    lucky_item: str
    message: str


def daily_ranking(target: date | None = None) -> list[Fortune]:
    """指定日の星座占いランキングを返す / Return the zodiac ranking for the given date."""
    target = target or date.today()
    rng = random.Random(target.toordinal())

    # 各星座にスコアを割り当て、降順に並べてランキング化する
    scored = sorted(
        (
            (sign, rng.randint(1, 100))
            for sign in ZODIAC_SIGNS
        ),
        key=lambda pair: pair[1],
        reverse=True,
    )

    ranking: list[Fortune] = []
    for rank, (sign, score) in enumerate(scored, start=1):
        ranking.append(
            Fortune(
                rank=rank,
                sign=sign,
                score=score,
                lucky_color=rng.choice(LUCKY_COLORS),
                lucky_item=rng.choice(LUCKY_ITEMS),
                message=rng.choice(MESSAGES),
            )
        )
    return ranking


def format_ranking(ranking: list[Fortune], target: date | None = None) -> str:
    """ランキングを表示用の文字列に整形する / Format the ranking for display."""
    target = target or date.today()
    lines = [f"★ {target:%Y年%m月%d日} の星座占いランキング ★", ""]
    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    for f in ranking:
        marker = medals.get(f.rank, f"{f.rank:>2d}位")
        lines.append(f"{marker} {f.sign}（{f.score}点）")
        lines.append(f"     ラッキーカラー: {f.lucky_color} / ラッキーアイテム: {f.lucky_item}")
        lines.append(f"     {f.message}")
    return "\n".join(lines)


if __name__ == "__main__":
    today = date.today()
    print(format_ranking(daily_ranking(today), today))
