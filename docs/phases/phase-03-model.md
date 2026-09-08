# Phase 03 — On-device model

**Status:** ✅ Complete · 2026-09-08 — **0.6 tok/s generation**

Goal: llama.cpp compiled on the device, a sub-1B GGUF loaded, and a measured throughput number.

## Steps

### 1. Build under tmux

A long compile on four A53 cores dies with the SSH session if it drops. Don't let it.

```bash
pkg install -y tmux
tmux new -s build
```

Detach with **Ctrl-b** then **d**; reattach with `tmux attach -t build`.

### 2. Compile

```bash
cd ~ && git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
cmake -B build
cmake --build build --config Release -j 2 --target llama-cli llama-bench
```

> **`--target llama-cli llama-bench`, never `all`.** On 32-bit ARM the test
> suite fails to compile (`tests/test-opt.cpp` narrows `int64_t` to `size_t`),
> which kills a full build at 74%. Building only what you need sidesteps it
> entirely and finishes far sooner.

> **You will also hit a redefinition error at ~5%:** llama.cpp's 32-bit ARM
> fallback for `vcvtnq_s32_f32` collides with clang 21, which now provides it.
> Wrap llama.cpp's version in `#if 0` and let clang's win.

> **`-j 2`, not `-j 4`.** Each compile job can claim several hundred MB and there is roughly a gigabyte usable. Four parallel jobs risk the OOM killer taking the build near the end. Drop to `-j 1` if it still dies.

If the link step fails, confirm `libandroid-spawn` is installed.

### 3. Model onto the device

Download on the Mac — the phone's 2.4 GHz radio is not the tool for 491 MB.

```bash
# mac
cd ~/Downloads
curl -L -o qwen2.5-0.5b-instruct-q4_k_m.gguf \
  https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_k_m.gguf
scp -P 8022 qwen2.5-0.5b-instruct-q4_k_m.gguf u0_aXXX@localhost:~/models/
```

### 4. First run — small context

```bash
~/llama.cpp/build/bin/llama-cli \
  -m ~/models/qwen2.5-0.5b-instruct-q4_k_m.gguf \
  -c 1024 -t 4 -p "Rewrite this as one punchy sentence: "
```

Context size is the memory dial. Upstream docs suggest 4096 on typical phones; start at 1024 here and raise only if it holds.

### 5. Benchmark — and record the number

```bash
~/llama.cpp/build/bin/llama-bench \
  -m ~/models/qwen2.5-0.5b-instruct-q4_k_m.gguf -t 4
```

No published tokens-per-second figure exists for this chipset. The measured result goes in the engineering log and decides whether the model is a batch tool or a conversational one.

### 6. Wrap it

```bash
cat > $PREFIX/bin/ask <<'SCRIPT'
#!/data/data/com.termux/files/usr/bin/bash
~/llama.cpp/build/bin/llama-cli \
  -m ~/models/qwen2.5-0.5b-instruct-q4_k_m.gguf \
  -c 1024 -t 4 --no-display-prompt -p "$*"
SCRIPT
chmod +x $PREFIX/bin/ask
```

## What it's for

Bounded, mechanical text work with no network: tightening a sentence, generating variations, summarizing a paragraph, unsticking a blank page. Not facts, not long reasoning, not anything shipped unedited. Factual lookup belongs to Phase 04.
