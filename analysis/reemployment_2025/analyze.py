#!/usr/bin/env python3
"""国家公務員 再就職状況の公表（令和6年度分）データ分析スクリプト.

入力: 公表様式 (24-2) の Excel ファイル
出力:
  - records.csv     全レコード（日付シリアル値を ISO 日付へ変換）
  - report.md       集計レポート (Markdown)
  - charts/*.png    グラフ画像

使い方:
  python analyze.py <input.xlsx>
"""
from __future__ import annotations

import collections
import csv
import datetime
import sys
from pathlib import Path

import openpyxl

# --- 出身府省庁の推定に使うパターン（離職時の官職の文字列から判定） ---
# (キーワード, 正規化後の府省庁名) を「具体的→一般的」の順に並べる。
# 離職時の官職に最初に含まれたキーワードでその府省庁に分類する。
MINISTRY_PATTERNS = [
    # 内閣・内閣府系
    ("内閣官房", "内閣官房"), ("内閣法制局", "内閣法制局"),
    ("個人情報保護委員会", "個人情報保護委員会"),
    ("公正取引委員会", "公正取引委員会"),
    ("宮内庁", "宮内庁"), ("人事院", "人事院"),
    ("消費者庁", "消費者庁"), ("デジタル庁", "デジタル庁"),
    ("復興庁", "復興庁"), ("こども家庭庁", "こども家庭庁"),
    # 警察系
    ("警視総監", "警察庁"), ("警視庁", "警察庁"),
    ("警察大学校", "警察庁"), ("皇宮警察", "警察庁"), ("管区警察局", "警察庁"),
    ("警察庁", "警察庁"), ("警察情報通信", "警察庁"),
    # 金融庁系
    ("証券取引等監視委員会", "金融庁"), ("公認会計士・監査審査会", "金融庁"),
    ("金融庁", "金融庁"),
    # 総務省系
    ("管区行政評価局", "総務省"), ("行政評価", "総務省"),
    ("総合通信局", "総務省"), ("消防庁", "総務省"), ("総務", "総務省"),
    # 法務・検察系
    ("検事総長", "検察"), ("検事正", "検察"), ("検事長", "検察"),
    ("検事", "検察"), ("検察", "検察"), ("公安審査", "法務省"),
    ("公安調査", "法務省"), ("更生保護", "法務省"), ("刑務所", "法務省"),
    ("拘置所", "法務省"), ("少年院", "法務省"), ("矯正", "法務省"),
    ("入国管理", "法務省"), ("出入国在留", "法務省"), ("入国在留", "法務省"),
    ("保護観察所", "法務省"), ("少年鑑別所", "法務省"),
    ("地方法務局", "法務省"), ("法務局", "法務省"), ("法務", "法務省"),
    # 外務省系（在外公館を含む）
    ("総領事館", "外務省"), ("大使館", "外務省"), ("外務", "外務省"),
    # 財務省・国税系
    ("国税", "国税"), ("税関", "税関"), ("国立印刷局", "財務省"),
    ("造幣局", "財務省"), ("財務", "財務省"),
    # 文部科学系
    ("文化庁", "文化庁"), ("スポーツ庁", "スポーツ庁"),
    ("科学技術・学術政策研究所", "文部科学省"), ("文部科学", "文部科学省"),
    # 厚生労働系
    ("労働局", "厚生労働省"), ("労働基準", "厚生労働省"),
    ("公共職業安定", "厚生労働省"), ("厚生局", "厚生労働省"),
    ("検疫所", "厚生労働省"), ("国立医薬品", "厚生労働省"),
    ("国立保健医療", "厚生労働省"), ("国立感染症", "厚生労働省"),
    ("国立障害者", "厚生労働省"), ("国立療養所", "厚生労働省"),
    ("中央労働委員会", "厚生労働省"), ("厚生労働", "厚生労働省"),
    # 農林水産系
    ("林野庁", "林野庁"), ("森林管理局", "林野庁"), ("水産庁", "水産庁"),
    ("農政局", "農林水産省"), ("農林水産", "農林水産省"),
    # 経済産業系
    ("特許庁", "特許庁"), ("資源エネルギー", "経済産業省"),
    ("中小企業庁", "経済産業省"), ("産業保安監督部", "経済産業省"),
    ("製品評価技術基盤", "経済産業省"), ("経済産業", "経済産業省"),
    # 国土交通系
    ("国土地理院", "国土交通省"), ("国土技術政策総合研究所", "国土交通省"),
    ("運輸安全委員会", "国土交通省"), ("航空保安大学校", "国土交通省"),
    ("北海道開発局", "国土交通省"), ("地方整備局", "国土交通省"),
    ("運輸局", "国土交通省"), ("運輸支局", "国土交通省"),
    ("航空局", "国土交通省"), ("地方航空局", "国土交通省"),
    ("航空交通管制部", "国土交通省"),
    ("気象", "気象庁"), ("海上保安", "海上保安庁"), ("観光庁", "観光庁"),
    ("国土交通", "国土交通省"),
    # 環境・防衛・その他
    ("環境", "環境省"), ("原子力規制", "原子力規制委員会"),
    ("防衛装備庁", "防衛省"), ("自衛隊", "防衛省"),
    ("駐留軍等労働者", "防衛省"), ("防衛", "防衛省"),
    ("会計検査院", "会計検査院"), ("裁判所", "裁判所"),
    # 内閣府は他省庁の出先（○○府）と紛れるため末尾に置く
    ("内閣府", "内閣府"),
]

