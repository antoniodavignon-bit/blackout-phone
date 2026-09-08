# ADR-001 — Offline-first, not a thin client

**Status:** Accepted · 2026-09-07

## Context

The device could serve two very different roles.

A **thin client** would tunnel to the Ollama stack already running on a MacBook Air M4 — llama3.1:8b, qwen2.5-coder:7b — over Tailscale. Full-size model quality from a rugged pocket device, with the phone doing almost no work.

An **offline device** would run everything locally: a small model, a local reference library, local capture, no network dependency at all.

The hardware pushes toward the thin client. A Snapdragon 215 with ~1 GB usable RAM cannot run a model anyone would call good.

## Decision

Build the offline device.

## Rationale

A thin client is only as available as its network. The scenarios that justify carrying a second phone — a dead zone, a basement, a flight, a disaster, a jobsite with no coverage — are exactly the scenarios where a thin client is a paperweight. Optimizing for output quality optimizes for the case where the good phone already works.

The offline device is worse at everything except the one thing it exists for.

## Consequences

- Model quality is capped at what fits in ~1 GB of RAM. Accepted; see [ADR-002](ADR-002-model-ceiling.md).
- Every dependency must be resolvable offline: F-Droid APKs, local ZIM archives, on-device compilation.
- A Google account becomes a liability rather than a feature — nothing in the build needs Play Store, and an account on the device arms Factory Reset Protection.
- The MacBook stays in the architecture as a build host and library source, not as a runtime dependency.
