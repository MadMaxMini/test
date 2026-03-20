#!/usr/bin/env python3
"""
llm-benchmark.py
================
Benchmark local LLMs (via Ollama) and Claude side-by-side on your own tasks.

Runs the same prompts through every model and generates a readable markdown report
so you can compare quality and speed at a glance.

Requirements:
    - Ollama installed and running (https://ollama.com)
    - At least one model pulled: ollama pull llama3.2
    - Optional: Claude CLI installed for Claude comparison

Usage:
    python3 llm-benchmark.py
    python3 llm-benchmark.py --models llama3.2 mistral
    python3 llm-benchmark.py --skip-claude
    python3 llm-benchmark.py --tasks summarize classify

Author: Devon Clemente
GitHub: https://github.com/[devon-github]
"""

import argparse
import json
import subprocess
import time
import urllib.request
from datetime import datetime
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────

OLLAMA_URL = "http://127.0.0.1:11434"

# Models to benchmark. Any model you've pulled via `ollama pull` works here.
DEFAULT_MODELS = [
    "llama3.2",
    "mistral",
]

# ── Sample tasks ──────────────────────────────────────────────────────────────
# Swap these out for your own tasks. Each task needs:
#   description : one line explaining what this tests
#   prompt      : the actual prompt sent to every model
#   system      : (optional) system prompt / persona

SAMPLE_CONTEXT = """
Open items for the week:
- Follow up with client on proposal sent Tuesday
- Review Q1 budget draft before Thursday meeting
- Respond to 3 support tickets marked urgent
- Update project timeline — milestone 2 slipped by 4 days
- Schedule onboarding call for new team member starting Monday
"""

TASKS = {
    "summarize": {
        "description": "Summarize a list of open items into a short digest",
        "system": "You are a terse operations assistant. No filler. Facts only. Bullets or 2-3 sentences max.",
        "prompt": f"Write a 3-sentence summary of what needs attention this week.\n\n{SAMPLE_CONTEXT}",
    },
    "priorities": {
        "description": "Extract the top 3 urgent items",
        "system": "You are a terse operations assistant. No filler. Facts only.",
        "prompt": f"List the 3 most urgent items from the list below. One sentence each. Be specific.\n\n{SAMPLE_CONTEXT}",
    },
    "classify": {
        "description": "Classify items by type and urgency",
        "system": "You are a terse operations assistant. Return only the JSON requested, no explanation.",
        "prompt": (
            "Return ONLY valid JSON. Classify each item below as an object with keys: "
            "item (string), type (client/finance/ops/people), urgency (high/medium/low).\n\n"
            f"{SAMPLE_CONTEXT}"
        ),
    },
    "draft": {
        "description": "Draft a short message based on context",
        "system": "You are a terse operations assistant. Write in plain, direct language. No corporate filler.",
        "prompt": (
            "Draft a 2-3 sentence Slack message to the team flagging the most urgent issue "
            f"from this week's list. Direct and friendly tone.\n\n{SAMPLE_CONTEXT}"
        ),
    },
}


# ── Ollama runner ─────────────────────────────────────────────────────────────

def get_pulled_models():
    """Return set of model names currently pulled in Ollama."""
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=5) as r:
            data = json.loads(r.read())
            return {m["name"].split(":")[0] for m in data.get("models", [])}
    except Exception:
        return set()