EXCEL_EPOCH = datetime.date(1899, 12, 30)  # Excel のシリアル値起点


def to_date(value):
    """Excel のシリアル値（数値）を date に変換。数値以外は None。"""
    if isinstance(value, (int, float)):
        return EXCEL_EPOCH + datetime.timedelta(days=int(value))
    return None


def guess_ministry(position: str | None) -> str:
    """離職時の官職文字列から出身府省庁を推定する。

    MINISTRY_PATTERNS を具体的→一般的の順に走査し、最初に一致した
    キーワードの正規化名を返す。一致しなければ "その他"。
    """
    if not position:
        return "不明"
    text = str(position)
    for keyword, name in MINISTRY_PATTERNS:
        if keyword in text:
            return name
    return "その他"


def load_records(xlsx_path: Path) -> list[dict]:
    """Excel から再就職レコードを読み込む。"""
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = wb.active
    records = []
    for row in range(1, ws.max_row + 1):
        no = ws.cell(row=row, column=1).value
        if not isinstance(no, (int, float)):
            continue  # ヘッダ・注記行などを除外
        cell = lambda c: ws.cell(row=row, column=c).value  # noqa: E731
        records.append(
            {
                "番号": int(no),
                "氏名": cell(2),
                "離職時の年齢": cell(3),
                "離職時の官職": cell(4),
                "出身府省庁（推定）": guess_ministry(cell(4)),
                "離職日": to_date(cell(10)),
                "再就職日": to_date(cell(11)),
                "再就職先の名称": cell(12),
                "再就職先の業務内容": cell(13),
                "再就職先における地位": cell(14),
                "求職の承認の有無": cell(15),
                "センター援助の有無": cell(16),
            }
        )
    return records


def write_csv(records: list[dict], out_path: Path) -> None:
    fields = list(records[0].keys())
    with out_path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for rec in records:
            row = dict(rec)
            for key in ("離職日", "再就職日"):
                row[key] = row[key].isoformat() if row[key] else ""
            writer.writerow(row)


def build_stats(records: list[dict]) -> dict:
    ages = [r["離職時の年齢"] for r in records if isinstance(r["離職時の年齢"], (int, float))]
    age_bins = collections.Counter()
    for a in ages:
        lo = int(a) // 5 * 5
        age_bins[f"{lo}-{lo + 4}"] += 1

    gaps = [
        (r["再就職日"] - r["離職日"]).days
        for r in records
        if r["離職日"] and r["再就職日"] and (r["再就職日"] - r["離職日"]).days >= 0
    ]
    gap_bins = collections.Counter()
    for g in gaps:
        if g <= 30:
            gap_bins["0-30日"] += 1
        elif g <= 90:
            gap_bins["31-90日"] += 1
        elif g <= 180:
            gap_bins["91-180日"] += 1
        elif g <= 365:
            gap_bins["181-365日"] += 1
        else:
            gap_bins["365日超"] += 1

    months = collections.Counter()
    for r in records:
        if r["再就職日"]:
            months[r["再就職日"].strftime("%Y-%m")] += 1

    return {
        "total": len(records),
        "people": len({r["氏名"] for r in records}),
        "ages": ages,
        "age_bins": age_bins,
        "ministry": collections.Counter(r["出身府省庁（推定）"] for r in records),
        "employer": collections.Counter(r["再就職先の名称"] for r in records if r["再就職先の名称"]),
        "title": collections.Counter(r["再就職先における地位"] for r in records if r["再就職先における地位"]),
        "approval": collections.Counter(r["求職の承認の有無"] for r in records),
        "center": collections.Counter(r["センター援助の有無"] for r in records),
        "months": months,
        "gaps": gaps,
        "gap_bins": gap_bins,
        "repeat": collections.Counter(r["氏名"] for r in records),
    }


