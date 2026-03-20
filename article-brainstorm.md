# Article Brainstorm — AI Automation Portfolio Series

For: Devon — targeting AI automation roles
Assets: benchmark script (Python), benchmark report, Mac mini local AI stack, real project context

---

## The Play

A micro-article series. Each one stands alone but links to the others.
Together they tell the story of someone who *actually built something real* — not just talked about AI.
That's the differentiator right now. Everyone has a ChatGPT wrapper.
Almost nobody has benchmarked models on real data and shipped a production bot for a real team.

---

## The Articles

---

### 1. "I Ran 4 AI Models on Real Business Data. Here's What I Found."
**Type:** Experiment writeup | **Difficulty to write:** Easy | **Viral potential:** High

The experiment: same 5 tasks, 4 models, real small business data.
The twist: one model costs $0/month to run locally. One is Claude.
Key finding: local models are 2x faster on throughput. Claude wins on quality and reasoning.
Ends with: so when do you actually need the expensive cloud model?

**Why it works for job hunting:**
Shows benchmarking instincts, Python chops, ability to frame technical results
for a non-technical audience. Every AI automation employer wants someone who can
*evaluate* models, not just call an API.

**GitHub asset:** `llm-benchmark.py` — the public benchmark script (see below)
**Report asset:** speed table + 2 side-by-side output comparisons

---

### 2. "I Built a Daily Ops Bot for a Small Business on a $700 Mac Mini"
**Type:** Build story | **Difficulty to write:** Medium | **Viral potential:** High

What it does: scans 40 open tasks across 4 people every morning, generates a standup digest,
drafts messages, outputs structured JSON for automation.
Stack: Mac mini M4, Ollama, Python, Claude CLI, secrets vault.
The punchline: it runs 24/7 on hardware that fits in a backpack, costs nothing per query,
and the team lead doesn't have to read a wall of tasks every morning.

**Why it works for job hunting:**
The "I shipped something" piece. Not a tutorial. Not a toy.
A real system running for a real team. Shows systems thinking and end-to-end ownership.

**GitHub asset:** link to the benchmark script + README explaining the architecture

---

### 3. "The 50-Line Python Script That Runs a Team Standup Every Morning"
**Type:** Tutorial / walkthrough | **Difficulty to write:** Easy | **Viral potential:** Medium-high (bookmarked, shared)

Walk through the script in plain English first, then show the code.
Explain each piece. Show a real output.
Close with: "you could adapt this for your team in an afternoon."

**Why it works for job hunting:**
Tutorial content gets bookmarked and shared. Shows you can teach —
which means you can document, onboard, and communicate. All things employers want.

**GitHub asset:** the script itself IS the asset. Link directly.

---

### 4. "Why I Don't Trust AI Models I Can't Run Offline"
**Type:** Opinion / architecture | **Difficulty to write:** Medium | **Viral potential:** Medium (niche but sticky)

The trust tier framework: some models run native, some run Docker-isolated with no network.
Why model weights aren't neutral: training data, alignment, behavioral differences in agentic contexts.
Practical paranoia: what "air-gapped" AI looks like for a small business.
Not fear-mongering — just: here's how I think about it, here's what I do.

**Why it works for job hunting:**
Most AI automation candidates are tool-users. This piece shows security thinking
and architectural judgment. Hiring managers at serious companies will notice.

---

### 5. "Claude vs Llama vs Mistral: I Made Them All Do My Boss's Job"
**Type:** Spicy comparison | **Difficulty to write:** Easy | **Viral potential:** Very high

Same experiment as Article 1, different packaging.
Clickbait headline, real data, real outputs side by side.
Let the outputs speak — don't editorialize too much, let readers argue in the comments.

**Why it works for job hunting:**
Reddit (r/LocalLLaMA, r/MachineLearning) and HackerNews eat this up.
One good post there can drive hundreds of profile views.

**GitHub asset:** same benchmark script

---

### 6. "How I Set Up a Local AI Stack That Costs $0/Month to Run"
**Type:** Setup guide | **Difficulty to write:** Easy | **Viral potential:** High (evergreen, searchable)

Step by step: Ollama on Apple Silicon, localhost binding, model tiers, secrets management.
The gotchas nobody tells you: Docker doesn't get Metal GPU, so local beats container for Tier 1.
Who this is for: anyone who wants to stop paying per-token for internal tooling.

**Why it works for job hunting:**
Evergreen content. Searchable. People find this via Google months later.
Shows infrastructure thinking, not just prompt engineering.

---

### 7. "I Gave an AI a Real Estate Portfolio to Manage for a Day"
**Type:** Narrative / case study | **Difficulty to write:** Medium | **Viral potential:** High (crossover audience)

Tell the story from the business side, not the tech side.
40 open items across 4 people. One bot. One morning.
What it got right. What it got wrong. What it still can't do.
The human still makes the calls — the bot just makes sure nothing falls through the cracks.

