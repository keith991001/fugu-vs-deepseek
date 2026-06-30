"""
Poor-man's head-to-head: Fugu vs DeepSeek.

Runs every task in tasks.json against both providers, records the answer,
token usage, cost, and latency, then writes results.json.

It does NOT auto-grade -- you open results.json afterwards and fill in the
"correct" field (true/false) for each row by hand. Then run summarize.py.

Both Fugu and DeepSeek expose an OpenAI-compatible API, so the SAME client
code talks to both -- we only swap base_url / api_key / model. That is the
whole trick: "OpenAI-compatible" means a tool written once works everywhere.
"""

import json
import os
import time

from openai import OpenAI

try:
    from dotenv import load_dotenv

    load_dotenv()  # reads a local .env file if present (never committed)
except ImportError:
    pass  # python-dotenv is optional; real env vars still work


# --- Pricing, in USD per 1,000,000 tokens. EDIT THESE to current rates. -------
# Look up the live numbers on each provider's pricing page before trusting cost.
# Fugu usually bills a single blended price (it hides the underlying workers),
# so put Fugu's published input/output price here.
PRICES = {
    "deepseek": {"in": 0.27, "out": 1.10},   # <-- verify on deepseek.com
    "fugu":     {"in": 0.00, "out": 0.00},    # <-- fill from sakana.ai pricing
}


def build_providers():
    """Two OpenAI clients that differ only in endpoint, key, and model name."""
    return {
        "deepseek": {
            "client": OpenAI(
                api_key=os.environ["DEEPSEEK_API_KEY"],
                base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            ),
            "model": os.environ.get("DEEPSEEK_MODEL", "deepseek-chat"),
        },
        "fugu": {
            "client": OpenAI(
                api_key=os.environ["FUGU_API_KEY"],
                # No default: you MUST set the real endpoint from Sakana's docs.
                base_url=os.environ["FUGU_BASE_URL"],
            ),
            "model": os.environ.get("FUGU_MODEL", "fugu"),  # or "fugu-ultra"
        },
    }


def cost_usd(provider, usage):
    p = PRICES[provider]
    return (usage.prompt_tokens * p["in"] + usage.completion_tokens * p["out"]) / 1_000_000


def main():
    with open("tasks.json", encoding="utf-8") as f:
        tasks = json.load(f)["tasks"]

    providers = build_providers()
    results = []

    for task in tasks:
        for name, p in providers.items():
            print(f"[{task['id']}] -> {name} ...", end="", flush=True)
            row = {
                "task": task["id"],
                "category": task["category"],
                "provider": name,
                "model": p["model"],
                "reference_answer": task["reference_answer"],
                "grading_hint": task["grading_hint"],
            }
            try:
                t0 = time.time()
                resp = p["client"].chat.completions.create(
                    model=p["model"],
                    messages=[{"role": "user", "content": task["prompt"]}],
                )
                row["latency_s"] = round(time.time() - t0, 2)
                row["output"] = resp.choices[0].message.content
                row["prompt_tokens"] = resp.usage.prompt_tokens
                row["completion_tokens"] = resp.usage.completion_tokens
                row["cost_usd"] = round(cost_usd(name, resp.usage), 6)
                row["error"] = None
                print(f" {row['latency_s']}s  ${row['cost_usd']}")
            except Exception as e:  # one bad call shouldn't kill the whole run
                row["error"] = str(e)
                row["output"] = None
                print(f" ERROR: {e}")
            row["correct"] = None  # <-- YOU fill this in by hand afterwards
            results.append(row)

    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("\nDone. Open results.json, read each 'output', and set 'correct' to")
    print("true or false for every row. Then run:  python summarize.py")


if __name__ == "__main__":
    main()
