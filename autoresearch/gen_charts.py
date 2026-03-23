#!/usr/bin/env python3
"""Generate all charts for README. Run from project root: python3 autoresearch/gen_charts.py"""

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

OUT_DIR = "docs/img"
DPI = 180

# ── Shared style ────────────────────────────────────────────
plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.25,
        "grid.linestyle": "--",
    }
)


def _save(fig, name):
    fig.tight_layout()
    fig.savefig(
        f"{OUT_DIR}/{name}.png",
        dpi=DPI,
        bbox_inches="tight",
        facecolor="white",
        edgecolor="none",
    )
    fig.savefig(
        f"{OUT_DIR}/{name}.svg",
        bbox_inches="tight",
        facecolor="white",
        edgecolor="none",
    )
    plt.close(fig)
    print(f"  ✓ {name}.png/svg")


# ════════════════════════════════════════════════════════════
# 1. OPTIMIZATION TIMELINE — key milestones
# ════════════════════════════════════════════════════════════
def fig_optimization_timeline():
    steps = [
        ("Baseline\norder=11, cubic", 3.220, "#5B8DEE"),
        ("Confidence\npenalty (n+3)", 3.212, "#5B8DEE"),
        ("ESC_PROB\n20K → 500", 3.211, "#5B8DEE"),
        ("SCRIPT_BOOST\n30 → 5", 3.210, "#F4A942"),
        ("CJK 3× weight\n+ conf n+8", 3.210, "#F4A942"),
        ("Passthrough\n(zero overhead)", 3.207, "#4CAF50"),
        ("Compact header\n3B → 2B", 2.980, "#4CAF50"),
        ("Confidence\nn+3 → n+1.5", 2.977, "#4CAF50"),
    ]

    labels = [s[0] for s in steps]
    bpcs = [s[1] for s in steps]
    colors = [s[2] for s in steps]

    fig, ax = plt.subplots(figsize=(14, 5.5))

    # Phase bands
    ax.axvspan(-0.5, 2.5, alpha=0.06, color="#5B8DEE")
    ax.axvspan(2.5, 4.5, alpha=0.06, color="#F4A942")
    ax.axvspan(4.5, 7.5, alpha=0.06, color="#4CAF50")

    ax.text(
        1.0,
        3.24,
        "Model tuning",
        ha="center",
        fontsize=9,
        color="#5B8DEE",
        fontweight="bold",
        alpha=0.8,
    )
    ax.text(
        3.5,
        3.24,
        "Multilingual",
        ha="center",
        fontsize=9,
        color="#F4A942",
        fontweight="bold",
        alpha=0.8,
    )
    ax.text(
        6.0,
        3.24,
        "Format optimization",
        ha="center",
        fontsize=9,
        color="#4CAF50",
        fontweight="bold",
        alpha=0.8,
    )

    ax.plot(range(len(bpcs)), bpcs, color="#333", lw=1.5, alpha=0.4, zorder=2)
    for i, (_, bpc, c) in enumerate(steps):
        ax.scatter(i, bpc, color=c, s=120, zorder=3, edgecolors="white", linewidth=1.5)

    for i, bpc in enumerate(bpcs):
        above = i != 6
        ax.annotate(
            f"{bpc:.3f}",
            (i, bpc),
            textcoords="offset points",
            xytext=(0, 8 if above else -12),
            ha="center",
            va="bottom" if above else "top",
            fontsize=9,
            fontweight="bold",
            color="#333",
        )

    # Arrow for biggest drop
    ax.annotate(
        "",
        xy=(6, 2.980),
        xytext=(5, 3.207),
        arrowprops=dict(
            arrowstyle="->", color="#4CAF50", lw=2.5, connectionstyle="arc3,rad=-0.2"
        ),
    )
    ax.text(
        5.8,
        3.10,
        "−7.1%",
        fontsize=11,
        fontweight="bold",
        color="#4CAF50",
        ha="center",
        rotation=-50,
    )

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("Bits per character (BPC)", fontsize=11)
    ax.set_title(
        "Compression optimization progress (lower = better)",
        fontsize=13,
        fontweight="bold",
        pad=15,
    )
    ax.set_ylim(2.90, 3.26)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(0.05))
    _save(fig, "optimization-progress")


