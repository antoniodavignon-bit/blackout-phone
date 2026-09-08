# ADR-002 — Sub-1B model ceiling

**Status:** Accepted · 2026-09-07

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

## Open question

**Throughput is unmeasured.** No published tokens-per-second figure exists for llama.cpp on a Snapdragon 215, and none is assumed here. Phase 03 runs `llama-bench` and the real number is recorded in the engineering log. If it lands in low single digits the model is a batch tool, not a conversational one, and the field workflow is written accordingly.

## Consequences

- The model handles bounded, mechanical text work: tightening a sentence, generating variations, summarizing a paragraph.
- It is not a reference source. Factual lookup goes to the Kiwix library; navigation goes to offline maps.
- Compilation must respect the same ceiling — `-j 2` rather than `-j 4`, since parallel compile jobs each claim hundreds of MB.
