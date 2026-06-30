"""
Read the hand-graded results.json and print the scoreboard.

The headline metric is NOT raw accuracy (Fugu orchestrates premium frontier
models, so it is expected to win on quality). The interesting number is
accuracy-per-dollar: is the orchestration worth its cost premium over a single
cheap model like DeepSeek?
"""

import json
from collections import defaultdict


def main():
    with open("results.json", encoding="utf-8") as f:
        rows = json.load(f)

    stats = defaultdict(lambda: {"graded": 0, "correct": 0, "cost": 0.0,
                                 "latency": 0.0, "runs": 0, "errors": 0})

    for r in rows:
        s = stats[r["provider"]]
        s["runs"] += 1
        if r.get("error"):
            s["errors"] += 1
            continue
        s["cost"] += r.get("cost_usd", 0.0)
        s["latency"] += r.get("latency_s", 0.0)
        if r.get("correct") is True:
            s["graded"] += 1
            s["correct"] += 1
        elif r.get("correct") is False:
            s["graded"] += 1

    ungraded = sum(1 for r in rows if r.get("correct") is None and not r.get("error"))
    if ungraded:
        print(f"WARNING: {ungraded} rows still have correct=null. Grade them for accurate numbers.\n")

    header = f"{'provider':<10} {'acc':>8} {'correct':>9} {'total$':>10} {'avg latency':>12} {'acc/$':>12}"
    print(header)
    print("-" * len(header))
    for prov, s in stats.items():
        acc = s["correct"] / s["graded"] if s["graded"] else 0.0
        ok_runs = s["runs"] - s["errors"]
        avg_lat = s["latency"] / ok_runs if ok_runs else 0.0
        acc_per_dollar = (acc / s["cost"]) if s["cost"] > 0 else float("inf")
        apd = "inf (cost=0)" if s["cost"] == 0 else f"{acc_per_dollar:,.1f}"
        print(f"{prov:<10} {acc:>7.0%} {s['correct']:>4}/{s['graded']:<4} "
              f"${s['cost']:>8.4f} {avg_lat:>10.2f}s {apd:>12}")
        if s["errors"]:
            print(f"           ({s['errors']} call(s) errored and were skipped)")

    print("\nReading: higher acc/$ = more correctness per dollar spent. If DeepSeek's")
    print("acc/$ beats Fugu's by a wide margin, the orchestration isn't paying off")
    print("at this task mix -- which is the whole question this experiment tests.")


if __name__ == "__main__":
    main()