def _table(rows, headers):
    lines = ["| " + " | ".join(headers) + " |",
             "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(c) for c in row) + " |")
    return "\n".join(lines)


def write_report(stats: dict, out_path: Path) -> None:
    ages = stats["ages"]
    gaps = stats["gaps"]
    gap_order = ["0-30日", "31-90日", "91-180日", "181-365日", "365日超"]
    parts = []
    parts.append("# 国家公務員 再就職状況の公表（令和6年度分）データ分析\n")
    parts.append(
        "対象期間: 令和6年4月1日〜令和7年3月31日 ／ 公表: 令和7年9月\n\n"
        "様式: 公表様式（24-2）国家公務員法第106条の24第2項等の規定に基づく届出関連\n"
    )
    parts.append("## 概要\n")
    parts.append(
        f"- 総レコード数: **{stats['total']:,}件**（1人が複数の再就職をしている場合は別行）\n"
        f"- 実人数（氏名ユニーク）: **{stats['people']:,}人**\n"
        f"- 求職の承認の有無: " + "、".join(f"{k} {v}" for k, v in stats["approval"].most_common()) + "\n"
        f"- 官民人材交流センターの援助の有無: " + "、".join(f"{k} {v}" for k, v in stats["center"].most_common()) + "\n"
    )

    parts.append("\n## 離職時の年齢\n")
    parts.append(
        f"平均 **{sum(ages) / len(ages):.1f}歳**（最小 {min(ages)} / 最大 {max(ages)}）\n\n"
    )
    parts.append(_table(
        [(k, stats["age_bins"][k]) for k in sorted(stats["age_bins"])],
        ["年齢層", "件数"],
    ))
    parts.append("\n\n![年齢分布](charts/age_distribution.png)\n")

    parts.append("\n## 出身府省庁（離職時の官職から推定）上位20\n")
    parts.append(_table(stats["ministry"].most_common(20), ["府省庁", "件数"]))
    parts.append("\n\n![出身府省庁](charts/ministry.png)\n")

    parts.append("\n## 再就職先の名称 上位20\n")
    parts.append(_table(stats["employer"].most_common(20), ["再就職先", "件数"]))

    parts.append("\n\n## 再就職先における地位 上位15\n")
    parts.append(_table(stats["title"].most_common(15), ["地位", "件数"]))

    parts.append("\n\n## 離職 → 再就職までの期間\n")
    parts.append(
        f"平均 **{sum(gaps) / len(gaps):.0f}日** ／ 中央値 **{sorted(gaps)[len(gaps) // 2]}日** "
        f"（最小 {min(gaps)} / 最大 {max(gaps)}）\n\n"
    )
    parts.append(_table(
        [(k, stats["gap_bins"].get(k, 0)) for k in gap_order],
        ["期間", "件数"],
    ))

    parts.append("\n\n## 再就職日（年月）分布\n")
    parts.append(_table(
        [(k, stats["months"][k]) for k in sorted(stats["months"])],
        ["年月", "件数"],
    ))
    parts.append("\n\n![再就職時期](charts/monthly.png)\n")

    parts.append("\n## 複数回再就職している人 上位10\n")
    parts.append(_table(
        [(name, cnt) for name, cnt in stats["repeat"].most_common(10)],
        ["氏名", "件数"],
    ))
    parts.append("\n\n---\n*本レポートは `analyze.py` により自動生成されました。*\n")

    out_path.write_text("\n".join(parts), encoding="utf-8")


def make_charts(stats: dict, out_dir: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager

    font_path = "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf"
    fp = font_manager.FontProperties(fname=font_path)
    matplotlib.rcParams["axes.unicode_minus"] = False
    out_dir.mkdir(parents=True, exist_ok=True)

    # 年齢分布
    keys = sorted(stats["age_bins"])
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(keys, [stats["age_bins"][k] for k in keys], color="#4C72B0")
    ax.set_title("離職時の年齢分布", fontproperties=fp)
    ax.set_xlabel("年齢層", fontproperties=fp)
    ax.set_ylabel("件数", fontproperties=fp)
    ax.set_xticks(range(len(keys)))
    ax.set_xticklabels(keys, fontproperties=fp, rotation=45)
    fig.tight_layout()
    fig.savefig(out_dir / "age_distribution.png", dpi=120)
    plt.close(fig)

    # 出身府省庁 上位15
    top = stats["ministry"].most_common(15)[::-1]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh([k for k, _ in top], [v for _, v in top], color="#55A868")
    ax.set_title("出身府省庁（推定）上位15", fontproperties=fp)
    ax.set_xlabel("件数", fontproperties=fp)
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels([k for k, _ in top], fontproperties=fp)
    fig.tight_layout()
    fig.savefig(out_dir / "ministry.png", dpi=120)
    plt.close(fig)

    # 再就職時期（対象年度のみ）
    months = {k: v for k, v in stats["months"].items() if k >= "2024-04"}
    keys = sorted(months)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(keys, [months[k] for k in keys], color="#C44E52")
    ax.set_title("再就職日（年月）分布", fontproperties=fp)
    ax.set_xlabel("年月", fontproperties=fp)
    ax.set_ylabel("件数", fontproperties=fp)
    ax.set_xticks(range(len(keys)))
    ax.set_xticklabels(keys, fontproperties=fp, rotation=45)
    fig.tight_layout()
    fig.savefig(out_dir / "monthly.png", dpi=120)
    plt.close(fig)


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    xlsx_path = Path(sys.argv[1])
    out_dir = Path(__file__).resolve().parent

    records = load_records(xlsx_path)
    write_csv(records, out_dir / "records.csv")
    stats = build_stats(records)
    make_charts(stats, out_dir / "charts")
    write_report(stats, out_dir / "report.md")
    print(f"レコード {stats['total']}件 / 実人数 {stats['people']}人 を処理しました。")
    print("出力: records.csv, report.md, charts/*.png")


if __name__ == "__main__":
    main()
