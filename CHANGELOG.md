# Changelog

## 2026-03-23 — Format optimization: passthrough + compact header

**BPC: 3.210 → 2.977 (−7.3%). Negative compression eliminated (19 → 0 cases).**

15 autoresearch experiments, 4 kept, 11 discarded.

### What changed

#### 1. Zero-overhead passthrough for short messages

**Problem:** Messages like "ok" (2 UTF-8 bytes) were being output as 6 bytes — the 3-byte header + arithmetic coder overhead made short messages *bigger* than the original.

**Fix:** After arithmetic coding, compare the compressed output with the raw UTF-8 bytes. If compressed ≥ raw, return the raw UTF-8 directly with no header. The decompressor auto-detects the format by the first byte: compressed data always starts with `0x00` (the high byte of the text length field), while raw UTF-8 text never starts with a null byte.

**Impact:** 19 messages that previously had negative compression now have zero overhead. Output is guaranteed ≤ input for all messages.

#### 2. Compact 2-byte header (was 3 bytes)

**Problem:** Every compressed message paid a 3-byte header tax: `[uint16 text_len] [flags]`. For a typical 10-byte compressed message, 30% is just header.

**Fix:** For messages with text_len < 128 (99%+ of Meshtastic messages), pack everything into 2 bytes: `[0x00] [has_escapes_bit7 | text_len_7bits]`. Messages with text_len ≥ 128 keep the old 3-byte header, disambiguated by the high bit of byte[1].

**Impact:** **−7.1% BPC** — the single biggest improvement ever. Saves 1 byte per compressed message, which is huge for short radio packets.

#### 3. Confidence denominator n+3 → n+1.5 for Latin/Cyrillic

**Problem:** The confidence penalty `min(count / (n+3), 1)` was too conservative for well-represented scripts — it distrusted high-order contexts that had plenty of training data.

**Fix:** Reduce the denominator from `n+3` to `n+1.5` for Latin/Cyrillic scripts (CJK/Hangul/Japanese keep `n+8`). This trusts long-context predictions more when training data is abundant.

**Impact:** −0.003 BPC. Small but consistent improvement across all Latin/Cyrillic languages.

### Discarded experiments

| Experiment | Result | Why discarded |
|-----------|--------|---------------|
| Remove EOF encoding | BPC −0.018 | Roundtrip failures (99.95%) — EOF needed for AC finalization |
| ESC_PROB 500→200 | BPC +0.002 | Slight regression |
| Order weight exponent 3→4 | BPC +0.013 | Over-emphasizes long contexts |
| SCRIPT_BOOST 5→3 | BPC ±0 | No measurable effect |
| CDF_SCALE 2^20→2^22 | BPC −0.0001 | Negligible, not worth complexity |
| Epsilon cap CDF_SCALE/4 | BPC ±0 | Cap was never being hit |
| ORDER 11→13 | BPC +0.004 | Overfitting (not enough data for long contexts) |
| ORDER 11→9 | BPC +0.006 | Loses useful long-context predictions |
| PPM-style exclusion | BPC +1.55 | Catastrophic — zeroed out too many probabilities |
| Soft PPM exclusion (50%) | BPC +0.095 | Still too aggressive for this interpolation model |
| Passthrough threshold ≥ vs > | BPC ±0 | No messages had exactly equal sizes |

### Files changed

- `autoresearch/compress.py` — passthrough logic, compact header, confidence tuning
- `autoresearch/eval_short.py` — new evaluation harness for short message compression
- `autoresearch/gen_charts.py` — new chart generator (matplotlib) for all README charts
- `docs/img/*.png` — regenerated all charts with current data
- `README.md` — updated results, wire format docs, added "How compression works" section
- `CHANGELOG.md` — this file

### Metrics

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| avg_bpc (RU+EN) | 3.210 | 2.977 | **−7.3%** |
| avg_ratio | 76.87% | 78.55% | +1.68pp |
| neg_count | 19 | 0 | **−100%** |
| roundtrip | 100% | 100% | ✓ |
| fits_233 | 100% | 100% | ✓ |

Per-language BPC (multilingual universal model):

| Language | Before | After | Change |
|----------|--------|-------|--------|
| ZH | 4.759 | 3.950 | −17% |
| JA | 3.906 | 3.225 | −17% |
| KO | 3.454 | 2.859 | −17% |
| RU | 3.271 | 3.041 | −7% |
| EN | 2.208 | 1.964 | −11% |

---

## 2026-03-22 — Multilingual CJK optimization

25 autoresearch experiments. 9 kept, 15 discarded, 1 no-op.

- ESC_PROB 20000→500: more CDF budget for model predictions
- SCRIPT_BOOST 30→5: less epsilon bias toward same-script chars
- CJK 3× training weight: compensate for sparse template-generated CJK data
- CJK-specific confidence denominator (n+8): prevent overfitting rare high-order CJK contexts
- CJK weight threshold 0.3→0.05: boost mixed CJK messages too
- Two-tier CJK codepoint encoding: top-500 common chars get cheaper ESC codes

ZH BPC: 4.841 → 4.759 (−1.7%). All other languages improved or stable.

---

## 2026-03-21 — Model tuning (initial autoresearch)

17 experiments. Key findings:

- Order=11 with cubic `(n+1)^3` interpolation weights is optimal
- Confidence penalty `min(t/(n+3), 1)` prevents overfitting sparse contexts
- Quartic/quintic weights, PPM exclusion, dynamic model update all failed

BPC: 3.272 → 3.212 (−1.8%).

---

## 2026-03-20 — Multilingual universal model

- 10-language universal model (RU, EN, ES, DE, FR, PT, ZH, AR, JA, KO)
- 452,532 training messages, 1,494 unique characters
- Web UI with client-side JavaScript compression
- Only 1-3% worse than per-language models → ship one universal model