# ════════════════════════════════════════════════════════════
# 2. BPC BEFORE / AFTER  by language
# ════════════════════════════════════════════════════════════
def fig_before_after_languages():
    langs = ["EN", "ES", "FR", "PT", "DE", "AR", "RU", "KO", "JA", "ZH"]
    bpc_before = [2.208, 1.600, 1.764, 1.774, 1.837, 1.841, 3.271, 3.454, 3.906, 4.759]
    bpc_after = [1.964, 1.600, 1.764, 1.774, 1.837, 1.841, 3.041, 2.859, 3.225, 3.950]

    idx = np.argsort(bpc_after)
    langs = [langs[i] for i in idx]
    bpc_before = [bpc_before[i] for i in idx]
    bpc_after = [bpc_after[i] for i in idx]

    x = np.arange(len(langs))
    w = 0.35
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.bar(
        x - w / 2,
        bpc_before,
        w,
        label="Before (3-byte header)",
        color="#EF9A9A",
        edgecolor="white",
        lw=0.8,
    )
    ax.bar(
        x + w / 2,
        bpc_after,
        w,
        label="After  (2-byte + passthrough)",
        color="#81C784",
        edgecolor="white",
        lw=0.8,
    )

    for i in range(len(langs)):
        d = bpc_after[i] - bpc_before[i]
        if abs(d) > 0.01:
            ax.text(
                x[i] + w / 2,
                bpc_after[i] + 0.06,
                f"{d / bpc_before[i] * 100:.0f}%",
                ha="center",
                va="bottom",
                fontsize=8,
                fontweight="bold",
                color="#2E7D32",
            )

    ax.set_xticks(x)
    ax.set_xticklabels(langs, fontsize=11, fontweight="bold")
    ax.set_ylabel("Bits per character (BPC)", fontsize=11)
    ax.set_title(
        "BPC by language: before vs after format optimization",
        fontsize=13,
        fontweight="bold",
    )
    ax.legend(fontsize=10, loc="upper left")
    ax.set_ylim(0, 5.5)
    _save(fig, "bpc-before-after")


# ════════════════════════════════════════════════════════════
# 3. SHORT MESSAGE FIX — before / after passthrough
# ════════════════════════════════════════════════════════════
def fig_short_message_fix():
    msgs = ["ok", "да", "hi", "Лол", "Мм?", "Ое", "Ккк", "Впн", "нет", "тест", "привет"]
    utf8 = [2, 4, 2, 6, 5, 4, 6, 6, 6, 8, 12]
    comp_old = [6, 6, 7, 7, 7, 7, 7, 8, 6, 5, 5]
    comp_new = [2, 4, 2, 6, 5, 4, 6, 6, 5, 5, 5]

    x = np.arange(len(msgs))
    w = 0.25
    fig, ax = plt.subplots(figsize=(12, 5))

    ax.bar(
        x - w, utf8, w, label="UTF-8 (raw)", color="#90CAF9", edgecolor="white", lw=0.8
    )
    ax.bar(
        x,
        comp_old,
        w,
        label="Before (3B header, no pass)",
        color="#EF9A9A",
        edgecolor="white",
        lw=0.8,
    )
    ax.bar(
        x + w,
        comp_new,
        w,
        label="After (2B header + pass)",
        color="#81C784",
        edgecolor="white",
        lw=0.8,
    )

    for i in range(len(msgs)):
        if comp_old[i] > utf8[i]:
            ax.text(
                x[i],
                comp_old[i] + 0.15,
                f"+{comp_old[i] - utf8[i]}B",
                ha="center",
                va="bottom",
                fontsize=7.5,
                color="#C62828",
                fontweight="bold",
            )

    ax.set_xticks(x)
    ax.set_xticklabels([f'"{m}"' for m in msgs], fontsize=9, rotation=30, ha="right")
    ax.set_ylabel("Output size (bytes)", fontsize=11)
    ax.set_title(
        "Short message compression: negative compression eliminated",
        fontsize=13,
        fontweight="bold",
    )
    ax.legend(fontsize=9.5, loc="upper right")
    ax.set_ylim(0, 10)
    _save(fig, "short-message-fix")


