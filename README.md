# TMP — Tokenizer Morphological Profile

**Author:** Elżbieta Dawidek · ORCID 0009-0000-0433-6095
**Version:** 0.2.0 · July 2026
**Licenses:** code — Apache-2.0 · data and documentation — CC BY 4.0

An open diagnostic tool for measuring how a tokenizer behaves at morpheme boundaries in an inflectional language. Polish is the validation material; the metrics are not specific to Polish.

Everything here is open: the data, the code, and the results. Nothing is gated. A held-out test set would make no sense for this task — a tokenizer is frozen and cannot learn from the items it is measured on.

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

```
form           c z y t a ł a m
index         0 1 2 3 4 5 6 7 8
stem          |—————————|            stem = "czyta", stem_len = 5
```

A token boundary is a character index at which one token ends and the next begins.

- **SI** holds when no boundary falls strictly inside the stem — that is, nowhere in the open interval (0, 5).
- **ISS** holds when a boundary sits exactly at index 5.

Boundaries are read from character offsets supplied by the fast tokenizer, not from token strings. This matters: HerBERT appends `</w>`, mBERT prefixes `##`, XLM-R prefixes `▁`, and GPT-2 encodes bytes, so that `mówię` becomes `m|Ã³|wi|Ä|Ļ`. Any comparison based on token strings will silently corrupt on Polish diacritics. Character offsets refer to the original surface string and are comparable across all four.

## What is not penalised

Stem alternation (`pis-` → `pisz-`) and suppletion (`człowiek` → `ludzie`) are properties of the language, not of the tokenizer. The stem recorded for each form is the surface stem present in that form. A tokenizer is never penalised for an alternation it did not perform.

Alternation type and suppletion are recorded as separate columns, so that they can be analysed rather than silently absorbed into the score.

Alternation labels in the dataset are descriptive, not operational: they explain why a surface stem differs across a paradigm, but they enter no metric. SI and ISS are computed from the surface stem and its length. Polish alternation is a large and well-described system; a full typology is out of scope here, and would not change a single number in the results.

Analytic forms (`będę czytać`) are excluded from SI and ISS. They are two orthographic words, and their fragmentation reflects the auxiliary, not the segmentation of a single synthetic form.

## Data

`paradigms_pl.csv` — 10 Polish lexemes, 6 verbal and 4 nominal, in full inflectional paradigms.

- **121 paradigm cells / 109 unique surface forms.** The difference is syncretism: `mamy` fills three cells (GEN.SG, NOM.PL, ACC.PL), `dzieci` three, `domu` two. Metrics are computed over cells, so syncretic forms carry proportionally more weight. This is stated rather than corrected: a syncretic form genuinely occurs in more grammatical positions.
- **30 suppletive forms, 18 with stem alternation.** Both are flagged.
- The stem/ending boundary for every form was established by hand, on morphological analysis. This is the part that cannot be automated, and it is the part that makes the metrics mean anything.

## Results

Four tokenizers, 121 paradigm cells. Corrected implementation, July 2026.

| Tokenizer | Architecture | Training corpus | MFL | SI % | ISS % |
|---|---|---|---|---|---|
| HerBERT BPE-PL | BPE | Polish (mono) | 1.22 | 85.8 | 3.8 |
| XLM-R Unigram | Unigram LM | multilingual | 1.66 | 85.8 | 29.2 |
| mBERT WordPiece | WordPiece | multilingual | 2.45 | 43.3 | 37.7 |
| GPT-2 BPE-EN | BPE | English (mono) | 3.91 | 13.3 | 70.8 |

Reproduce with `python metrics.py`. Per-form output is in `results_forms.csv`.

**Fragmentation and stem destruction move together.** A tokenizer at MFL 1.22 or 1.66 keeps the stem intact in 85.8% of forms. At 2.45 that falls to 43.3%; at 3.91 to 13.3%. Above roughly two tokens per form, fragmentation stops being merely verbose and starts cutting through morphological boundaries. This was earlier proposed as a hypothesis on the basis of MFL alone; SI now supports it independently.

**The worst tokenizer has the best ISS.** GPT-2 separates the inflectional ending in 70.8% of forms — more often than any other — while destroying the stem in 86.7% of them. It hits the morpheme boundary because it cuts almost everywhere. ISS read on its own would rank it first. This is the clearest available demonstration that the three metrics are a profile and not a scoreboard.

## Two identical scores, two different tokenizers

HerBERT and XLM-R both score SI = 85.8%. Both cut the stem in exactly 17 of 121 cells.

They are not the same 17. The two sets overlap in three forms.

| | HerBERT (Polish, mono) | XLM-R (multilingual) |
|---|---|---|
| **cuts the stem in** | past tense 2nd/3rd person (`czytała`, `czytałaś`)<br>conditional (`czytałabym`, `pisałabym`)<br>plural noun endings (`mamom`, `mamami`, `domami`) | infinitives (`czytać`, `pisać`, `mówić`, `iść`)<br>present tense with alternation (`piszę`, `piszą`)<br>suppletive past stems (`szłam`, `szedł`) |

Two tokenizers with the same aggregate score and almost disjoint failure patterns.

This is the reason the per-form output matters. An aggregate percentage answers *how often* a tokenizer cuts the stem; it cannot answer *where*, and two tokenizers that behave nothing alike can land on the same number. A morphological profile therefore needs the per-form data, not three percentages.

Any downstream claim — that a tokenizer damages the conditional, or the infinitive, or suppletive paradigms — is invisible at the level of the score and visible in `results_forms.csv`.

## Correction

The SI implementation used for the results in the preprint below was incorrect: it reconstructed the form from its tokens and searched for the root as a substring, which always succeeds. See `CHANGELOG.md`. MFL is unaffected, and the central claims resting on it stand.

## Run it

```
pip install transformers
python metrics.py
```

Writes `results_forms.csv` (per form) and `results_profile.csv` (per tokenizer).

To profile your own tokenizer, add it to the `TOKENIZERS` dictionary in `metrics.py`. Any tokenizer with a fast implementation will work.

## Related preprint

Dawidek, E. (2026). *Inflectional Paradigms as a Diagnostic Tool for Tokenizers in Morphologically Rich Languages: A Proposal for a Linguistic Benchmark.* SocArXiv.
https://doi.org/10.31235/osf.io/tqvuf_v1

The preprint proposes the metrics. This repository implements them, supplies the data, and carries the correction.

## Relation to PL-GGE and PL-IPE

TMP measures the **tokenizer**: what a model receives as input. It requires no model and runs on frozen tokenizers.

PL-GGE and PL-IPE measure the **model**: what it produces. They are closed benchmarks, gated under a Data Use Agreement, because a model that has seen the test items stops being measured by them.

- PL-GGE: https://github.com/lizzy-606/pl-gge
- PL-IPE: https://github.com/lizzy-606/pl-ipe

Different object, different logic, different access model. TMP is open precisely because contamination is not a risk here.

## Contact

plgram.benchmarks@proton.me

---

*Licensing: code under Apache-2.0 (`LICENSE-CODE`); data and documentation under CC BY 4.0 (`LICENSE`).*