**Why it works for job hunting:**
Crossover appeal: real estate people share it, tech people share it.
Shows you can communicate value to non-technical stakeholders — a huge skill gap in AI automation.

---

### 8. "Why Every Small Business Should Have a $700 AI Server"
**Type:** Opinion / think piece | **Difficulty to write:** Easy | **Viral potential:** Medium-high

The argument: a Mac mini M4 running Ollama beats a $50/month API subscription
for any business with recurring AI tasks.
The math: at what query volume does local win? (spoiler: not that high)
The hidden benefit: your data never leaves your building.

**Why it works for job hunting:**
Business-facing piece. Shows you understand ROI, not just tech.
Consultants and agencies will read this and think "I want to hire that person."

---

### 9. "I Used AI to Automate My Own Job Application Process" *(meta play)*
**Type:** Meta / personal story | **Difficulty to write:** Medium | **Viral potential:** Very high

The hook: I'm applying for AI automation jobs. So I built an AI automation pipeline to help me do it.
What it does: scans job descriptions, matches skills, drafts cover letters, tracks applications.
The punchline: the bot that got me the job interview was built to get me a job interview.

**Why it works for job hunting:**
This IS the job application. Share it the day you apply somewhere.
Recruiters and hiring managers will forward it to each other.
High risk, high reward — but if it lands, it really lands.

**GitHub asset:** a simple job-description parser script (new script, easy to write)

---

### 10. "What I Learned Benchmarking AI Models for 3 Months"
**Type:** Retrospective / lessons learned | **Difficulty to write:** Medium | **Viral potential:** Medium (good for LinkedIn)

The capstone piece. Write it after publishing 2-3 others.
Distill the actual lessons: what surprised you, what didn't, what you'd do differently.
The meta-lesson: the model matters less than the prompt and the data pipeline.

**Why it works for job hunting:**
Shows growth and reflection. Signals someone who learns from doing, not just reads about doing.
Good LinkedIn piece — thoughtful, not clickbait.

---

### 11. "Local AI vs Cloud AI: The Honest Comparison Nobody Is Writing"
**Type:** Analysis | **Difficulty to write:** Medium | **Viral potential:** High

Cut through the hype in both directions.
Cloud wins: quality, reasoning, multimodal, no setup.
Local wins: cost at scale, privacy, latency, offline capability.
Neither wins: it depends on the task. Here's the decision tree.

**GitHub asset:** the benchmark script as evidence

---

### 12. "How to Benchmark Any AI Model on YOUR Data in Under an Hour"
**Type:** How-to / actionable | **Difficulty to write:** Easy | **Viral potential:** High (very shareable)

Use the benchmark script as the tutorial.
Walk through: swap in your own tasks, point it at your Ollama instance, read the report.
Generic enough that anyone can use it. Specific enough to be actually useful.

**Why it works for job hunting:**
People clone the repo. They star it. Devon's GitHub profile gets real traffic.
This is how you get "200 stars" on your resume without grinding for years.

---

## Recommended Series Order

```
Week 1:  Article 1  — "I Ran 4 AI Models..."          (anchor piece, drives GitHub traffic)
Week 2:  Article 3  — "The 50-Line Script..."          (tutorial, gets bookmarks)
Week 3:  Article 5  — "Claude vs Llama vs Mistral..."  (spicy, gets Reddit/HN traction)
Week 4:  Article 2  — "I Built a Daily Ops Bot..."     (depth piece, for serious readers)
Later:   Article 9  — "I Used AI to Automate My Job Search" (publish when actively applying)
Later:   Article 10 — "What I Learned..."              (capstone, after others land)
```

---

## Platform Strategy

| Platform | Best articles | Why |
|----------|--------------|-----|
| LinkedIn | 1, 2, 7, 8, 10 | Hiring managers live here |
| Medium | 3, 4, 6, 11, 12 | Searchable, evergreen |
| Reddit (r/LocalLLaMA) | 5, 6, 12 | Technical audience, high engagement |
| HackerNews | 4, 11 | Niche but influential |
| Dev.to | 3, 6, 12 | Developer audience, good for GitHub traffic |

Cross-post everything. Link between articles. Link to GitHub on every one.

---

## What Devon Needs From Rod

- Permission to reference the project (frame it as: "I helped build this for a small business")
- The benchmark script (public version — see `llm-benchmark-public.py` in this repo)
- 2-3 output snippets from the benchmark report (paste directly — no sensitive data in the outputs)
- Optional: a quote from Rod ("my brother built this for my real estate team")

---

## The GitHub Profile Play

Devon needs public repos. Here's the ladder from easiest to most impressive:

```
Step 1 (this week):  llm-benchmark     ← the public benchmark script. Small. Clean. Useful.
Step 2 (next):       ai-standup-bot    ← sanitized version of the bot. Generic, no Dakota data.
Step 3 (later):      job-hunt-ai       ← the meta Article 9 project. High visibility.
```

Start with Step 1. Ship it. Link it in Article 1. That's the flywheel.