# ════════════════════════════════════════════════════════════
# 4. COMPRESSION BY LANGUAGE — horizontal bars (updated)
# ════════════════════════════════════════════════════════════
def fig_compression_by_language():
    langs = ["AR", "JA", "KO", "ES", "EN", "FR", "PT", "DE", "RU", "ZH"]
    ratios = [86.8, 83.2, 82.5, 81.1, 79.1, 79.3, 79.3, 78.4, 78.0, 78.5]

    idx = np.argsort(ratios)[::-1]
    langs = [langs[i] for i in idx]
    ratios = [ratios[i] for i in idx]

    colors = []
    for r in ratios:
        if r >= 82:
            colors.append("#4CAF50")
        elif r >= 79:
            colors.append("#66BB6A")
        else:
            colors.append("#81C784")

    fig, ax = plt.subplots(figsize=(10, 5.5))
    bars = ax.barh(
        range(len(langs)),
        ratios,
        color=colors,
        edgecolor="white",
        linewidth=0.8,
        height=0.65,
    )

    for i, (lang, r) in enumerate(zip(langs, ratios)):
        ax.text(
            r + 0.5,
            i,
            f"{r:.1f}%",
            va="center",
            fontsize=10,
            fontweight="bold",
            color="#333",
        )

    ax.set_yticks(range(len(langs)))
    ax.set_yticklabels(langs, fontsize=12, fontweight="bold")
    ax.set_xlabel("Compression ratio (%)", fontsize=11)
    ax.set_title(
        "Compression ratio by language (universal model, 10 languages)",
        fontsize=13,
        fontweight="bold",
    )
    ax.set_xlim(60, 95)
    ax.invert_yaxis()
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)
    _save(fig, "compression-by-language")


# ════════════════════════════════════════════════════════════
# 5. COMPRESSION BY LENGTH — bar chart (updated)
# ════════════════════════════════════════════════════════════
def fig_compression_by_length():
    buckets = ["1–10", "11–20", "21–50", "51–100", "101–200", "201+"]
    ratios = [26.7, 57.4, 73.7, 80.4, 81.8, 71.8]
    counts = [55, 214, 780, 617, 332, 2]

    fig, ax1 = plt.subplots(figsize=(10, 5.5))

    color_bars = "#5B8DEE"
    color_line = "#F4A942"

    bars = ax1.bar(
        range(len(buckets)),
        ratios,
        color=color_bars,
        edgecolor="white",
        linewidth=0.8,
        width=0.6,
        alpha=0.85,
        zorder=2,
    )
    ax1.set_xticks(range(len(buckets)))
    ax1.set_xticklabels(buckets, fontsize=10)
    ax1.set_xlabel("Message size, UTF-8 bytes", fontsize=11)
    ax1.set_ylabel("Compression ratio (%)", fontsize=11, color=color_bars)
    ax1.tick_params(axis="y", labelcolor=color_bars)
    ax1.set_ylim(0, 100)

    for i, r in enumerate(ratios):
        ax1.text(
            i,
            r + 1.5,
            f"{r:.0f}%",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
            color=color_bars,
        )

    ax2 = ax1.twinx()
    ax2.plot(
        range(len(buckets)),
        counts,
        color=color_line,
        marker="o",
        lw=2,
        markersize=7,
        zorder=3,
    )
    ax2.set_ylabel("Message count", fontsize=11, color=color_line)
    ax2.tick_params(axis="y", labelcolor=color_line)
    ax2.set_ylim(0, max(counts) * 1.3)
    ax2.spines["top"].set_visible(False)

    for i, c in enumerate(counts):
        ax2.text(
            i, c + 25, str(c), ha="center", va="bottom", fontsize=8, color=color_line
        )

    ax1.set_title(
        "Compression ratio vs message length (RU+EN test set, n=2000)",
        fontsize=13,
        fontweight="bold",
    )
    _save(fig, "compression-by-length")


