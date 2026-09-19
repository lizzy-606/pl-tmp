# TMP — Tokenizer Morphological Profile

**Author:** Elżbieta Dawidek · ORCID: [0009-0000-0433-6095](https://orcid.org/0009-0000-0433-6095)  
**Version:** 0.2.0 · July 2026  
**Licenses:** code — Apache-2.0 · data and documentation — CC BY 4.0

An open diagnostic tool for measuring how a tokenizer behaves at morpheme boundaries in an inflectional language. Polish is the validation material; the metrics are not specific to Polish.

Everything here is open: the data, the code, and the results. Nothing is gated. A held-out test set would make no sense for this task — a tokenizer is frozen and cannot learn from the items it is measured on.

[![Part I](https://img.shields.io/badge/Part%20I-submitted%20APR%202026-B31B1B.svg)](https://doi.org/10.31235/osf.io/7exa6_v3)
[![arXiv mirror](https://img.shields.io/badge/Part%20I-arXiv%20mirror%202026-B31B1B.svg)](https://arxiv.org/abs/2609.17553)
[![Part II](https://img.shields.io/badge/Part%20II-submitted%20MAY%202026-2F80ED.svg)](https://doi.org/10.31235/osf.io/tqvuf_v1)
[![Part III](https://img.shields.io/badge/Part%20III-submitted%20MAY%202026-6F42C1.svg)](https://doi.org/10.31235/osf.io/6sj8d_v4)
[![Part IV](https://img.shields.io/badge/Part%20IV-submitted%20JUN%202026-22863A.svg)](https://doi.org/10.31235/osf.io/a4wd9_v1)
![Part V](https://img.shields.io/badge/Part%20V-working%20paper%20JUL%202026-orange.svg)

---

## Why

The standard measure of tokenizer quality for morphologically rich languages is the **fertility ratio**: the mean number of tokens per word. It tells you *how much* a form is fragmented. It does not tell you *where* the cuts fall.

Two tokenizers can fragment a form into the same number of tokens and behave in completely different ways: one may keep the stem whole and separate the inflectional ending, the other may cut through the middle of the stem. To a model, these are not the same input. To the fertility ratio, they are indistinguishable.

TMP measures where the cuts fall.

## What it measures

Three metrics, read together as a profile:

**SI — Stem Integrity.** The percentage of forms in which no token boundary falls inside the stem.

**ISS — Inflectional Suffix Separation.** The percentage of forms with an overt ending in which a token boundary falls exactly at the stem/ending boundary.

**MFL — Mean Fragmentation per Lexeme.** The mean number of tokens per form, aggregated per lexeme.

SI, ISS, and MFL are not three independent quality scores. A high SI with a high MFL is not the same instrument behaviour as a high SI with a low MFL. A low ISS may mean that the tokenizer represents frequent inflected forms holistically — which is not a failure. The three are read as one profile.

## How boundaries are measured

For every form in the dataset, the surface stem is recorded together with its length in characters:
