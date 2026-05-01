# Whisper MPS NaN Debug — 2026-05-01

## Issue
Whisper large model on MPS (Apple Silicon GPU) crashes mid-transcription (~6 min mark on 32 min file) with NaN/inf in attention logits.

```
ValueError: Expected parameter logits... found invalid values: tensor([..., nan, ..., -inf, ...], device='mps:0')
```

**CPU fallback works fine.** GPU + small files work. GPU + big files crash.

## Root Cause (per Gemma + testing)
Mixed precision scaling in MPS attention mechanism causes numerical instability. Long sequences (30+ min audio) compound the issue.

## Fixes Tested

### Fix 1: Force FP32 (not FP16) ✓ Partially works
```python
model.transcribe(..., fp16=False)
```
- Small files: ✓ Works on MPS with fp16=False
- Large files: **Testing now** (background task be0krfqip)

**Why FP16 fails on MPS:** PyTorch's FP16 on Apple Metal has precision loss in softmax/attention. FP32 is safer.

### Fix 2: Epsilon clipping in logits (not yet tested)
Add small epsilon to attention logits before softmax to prevent `-inf` masking overflow:
```python
logits = logits + 1e-8  # in attention layer
```
Requires patching Whisper's attention code.

### Fix 3: Use CPU instead of MPS
Proven stable, ~16 min on M4 CPU for 32 min audio. GPU advantage lost but reliability gained.

## Status
- CPU mode: ✓ Stable, shipping now
- GPU mode (FP32): Testing on large file (task be0krfqip)
- If FP32 works → update transcribe-watch.sh to use `--device mps --fp16 0`
- If FP32 fails → keep CPU as default, GPU as experimental opt-in

## Next Steps (pending test result)
1. If test passes: update watch script to use MPS with explicit FP32
2. If test fails: debug further (epsilon clipping, deterministic mode, PyTorch upgrade)
3. Document as "GPU + Whisper large unstable, use CPU or GPU small model"

