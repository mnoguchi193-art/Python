"""
星座占いランキング / Daily horoscope ranking (stdlib only).

その日の日付をシード値にして 12 星座の順位を決めるので、
同じ日なら何度実行しても結果は変わりません (deterministic per day)。
"""

import random
from dataclasses import dataclass
from datetime import date

# 12 星座 (英名は参考用) / The twelve zodiac signs
SIGNS: list[tuple[str, str]] = [
    ("おひつじ座", "Aries"),
    ("おうし座", "Taurus"),
    ("ふたご座", "Gemini"),
    ("かに座", "Cancer"),
    ("しし座", "Leo"),
    ("おとめ座", "Virgo"),
    ("てんびん座", "Libra"),
    ("さそり座", "Scorpio"),
    ("いて座", "Sagittarius"),
    ("やぎ座", "Capricorn"),
    ("みずがめ座", "Aquarius"),
    ("うお座", "Pisces"),
]

LUCKY_COLORS = ["赤", "青", "黄", "緑", "白", "黒", "紫", "ピンク", "金", "銀"]
LUCKY_ITEMS = ["時計", "ハンカチ", "コーヒー", "本", "音楽", "花", "傘", "鍵", "写真", "観葉植物"]

# 順位ごとの一言 (1 位 → 12 位) / One-liner per rank
MESSAGES = [
    "絶好調！何をやってもうまくいく一日。",
    "好調をキープ。積極的に動いて吉。",
    "良い出会いやチャンスに恵まれそう。",
    "穏やかで安定した運気。丁寧さが鍵。",
    "小さな幸運が重なる予感。",
    "ほどほどに順調。無理は禁物。",
    "いつも通りの一日。基本を大切に。",
    "少し慎重に。確認を怠らないで。",
    "焦りは禁物。一呼吸おいて行動を。",
    "思わぬ落とし穴に注意。",
    "今日は守りの姿勢で過ごそう。",
    "充電日。ゆっくり休んで明日に備えて。",
]


@dataclass
class Fortune:
    rank: int
    sign_ja: str
    sign_en: str
    score: int
    color: str
    item: str
    message: str


def ranking(day: date | None = None) -> list[Fortune]:
    """指定日 (省略時は今日) の星座ランキングを返す。"""
    day = day or date.today()
    rng = random.Random(day.toordinal())

    # 各星座にスコアを割り当て、降順に並べて順位を決める
    scored = [(sign, rng.randint(1, 100)) for sign in SIGNS]
    scored.sort(key=lambda x: x[1], reverse=True)

    fortunes: list[Fortune] = []
    for rank, ((sign_ja, sign_en), score) in enumerate(scored, start=1):
        fortunes.append(
            Fortune(
                rank=rank,
                sign_ja=sign_ja,
                sign_en=sign_en,
                score=score,
                color=rng.choice(LUCKY_COLORS),
                item=rng.choice(LUCKY_ITEMS),
                message=MESSAGES[rank - 1],
            )
        )
    return fortunes


def format_ranking(fortunes: list[Fortune], day: date) -> str:
    lines = [f"★ {day:%Y年%m月%d日} の星座占いランキング ★", ""]
    for f in fortunes:
        lines.append(
            f"{f.rank:>2}位  {f.sign_ja:<6} (運勢 {f.score:>3})  "
            f"ラッキーカラー: {f.color} / ラッキーアイテム: {f.item}"
        )
        lines.append(f"      {f.message}")
    return "\n".join(lines)


if __name__ == "__main__":
    today = date.today()
    print(format_ranking(ranking(today), today))
