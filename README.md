# Fugu vs DeepSeek — a poor-man's head-to-head

A tiny, cheap experiment to get **first-hand intuition** about one question:

> Sakana **Fugu** orchestrates a pool of premium frontier models behind one API.
> **DeepSeek** is a single, very cheap model.
> Is the orchestration *worth its cost premium* over one good cheap model?

This is **not** a rigorous benchmark. It's 15 hand-checkable questions you run on
both providers, grade yourself, and compare. Small sample, you are the judge —
treat it as a vibe check, not a leaderboard.

## What it measures

For each task, on each provider, we record: the answer, token usage, **cost**,
and **latency**. The headline metric is **accuracy-per-dollar** — not raw
accuracy. Fugu is *expected* to win on quality (it calls Claude/GPT/Gemini under
the hood); the real question is whether the extra correctness justifies the
extra money and time versus a cheap single model.

## The tasks (`tasks.json`)

15 questions with a single verifiable answer each, in three categories that
loosely mirror the benchmarks Fugu reports:

| Category   | Count | Mirrors          | Note                                   |
|------------|-------|------------------|----------------------------------------|
| `algo`     | 5     | LiveCodeBench    | Final-answer algorithm problems        |
| `reasoning`| 5     | GPQA Diamond     | Math/physics/chem with one right answer |
| `debug`    | 5     | SWE-Bench Pro    | Find-and-fix a bug in a code snippet   |

⚠️ These are **easy proxies**, deliberately chosen so a non-expert can grade
them. They do **not** reproduce the real benchmarks' difficulty, so your scores
will be higher than the published numbers. What's meaningful is the **gap
between the two providers**, not the absolute scores.

## How to run

```bash
# 1. Install deps (a virtualenv is recommended)
pip install -r requirements.txt

# 2. Add your keys
cp .env.example .env
#    then edit .env: fill in DEEPSEEK_API_KEY, FUGU_API_KEY, and FUGU_BASE_URL
#    (get Fugu's endpoint + model name from Sakana's API docs)

# 3. Set current prices
#    open compare.py and edit the PRICES dict to each provider's live $/Mtoken

# 4. Run all tasks on both providers -> writes results.json
python compare.py

# 5. Grade: open results.json, read each "output", set "correct" to true/false

# 6. See the scoreboard
python summarize.py
```

## Cost

Tiny. 15 tasks × 2 providers = 30 calls. DeepSeek is pennies. Fugu depends on
whether you use `fugu` (cheap, routes to one model) or `fugu-ultra` (multi-step
orchestration, several model calls per task — more expensive). Start with `fugu`.

## Security

No keys live in this repo. Keys are read from environment variables (or a local
`.env`, which `.gitignore` excludes). If you fork this, **never** paste a real
key into any committed file — public-repo keys get scraped and abused within
minutes.

## Caveats (read before drawing conclusions)

- **Small sample** — 15 tasks is not statistically significant. A 9 vs 11 split
  means nothing; a blowout does.
- **You are the grader** — pick unambiguous answers and stay honest.
- **Bare API calls** — no fancy harness, retries, or scaffolding, so scores are
  lower than each vendor's official numbers. Compare providers to *each other*,
  not to published figures.
- **Prices change** — update the `PRICES` dict before trusting any cost number.