def run_ollama(model, system, prompt):
    """Call Ollama API. Returns (output, stats)."""
    payload = json.dumps({
        "model": model,
        "prompt": f"{system}\n\n{prompt}" if system else prompt,
        "stream": False,
    }).encode()

    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
    )

    t_start = time.perf_counter()
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read())
    elapsed = round(time.perf_counter() - t_start, 2)

    output = data.get("response", "").strip()
    n_tokens = data.get("eval_count", len(output) // 4)
    gen_time = data.get("eval_duration", elapsed * 1e9) / 1e9

    stats = {
        "load_time_s": round(data.get("load_duration", 0) / 1e9, 2),
        "gen_time_s": round(gen_time, 2),
        "tokens": n_tokens,
        "tok_per_sec": round(n_tokens / gen_time, 1) if gen_time > 0 else 0,
    }
    return output, stats


# ── Claude CLI runner ─────────────────────────────────────────────────────────

def find_claude():
    """Find claude binary. Returns path string or None."""
    from glob import glob
    # VSCode extension binary
    matches = sorted(glob(str(Path.home() / ".vscode/extensions/anthropic.claude-code-*/resources/native-binary/claude")))
    if matches:
        return matches[-1]
    # System install
    result = subprocess.run(["which", "claude"], capture_output=True, text=True)
    return result.stdout.strip() or None


def run_claude(system, prompt):
    """Call Claude CLI. Returns (output, stats)."""
    binary = find_claude()
    if not binary:
        raise RuntimeError("claude binary not found — install Claude CLI or use --skip-claude")

    full_prompt = f"{system}\n\n{prompt}" if system else prompt
    t_start = time.perf_counter()
    result = subprocess.run([binary, "-p", full_prompt], capture_output=True, text=True, timeout=60)
    elapsed = round(time.perf_counter() - t_start, 2)

    if result.returncode != 0:
        raise RuntimeError(f"claude error: {result.stderr.strip()[:200]}")

    output = result.stdout.strip()
    n_tokens = len(output) // 4  # rough estimate
    stats = {
        "load_time_s": 0,
        "gen_time_s": elapsed,
        "tokens": n_tokens,
        "tok_per_sec": round(n_tokens / elapsed, 1) if elapsed > 0 else 0,
    }
    return output, stats


# ── Report ────────────────────────────────────────────────────────────────────

def write_report(results, tasks, out_path):
    run_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    model_names = list(results.keys())

    lines = [
        "# LLM Benchmark Report\n\n",
        f"**Run:** {run_time}  \n",
        f"**Models:** {', '.join(model_names)}  \n",
        f"**Tasks:** {', '.join(tasks.keys())}\n\n",
        "> Same prompts. Same data. Every model. Raw output below.\n\n",
        "---\n\n",
        "## Speed Summary\n\n",
        "> **Time** = seconds to respond. Slower = less usable in real-time contexts.  \n",
        "> **Tokens out** = a proxy for how much the model wrote. More isn't always better.\n\n",
        "| Model | Task | Time | Tokens/sec | Tokens out |\n",
        "|-------|------|-----:|-----------:|-----------:|\n",
    ]

    for model, task_results in results.items():
        for task_name, (output, stats) in task_results.items():
            lines.append(
                f"| {model} | {task_name} | {stats['gen_time_s']}s"
                f" | {stats['tok_per_sec']}"
                f" | {stats['tokens']} |\n"
            )

    lines.append("\n---\n\n## Outputs — Side by Side\n\n")
    lines.append("> Read down each section to compare the same answer from every model.\n\n")

    for task_name, task_info in tasks.items():
        lines.append(f"### {task_name} — {task_info['description']}\n\n")
        lines.append(f"**Prompt:** `{task_info['prompt'][:120].strip()}...`\n\n")
        for model, task_results in results.items():
            if task_name not in task_results:
                continue
            output, stats = task_results[task_name]
            lines.append(f"**{model}** — {stats['gen_time_s']}s — {stats['tokens']} tokens\n\n")
            lines.append(f"```\n{output}\n```\n\n")
        lines.append("---\n\n")

    Path(out_path).write_text("".join(lines))
    return out_path


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Benchmark local LLMs via Ollama, optionally against Claude.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 llm-benchmark.py
  python3 llm-benchmark.py --models llama3.2 mistral devstral
  python3 llm-benchmark.py --skip-claude --tasks summarize classify
  python3 llm-benchmark.py --output my-results.md
        """
    )
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS,
                        help="Ollama model names to benchmark (must be pulled first)")
    parser.add_argument("--tasks", nargs="+", default=list(TASKS.keys()),
                        help="Which tasks to run (default: all)")
    parser.add_argument("--skip-claude", action="store_true",
                        help="Skip Claude CLI, run local models only")
    parser.add_argument("--output", default=f"benchmark-{datetime.now().strftime('%Y-%m-%d')}.md",
                        help="Output report filename")
    args = parser.parse_args()

    task_subset = {k: TASKS[k] for k in args.tasks if k in TASKS}
    if not task_subset:
        print(f"No valid tasks. Available: {', '.join(TASKS.keys())}")
        return

    # Build model list
    pulled = get_pulled_models()
    model_ids = []

    if not args.skip_claude:
        if find_claude():
            model_ids.append("claude")
        else:
            print("claude binary not found — skipping (use --skip-claude to suppress this)")

    for m in args.models:
        if m.split(":")[0] in pulled:
            model_ids.append(m)
        else:
            print(f"'{m}' not pulled — run: ollama pull {m}")

    if not model_ids:
        print("No models available. Pull a model first: ollama pull llama3.2")
        return

    print(f"\n{'='*60}")
    print(f"LLM Benchmark — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Models : {model_ids}")
    print(f"Tasks  : {list(task_subset.keys())}")
    print(f"{'='*60}\n")

    results = {}
    for model_id in model_ids:
        print(f"\n── {model_id} ──")
        results[model_id] = {}
        for task_name, task_info in task_subset.items():
            print(f"  {task_name}... ", end="", flush=True)
            try:
                if model_id == "claude":
                    output, stats = run_claude(task_info.get("system", ""), task_info["prompt"])
                else:
                    output, stats = run_ollama(model_id, task_info.get("system", ""), task_info["prompt"])
                results[model_id][task_name] = (output, stats)
                print(f"{stats['gen_time_s']}s  {stats['tok_per_sec']} tok/s")
            except Exception as e:
                print(f"FAILED: {e}")
                results[model_id][task_name] = (f"ERROR: {e}", {
                    "load_time_s": 0, "gen_time_s": 0, "tokens": 0, "tok_per_sec": 0
                })

    report = write_report(results, task_subset, args.output)
    print(f"\n{'='*60}")
    print(f"Report: {report}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
