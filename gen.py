"""Build step: pre-generate the demo's static content, run once with a key locally.

Scores every alert deterministically and generates its narrative ONCE, then writes
public/data.json. The deployed site serves that static file - there is no live LLM
call and no keyed endpoint in production, so a public visitor can never burn the key
or feed free text to a model. This is the AI-security baseline applied to the demo
itself: even the demo has no ungated LLM call.

Run:  ANTHROPIC_API_KEY=sk-... python3 gen.py
Without a key it writes template narratives and prints a warning so you know to
re-run with the key before deploying (interviewers should see the real AI narrative).
"""
from __future__ import annotations
import os, json
from pathlib import Path
from scorer import score_alert
from explain import explain

ROOT = Path(__file__).parent
ALERTS = json.loads((ROOT / "alerts.json").read_text())


def build() -> dict:
    out = []
    for a in ALERTS:
        r = score_alert(a)
        out.append({
            "id": a["id"], "customer": a["customer"],
            "customer_profile": a["customer_profile"], "period": a["period"],
            "score": r.score, "disposition": r.disposition,
            "factors": r.factors, "explanation": explain(a, r),
        })
    out.sort(key=lambda x: x["score"], reverse=True)
    return {"alerts": out}


if __name__ == "__main__":
    data = build()
    (ROOT / "public").mkdir(exist_ok=True)
    (ROOT / "public" / "data.json").write_text(json.dumps(data, indent=2))
    real = os.environ.get("ANTHROPIC_API_KEY", "").strip() and not any(
        a["explanation"].get("_note") for a in data["alerts"])
    n = len(data["alerts"])
    if real:
        print(f"OK: wrote public/data.json with {n} REAL AI narratives.")
    else:
        print(f"WARNING: wrote public/data.json with {n} TEMPLATE narratives "
              "(no key). Re-run with ANTHROPIC_API_KEY set before deploying.")
