# AML Alert Triage - a working demo of deterministic-core, AI-at-the-edge

A financial-crime alert queue where **the decision is made by rules and the explanation is written by AI** - never the other way round.

- `scorer.py` - a fixed, auditable rules table turns alert features into a risk score and disposition (ESCALATE / REVIEW / MONITOR). No model runs here. Change scoring = change the table, under version control.
- `explain.py` - Claude takes an alert and its *already-computed* score and writes the analyst narrative: what fired, the likely typology, what to check next. It is told the disposition is final and cannot change it; the code enforces that and fails closed to a template.
- `gen.py` - build step: runs the scorer + explainer once and writes `public/data.json`.
- `public/` - the deployed artifact. A static page that reads `data.json`. **No live LLM call, no keyed endpoint, no free-text input in production** - so a public visitor can never burn an API key or inject a model. The AI-security baseline applied to the demo itself.

## Why this matters

AML alert queues are a comprehension problem as much as a detection one - analysts drown less in missed alerts than in alerts nobody can explain quickly. An explain-only LLM layer cuts triage time without touching model risk, because the number a regulator audits is still produced by deterministic rules.

## Build and run

```
pip install -r requirements.txt
ANTHROPIC_API_KEY=sk-... python3 gen.py        # generates public/data.json ONCE, with real narratives
python3 -m http.server -d public 8080          # or deploy public/ to any static host
```

Run `gen.py` with the key on your own machine at build time; the deployed site is just the static `public/` folder. Synthetic data only - no real customers, no PII.

Built by Ivan S - ran AML/KYC/KYT transaction monitoring inside a crypto exchange, now builds production AI agents. Live agent: paypilot.fly.dev
