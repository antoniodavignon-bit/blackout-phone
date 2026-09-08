# ADR-002 — Sub-1B model ceiling

**Status:** Accepted 2026-09-07 · **Throughput measured 2026-09-08**

## Context

2 GB of RAM on an Android 11 Go build leaves roughly one gigabyte usable after the OS. A GGUF model must fit in that alongside its context window, the llama.cpp runtime, and whatever else is resident.

## Decision

Target sub-1B quantized models. Start with **Qwen2.5-0.5B-Instruct Q4_K_M** (491 MB), context window starting at 1024.

| Candidate | Quant | Size | Verdict |
|---|---|---|---|
| Qwen2.5-0.5B-Instruct | Q4_K_M | 491 MB | Primary |
| Qwen2.5-0.5B-Instruct | Q8_0 | 676 MB | Better output, tighter fit — test second |
| Qwen2.5-Coder-0.5B | Q4_K_M | ~0.5 GB | Swap in for offline shell help |
| Anything ≥ 1.5B | any | — | Loads, then the OOM killer takes the terminal |

## Rationale

Sizes are from the official Qwen GGUF release. The 4 GB per-file limit imposed by FAT32 (see [ADR-004](ADR-004-fat32-library.md)) is not the binding constraint here — RAM is. The model lives on internal storage, not the card.

Context size is the second memory dial. The upstream llama.cpp Android docs suggest 4096 as a starting point on typical phones; on this device the starting point is 1024, raised only if it holds.

## Measured 2026-09-08

Qwen2.5-0.5B-Instruct Q4_K_M, `-c 1024 -t 4`, on-device:

```
> Say hello in five words.
Hello!
[ Prompt: 6.1 t/s | Generation: 0.6 t/s ]
```

**0.6 tokens/second generation. 6.1 t/s prompt processing.**

That is roughly **1.7 seconds per generated token**. A 30-token reply takes about
50 seconds; a 200-token reply takes over five minutes. Prompt processing is ten
times faster than generation, so reading input is cheap and producing output is
the wall.

This is below the low-single-digits the ADR anticipated, and it settles the
question decisively: **the on-device model is not a conversational tool.** It is
usable only where the output is genuinely tiny — a rewritten sentence, a
handful of words, a yes/no classification. Anything longer is faster to write by
hand.

The ADR's guidance stands, sharpened: the model is a last-resort utility for
when there is no network, not a feature anyone should plan a workflow around.

## Consequences

- The model handles bounded, mechanical text work: tightening a sentence, generating variations, summarizing a paragraph.
- It is not a reference source. Factual lookup goes to the Kiwix library; navigation goes to offline maps.
- Compilation must respect the same ceiling — `-j 2` rather than `-j 4`, since parallel compile jobs each claim hundreds of MB.
