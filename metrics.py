#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TMP — Tokenizer Morphological Profile

Computes three metrics that together form the morphological profile of a
tokenizer on Polish inflectional paradigms:

  SI  — Stem Integrity
        Percentage of forms in which no token boundary falls inside the stem.

  ISS — Inflectional Suffix Separation
        Percentage of forms with an overt ending in which a token boundary
        falls exactly at the stem/ending boundary.

  MFL — Mean Fragmentation per Lexeme
        Mean number of tokens per form, aggregated per lexeme.

The three are read together as a profile, not as three independent quality
scores. A high SI with a high MFL is not the same instrument behaviour as a
high SI with a low MFL.

--------------------------------------------------------------------------
HOW BOUNDARIES ARE MEASURED

Token strings differ across tokenizers: HerBERT appends '</w>', mBERT prefixes
'##', XLM-R prefixes '▁', GPT-2 encodes bytes ('ó' -> 'Ã³'). String matching on
token strings is therefore not reliable, and byte-level encoding will silently
corrupt any comparison involving Polish diacritics.

This implementation uses character offsets from the fast tokenizer
(return_offsets_mapping=True). Offsets refer to positions in the original
surface string, so they are comparable across all tokenizers regardless of
their internal marker conventions.

  form           c z y t a ł a m
  index         0 1 2 3 4 5 6 7 8
  stem          |‑‑‑‑‑‑‑‑‑|            stem = "czyta", stem_len = 5
  boundary at             ^            SI holds iff no boundary in (0, 5)
                                       ISS holds iff a boundary sits at 5

--------------------------------------------------------------------------
WHAT IS NOT PENALISED

Stem alternation (pis- -> pisz-) and suppletion (człowiek -> ludzie) are
properties of the language, not of the tokenizer. The stem recorded for each
form is the surface stem actually present in that form. A tokenizer is never
penalised for an alternation it did not perform. Alternation type and
suppletion are recorded as separate columns for analysis.

Analytic forms (będę czytać) are excluded from SI and ISS: they are two
orthographic words and their fragmentation reflects the auxiliary, not the
segmentation of a single synthetic form.

--------------------------------------------------------------------------
Data:  paradigms_pl.csv  (109 unique surface forms, 121 paradigm cells)
Usage: pip install transformers
       python metrics.py
"""

import csv
import sys
from collections import defaultdict

DATA = "paradigms_pl.csv"
OUT_FORMS = "results_forms.csv"
OUT_PROFILE = "results_profile.csv"

TOKENIZERS = {
    "HerBERT_BPE_PL":   "allegro/herbert-base-cased",
    "mBERT_WordPiece":  "bert-base-multilingual-cased",
    "XLM-R_Unigram":    "xlm-roberta-base",
    "GPT2_BPE_EN":      "gpt2",
}


# ── boundaries ────────────────────────────────────────────────────────────

def char_boundaries(tokenizer, form):
    """Return (n_tokens, set of internal character boundaries).

    A boundary is the character index at which one token ends and the next
    begins. Index 0 and len(form) are not boundaries — every tokenizer has
    those. Offsets come from the fast tokenizer, so they are comparable across
    marker conventions and byte-level encodings alike.
    """
    enc = tokenizer(form, add_special_tokens=False, return_offsets_mapping=True)
    offsets = [(a, b) for a, b in enc["offset_mapping"] if b > a]
    n = len(enc["input_ids"])
    bounds = {b for _, b in offsets[:-1]} if offsets else set()
    return n, bounds


def stem_intact(bounds, stem_len):
    """SI — no token boundary falls strictly inside the stem."""
    return not any(0 < b < stem_len for b in bounds)


def suffix_separated(bounds, stem_len):
    """ISS — a token boundary falls exactly at the stem/ending boundary."""
    return stem_len in bounds


# ── run ───────────────────────────────────────────────────────────────────

def load_tokenizers():
    from transformers import AutoTokenizer
    loaded = {}
    for name, model_id in TOKENIZERS.items():
        tok = AutoTokenizer.from_pretrained(model_id)
        if not tok.is_fast:
            print(f"  skipped {name}: no fast tokenizer, offsets unavailable")
            continue
        loaded[name] = tok
        print(f"  loaded  {name}")
    return loaded


def main():
    print("TMP — Tokenizer Morphological Profile\n")
    print("Loading tokenizers...")
    toks = load_tokenizers()
    if not toks:
        sys.exit("No fast tokenizers available.")

    with open(DATA, encoding="utf-8-sig") as f:
        items = list(csv.DictReader(f))
    print(f"\n{len(items)} paradigm cells, "
          f"{len({i['form'] for i in items})} unique surface forms\n")

    rows = []
    for it in items:
        form = it["form"]
        stem_len = int(it["stem_len"])
        analytic = it["analytic"] == "yes"
        zero_ending = it["segmentation"].endswith("∅")

        row = dict(it)
        for name, tok in toks.items():
            n, bounds = char_boundaries(tok, form)
            row[f"{name}__n"] = n
            if analytic:
                row[f"{name}__SI"] = ""
                row[f"{name}__ISS"] = ""
            else:
                row[f"{name}__SI"] = "1" if stem_intact(bounds, stem_len) else "0"
                row[f"{name}__ISS"] = "" if zero_ending else (
                    "1" if suffix_separated(bounds, stem_len) else "0")
        rows.append(row)

    with open(OUT_FORMS, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # profile
    prof = []
    for name in toks:
        ns = [r[f"{name}__n"] for r in rows]
        si = [r[f"{name}__SI"] for r in rows if r[f"{name}__SI"] != ""]
        iss = [r[f"{name}__ISS"] for r in rows if r[f"{name}__ISS"] != ""]
        prof.append({
            "tokenizer": name,
            "MFL": round(sum(ns) / len(ns), 2),
            "SI_pct": round(100 * si.count("1") / len(si), 1),
            "ISS_pct": round(100 * iss.count("1") / len(iss), 1),
            "n_forms_SI": len(si),
            "n_forms_ISS": len(iss),
        })

    with open(OUT_PROFILE, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(prof[0].keys()))
        w.writeheader()
        w.writerows(prof)

    print(f"{'tokenizer':<20}{'MFL':>7}{'SI %':>8}{'ISS %':>8}")
    print("-" * 43)
    for p in prof:
        print(f"{p['tokenizer']:<20}{p['MFL']:>7}{p['SI_pct']:>8}{p['ISS_pct']:>8}")
    print(f"\nwrote {OUT_FORMS}, {OUT_PROFILE}")


if __name__ == "__main__":
    main()
