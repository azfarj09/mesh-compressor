#!/usr/bin/env python3
"""
autoresearch/eval_short.py — Evaluation harness focused on short message compression.

Trains the model, evaluates compression, specifically tracking:
- neg_count: number of messages where compressed > UTF-8 (LOWER = better) — PRIMARY METRIC
- avg_bpc: overall bits per character (LOWER = better) — must not regress
- roundtrip_pct: must be 100% — GUARD

Usage:
    python3 -m autoresearch.eval_short 2>/dev/null | grep -E "^(neg_count|neg_wasted|avg_bpc|avg_ratio|roundtrip_pct):"
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from compress import train_model, compress, decompress


def main():
    data_dir = Path(__file__).parent.parent / "data"

    # Load train data
    train_lines = data_dir / "train.txt"
    lines = [
        l.strip() for l in train_lines.read_text("utf-8").splitlines() if l.strip()
    ]

    t0 = time.time()
    model = train_model(lines)
    train_sec = time.time() - t0

    # Load test data
    test_lines = data_dir / "test.txt"
    test_msgs = [
        l.strip() for l in test_lines.read_text("utf-8").splitlines() if l.strip()
    ]

    # Evaluate
    neg_count = 0
    neg_wasted = 0
    total_comp = 0
    total_utf8 = 0
    total_bits = 0
    total_chars = 0
    rt_ok = 0
    n = 0

    for msg in test_msgs:
        if not msg:
            continue
        n += 1
        utf8_len = len(msg.encode("utf-8"))
        try:
            comp = compress(msg, model)
            d = decompress(comp, model)
            comp_len = len(comp)

            total_comp += comp_len
            total_utf8 += utf8_len
            total_bits += comp_len * 8
            total_chars += len(msg)

            if d == msg:
                rt_ok += 1
            if comp_len > utf8_len:
                neg_count += 1
                neg_wasted += comp_len - utf8_len
        except Exception:
            total_comp += utf8_len * 2
            total_utf8 += utf8_len
            total_bits += utf8_len * 16
            total_chars += len(msg)

    avg_bpc = total_bits / total_chars if total_chars > 0 else 99
    avg_ratio = (1 - total_comp / total_utf8) * 100 if total_utf8 > 0 else 0
    rt_pct = rt_ok / n * 100 if n > 0 else 0

    print("---")
    print(f"neg_count:          {neg_count}")
    print(f"neg_wasted:         {neg_wasted}")
    print(f"avg_bpc:            {avg_bpc:.6f}")
    print(f"avg_ratio:          {avg_ratio:.2f}")
    print(f"roundtrip_pct:      {rt_pct:.2f}")
    print(f"n_test:             {n}")
    print(f"train_seconds:      {train_sec:.1f}")
    print(f"total_seconds:      {time.time() - t0:.1f}")


if __name__ == "__main__":
    main()
