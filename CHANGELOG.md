# Changelog

## 0.2.0 — 2026-07-12

### Corrected: SI (Stem Integrity) was not measuring stem integrity

The implementation of SI used to produce the results reported in Dawidek (2026b), *Inflectional Paradigms as a Diagnostic Tool for Tokenizers in Morphologically Rich Languages* (doi:10.31235/osf.io/tqvuf_v1), was incorrect. This entry states what went wrong, what follows from it, and what does not.

**The fault.** The check concatenated all tokens of a form back into a single string and then tested whether the root appeared as a substring of it. Concatenating the tokens of a form always reconstructs that form. The root was therefore always found, whatever the tokenizer had done. A form cut as `c|zy|t|am` scored the same as one left whole.

**What the metric was actually measuring.** Whether the root string occurs in the surface form. That is a property of the linguistic material, not of the tokenizer — which is why three of the four tokenizers returned an identical value of 84.5%. That figure could not have differed between them.

The remaining 15.5% were forms in which the root string does not appear on the surface at all: stem alternation and suppletion (`dzieci`, `ludzie`, `rozumiałam`). Again, a fact about Polish, not about any tokenizer.

**The outlier.** GPT-2 returned 68.0% rather than 84.5%. All sixteen forms responsible for the gap contain a Polish diacritic. GPT-2 encodes bytes, so `mówię` becomes `m|Ã³|wi|Ä|Ļ`; concatenation does not reconstruct the form, and the root is not found. The 68.0% was an artefact of byte-level encoding, not a morphological finding.

**What is unaffected.** MFL counts tokens and is unaffected. The central claims of the preprint rest on MFL: a Polish-trained tokenizer fragments Polish inflected forms far less than an English-trained one (1.22 vs 3.91), and tokenizer architecture carries independent explanatory power (XLM-R Unigram at 1.66 against mBERT WordPiece at 2.45, on comparable training data). Those results stand.

**What is affected.** All reported SI values. The ISS heuristic — last token equals the expected ending — was crude and has also been rewritten.

**The correction.** SI and ISS are now computed from character offsets against a hand-annotated stem/ending boundary for each of the 109 forms. Boundaries and the reasoning behind them are in `paradigms_pl.csv`; the measurement is described in the README.

The dataset now records, per form: the surface stem and its length, the lexeme-level root, the alternation type where one applies, and flags for suppletion and analytic forms. Alternation and suppletion are not scored against the tokenizer — they are performed by the language, not by the segmentation.

**Status.** Results are being recomputed. A corrected version of the preprint will follow.

---

## 0.1.0 — 2026

Initial analysis: four tokenizers (HerBERT BPE-PL, mBERT WordPiece, XLM-R Unigram, GPT-2 BPE-EN) over 109 Polish inflected forms across 10 lexemes. Published as Dawidek (2026b).