# ════════════════════════════════════════════════════════════
# 6. COMPRESSION COMPARISON — n-gram+AC vs zlib vs Unishox2
# ════════════════════════════════════════════════════════════
def fig_compression_comparison():
    labels = [
        "Привет, как дела?",
        "Check channel 5",
        "Battery 40%, power save",
        "Проверка связи.\nКак слышно?",
        "Long EN (104 chars)",
        "Long RU (229 bytes)",
    ]
    utf8 = [30, 15, 39, 49, 104, 229]
    zlib = [41, 23, 47, 57, 96, 156]
    unishox = [20, 11, 26, 28, 65, 120]
    ngram = [6, 6, 11, 6, 52, 30]

    x = np.arange(len(labels))
    w = 0.20

    fig, ax = plt.subplots(figsize=(13, 6))
    ax.bar(
        x - 1.5 * w, utf8, w, label="UTF-8", color="#BDBDBD", edgecolor="white", lw=0.8
    )
    ax.bar(
        x - 0.5 * w, zlib, w, label="zlib", color="#EF9A9A", edgecolor="white", lw=0.8
    )
    ax.bar(
        x + 0.5 * w,
        unishox,
        w,
        label="Unishox2",
        color="#FFE082",
        edgecolor="white",
        lw=0.8,
    )
    ax.bar(
        x + 1.5 * w,
        ngram,
        w,
        label="n-gram + AC",
        color="#81C784",
        edgecolor="white",
        lw=0.8,
    )

    # % annotations on n-gram bars
    for i in range(len(labels)):
        pct = (1 - ngram[i] / utf8[i]) * 100
        ax.text(
            x[i] + 1.5 * w,
            ngram[i] + 1,
            f"−{pct:.0f}%",
            ha="center",
            va="bottom",
            fontsize=8,
            fontweight="bold",
            color="#2E7D32",
        )

    # Mark zlib expansion
    for i in range(len(labels)):
        if zlib[i] > utf8[i]:
            ax.text(
                x[i] - 0.5 * w,
                zlib[i] + 1,
                f"+{(zlib[i] / utf8[i] - 1) * 100:.0f}%",
                ha="center",
                va="bottom",
                fontsize=7,
                color="#C62828",
                fontweight="bold",
            )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8.5, ha="center")
    ax.set_ylabel("Compressed size (bytes)", fontsize=11)
    ax.set_title(
        "Compression comparison: n-gram+AC vs alternatives",
        fontsize=13,
        fontweight="bold",
    )
    ax.legend(fontsize=9.5, loc="upper left")
    ax.set_ylim(0, max(utf8) * 1.15)
    _save(fig, "compression-comparison")


# ════════════════════════════════════════════════════════════
# 7. CAPACITY — how many chars fit in 233 bytes
# ════════════════════════════════════════════════════════════
def fig_capacity():
    scripts = ["Latin (EN)", "Cyrillic (RU)", "CJK (ZH)", "Arabic (AR)", "Hangul (KO)"]
    # Uncompressed capacity (233 bytes ÷ bytes-per-char)
    raw = [233, 116, 77, 116, 77]
    # Compressed: 233 bytes × (1 / (1 - ratio))... but simpler:
    # avg chars/compressed_byte ~ 1/bpc*8
    # or: capacity ≈ 233 * 8 / bpc
    # EN: 233*8/1.68 ≈ 1110,  RU: 233*8/3.03 ≈ 615,  ZH: 233*8/3.94 ≈ 473
    # AR: 233*8/1.84 ≈ 1013,  KO: 233*8/2.86 ≈ 652
    comp = [1110, 615, 473, 1013, 652]

    x = np.arange(len(scripts))
    w = 0.35

    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.bar(
        x - w / 2,
        raw,
        w,
        label="Without compression",
        color="#EF9A9A",
        edgecolor="white",
        lw=0.8,
    )
    ax.bar(
        x + w / 2,
        comp,
        w,
        label="With compression",
        color="#81C784",
        edgecolor="white",
        lw=0.8,
    )

    for i in range(len(scripts)):
        mult = comp[i] / raw[i]
        ax.text(
            x[i] + w / 2,
            comp[i] + 15,
            f"×{mult:.1f}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
            color="#2E7D32",
        )
        ax.text(
            x[i] - w / 2,
            raw[i] + 15,
            str(raw[i]),
            ha="center",
            va="bottom",
            fontsize=9,
            color="#888",
        )
        ax.text(
            x[i] + w / 2,
            comp[i] - 40,
            str(comp[i]),
            ha="center",
            va="top",
            fontsize=9,
            color="white",
            fontweight="bold",
        )

    ax.set_xticks(x)
    ax.set_xticklabels(scripts, fontsize=10, fontweight="bold")
    ax.set_ylabel("Characters per 233-byte packet", fontsize=11)
    ax.set_title(
        "Meshtastic packet capacity: with vs without compression",
        fontsize=13,
        fontweight="bold",
    )
    ax.legend(fontsize=10, loc="upper right")
    ax.set_ylim(0, max(comp) * 1.15)
    _save(fig, "capacity")


if __name__ == "__main__":
    print("Generating all charts...")
    fig_optimization_timeline()
    fig_before_after_languages()
    fig_short_message_fix()
    fig_compression_by_language()
    fig_compression_by_length()
    fig_compression_comparison()
    fig_capacity()
    print("All done!")
