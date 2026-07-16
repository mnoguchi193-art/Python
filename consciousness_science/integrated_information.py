"""
統合情報理論 / Integrated Information Theory (IIT): computing Φ

小さな2値ネットワークについて、統合情報量 Φ の簡略版を計算するデモ。
Φ = 「全体が生む情報」から「最小情報分割 (MIP) で切り離した部分の和」を
引いた残り = システムが部分の寄せ集めを超えて統合している情報量。
統合的な回路 (高 Φ)、フィードフォワード/分離した回路 (低 Φ) を比較する。

⚠ 教育目的の大幅な簡略版です。実際の IIT 3.0/4.0 の Φ とは異なります
   (有効情報ベースの直観的な近似)。
"""

from itertools import product

from info_theory import binary_entropy, entropy, log2

# ── システム: 2値ノードの決定論的更新則 / deterministic binary network ───
# node_funcs[i](state) は現在の状態タプルから次のノード i のビットを返す。
def whole_effective_info(node_funcs, n):
    """全体の有効情報 EI = 一様入力を与えたときの次状態分布のエントロピー。
    決定論的なので H(Y|X)=0、EI = H(Y)。"""
    counts = {}
    for state in product((0, 1), repeat=n):
        nxt = tuple(f(state) for f in node_funcs)
        counts[nxt] = counts.get(nxt, 0) + 1
    total = 2 ** n
    return entropy([c / total for c in counts.values()])

def node_prob_cut(f, state, part, n):
    """ノードの更新で、所属パート part 外の入力を一様ノイズに置換したときに
    次ビットが 1 になる確率 (=切断された結線)。"""
    outside = [i for i in range(n) if i not in part]
    if not outside:
        return float(f(state))
    ones = 0
    for bits in product((0, 1), repeat=len(outside)):
        s = list(state)
        for idx, b in zip(outside, bits):
            s[idx] = b
        ones += f(tuple(s))
    return ones / (2 ** len(outside))

def partitioned_effective_info(node_funcs, n, partition):
    """分割 partition (ノード集合のリスト) で結線を切ったときの EI = I(X;Y)。
    各ノードは所属パート内の入力のみ見て、外部入力はノイズ化する。"""
    node_part = {}
    for part in partition:
        for i in part:
            node_part[i] = part
    hy_given_x = 0.0
    marginal = {}
    total = 2 ** n
    for state in product((0, 1), repeat=n):
        probs = [node_prob_cut(node_funcs[i], state, node_part[i], n) for i in range(n)]
        hy_given_x += sum(binary_entropy(p) for p in probs) / total
        # この入力からの次状態分布を周辺分布に足し込む
        for nxt in product((0, 1), repeat=n):
            p = 1.0
            for i in range(n):
                p *= probs[i] if nxt[i] else (1 - probs[i])
            marginal[nxt] = marginal.get(nxt, 0.0) + p / total
    hy = entropy(list(marginal.values()))
    return hy - hy_given_x  # I(X;Y) = H(Y) - H(Y|X)

def bipartitions(n):
    """ノード {0..n-1} の非自明な二分割をすべて生成"""
    nodes = list(range(n))
    seen = []
    for r in range(1, n):
        for combo in _combos(nodes, r):
            part_a = set(combo)
            part_b = set(nodes) - part_a
            key = frozenset([frozenset(part_a), frozenset(part_b)])
            if key not in seen:
                seen.append(key)
                yield [sorted(part_a), sorted(part_b)]

def _combos(items, r):
    if r == 0:
        yield []
        return
    for i in range(len(items)):
        for rest in _combos(items[i + 1:], r - 1):
            yield [items[i]] + rest

def phi(node_funcs, n):
    """最小情報分割 (MIP) を探し、そこでの統合情報量 Φ を返す。
    MIP は『部分の情報容量で正規化した情報損失』が最小の分割。"""
    ei_whole = whole_effective_info(node_funcs, n)
    best_phi, best_part = None, None
    for part in bipartitions(n):
        ei_part = partitioned_effective_info(node_funcs, n, part)
        loss = ei_whole - ei_part
        norm = min(len(p) for p in part)          # 部分の最大情報量 (bits) で正規化
        normalized = loss / norm
        if best_phi is None or normalized < best_normalized:
            best_phi, best_part, best_normalized = loss, part, normalized
    return max(best_phi, 0.0), best_part, ei_whole

# ── 比較する回路 / example circuits ──────────────────────────────────────
CIRCUITS = {
    "fully integrated (XOR parity)": (3, [
        lambda s: s[1] ^ s[2],      # 各ノードが他2つの XOR — 全結合で強く相互依存
        lambda s: s[0] ^ s[2],
        lambda s: s[0] ^ s[1],
    ]),
    "partially integrated (AND ring)": (3, [
        lambda s: s[1] & s[2],      # 各ノードが他2つの AND — 相互依存だが情報損失あり
        lambda s: s[0] & s[2],
        lambda s: s[0] & s[1],
    ]),
    "weakly integrated (pair + relay)": (3, [
        lambda s: s[0] ^ s[1],      # {0,1} は相互作用、2 は 0 の一方向コピー
        lambda s: s[0] ^ s[1],
        lambda s: s[0],
    ]),
    "feedforward chain": (3, [
        lambda s: s[0],             # A は自分のコピー
        lambda s: s[0],             # B ← A
        lambda s: s[1],             # C ← B (一方向のみ)
    ]),
    "two independent parts": (3, [
        lambda s: s[0] ^ s[1],      # {0,1} が相互作用
        lambda s: s[0] ^ s[1],
        lambda s: s[2],             # 2 は孤立
    ]),
}

print("integrated information Φ for small circuits (higher Φ = more integrated):")
print(f"  {'circuit':<32} {'Φ (bits)':>9} {'whole EI':>9}  MIP")
for name, (n, funcs) in CIRCUITS.items():
    p, mip, ei = phi(funcs, n)
    mip_str = " | ".join("".join(str(i) for i in part) for part in mip)
    bar = "#" * int(p * 8)
    print(f"  {name:<32} {p:>9.3f} {ei:>9.3f}  {{{mip_str}}} {bar}")

print("""
→ 全結合の XOR は Φ=2 — どの結線を切っても最大の情報が失われる (真に統合)
→ AND リングは Φ≈1.4 — 相互依存はあるが、切断コストはやや小さい (部分統合)
→ 一方向のフィードフォワード連鎖や孤立部分を持つ系は Φ=0 — 最小分割が『無コスト』
→ IIT の主張: 意識の量は統合情報量 Φ に対応する。統合された情報こそ経験の実体だとする
→ (注: 実際の IIT 3.0/4.0 はより精緻。ここでは有効情報に基づく直観的な近似を示した)""")
