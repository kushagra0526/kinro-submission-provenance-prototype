"""Per-field provenance of a submission + consistency rules → QUOTE-READY / ASK-FIRST / LICENSED REVIEW."""
from __future__ import annotations

import re

from .extract import Fact, extract

PREMIUM_FIELDS = ("annual_payroll", "annual_revenue", "employees", "prior_claims_3y")
REASON = r"\b(correction|i misread|misread|mistake|typo|actually it'?s|because|since we|lost a|laid off|seasonal|was wrong|projection)\b"
CHECKED = ("state", "zip", "years_in_business", "annual_revenue", "employees", "annual_payroll", "prior_claims_3y", "roofing_work",
           "max_stories", "subcontractor_cost", "alcohol_sales_pct", "deliveries", "coverage_start", "gl_limits", "hnoa")
OPS_FIELDS = ("roofing_work", "subcontractor_cost")
# class → operations that usually belong in a different (higher-hazard) class or need underwriter approval
CLASS_EXCLUDES = {"Lawn care": ["tree removal", "tree trimming", "stump grinding", "pesticide"],
                  "Janitorial services": ["window washing", "high-rise", "biohazard"],
                  "Painting - residential": ["high-rise", "industrial coatings"],
                  "Retail - clothing": ["firearms", "vape"]}
ISSUES = {"INFERRED", "CONTRADICTED", "UNSOURCED", "OPS_CONFLICT", "CHANGED_AFTER_QUOTE", "COVERAGE_GAP", "CLASS_FIT"}
REVIEW = {"CHANGED_AFTER_QUOTE", "OPS_CONFLICT", "CLASS_FIT"}


ASK_NAME = {"employees": "How many employees do you have", "annual_payroll": "What is your annual payroll",
            "annual_revenue": "What was your revenue last year", "prior_claims_3y": "How many insurance claims have you had in the last 3 years",
            "years_in_business": "How many years have you been in business"}


def asks(f: str) -> str:
    return ASK_NAME.get(f, f"What is your {f.replace('_', ' ')}")


def same(a, b) -> bool:
    if a == ">0":
        return isinstance(b, (int, float)) and b > 0
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= 0.02 * max(abs(a), abs(b), 1)
    return str(a).upper() == str(b).upper()


def show(v) -> str:
    if v is True:
        return "yes"
    if v is False:
        return "no"
    if v == ">0":
        return "some subcontracted work"
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    if isinstance(v, int) and v >= 10000:
        return f"${v:,}"
    return str(v)


def check(case: dict, year: int) -> dict:
    turns, sub = case["turns"], case["submission"]
    facts = extract(turns, year)
    quote_turns = [i for i, (r, t) in enumerate(turns) if r == "leo" and t.startswith("QUOTE")]
    rows, flags = [], []

    def flag(field, code, msg, ask=None):
        flags.append({"field": field, "code": code, "msg": msg, "ask": ask})

    for f in CHECKED:
        if f not in sub:
            continue
        v = sub[f]
        user = [x for x in facts if x.field == f and x.role == "user"]
        relay = [x for x in facts if x.field == f and x.role == "agent" and not x.hedged]
        guess = [x for x in facts if x.field == f and x.role == "agent" and x.hedged]
        status, src = None, None
        if f in PREMIUM_FIELDS and len(user) >= 2:
            first, last = user[0], user[-1]
            after_quote = any(first.turn < q < last.turn for q in quote_turns)
            if after_quote and isinstance(last.value, (int, float)) and last.value < first.value and same(last.value, v):
                if re.search(REASON, turns[last.turn][1].lower()):
                    status, src = "STATED", last  # corrected with a reason: fine
                else:
                    status, src = "CHANGED_AFTER_QUOTE", last
                    flag(f, status, f"{f} went from {show(first.value)} (turn {first.turn}) to {show(last.value)} right after a quote (turn {last.turn}), "
                         f"with no reason given: “{turns[last.turn][1]}”")
        if status is None and user:
            src = user[-1]
            if same(src.value, v):
                status = "STATED"
            elif f in OPS_FIELDS:
                status = "OPS_CONFLICT"
                flag(f, status, f"application says {f} = {show(v)}, but the owner said: “{src.quote}” (turn {src.turn})")
            else:
                status = "CONTRADICTED"
                flag(f, status, f"application says {show(v)}; the owner said {show(src.value)}: “{src.quote}” (turn {src.turn})",
                     ask=f"You mentioned “{src.quote}”. The application has {f.replace('_', ' ')} = {show(v)}. Which is right?")
        if status is None and relay:
            src = relay[-1]
            status = "RELAYED" if same(src.value, v) else "CONTRADICTED"
            if status == "CONTRADICTED":
                flag(f, status, f"application says {show(v)}; the assistant relayed {show(src.value)} (turn {src.turn})",
                     ask=f"Can you confirm your {f.replace('_', ' ')}?")
        if status is None and f in case["assumed"]:
            status = "ASSUMED"
        if status is None and guess:
            src = guess[-1]
            status = "INFERRED"
            flag(f, status, f"{f} = {show(v)} comes only from the assistant's guess: “{turns[src.turn][1]}” (turn {src.turn}); the owner never said it",
                 ask=f"{asks(f)}? We don't want to quote on an estimate.")
        if status is None:
            status = "UNSOURCED"
            flag(f, status, f"{f} = {show(v)} is in the application, but nobody said it and it isn't a disclosed assumption",
                 ask=f"{asks(f)}?")
        rows.append({"field": f, "value": show(v), "status": status, "turn": src.turn if src else None, "who": src.role if src else None,
                     "quote": src.quote if src else None})

    # coverage gap: deliveries or staff driving their own vehicles, but no hired & non-owned auto
    drives = [x for x in facts if (x.field == "own_vehicle" or (x.field == "deliveries" and x.value)) and x.role in ("user", "agent")]
    if drives and sub.get("hnoa") is False:
        x = drives[-1]
        flag("hnoa", "COVERAGE_GAP", f"no hired & non-owned auto, but: “{x.quote}” (turn {x.turn}). A delivery accident in a personal vehicle could fall outside both policies",
             ask="You mentioned deliveries in your own vehicles. Do you want hired & non-owned auto coverage added?")

    # class fit
    said = " ".join(t.lower() for r, t in turns if r in ("user", "agent"))
    for kw in CLASS_EXCLUDES.get(sub.get("class"), []):
        if kw in said:
            flag("class", "CLASS_FIT", f"class “{sub['class']}” but the owner described “{kw}”, which usually needs its own class or underwriter approval")

    codes = {f["code"] for f in flags}
    verdict = "LICENSED REVIEW" if codes & REVIEW else "ASK-FIRST" if codes else "QUOTE-READY"
    note = "workers' comp: a licensed agent completes the purchase (this packet goes with it)" if "WC" in case["lines"] else None
    return {"id": case["id"], "verdict": verdict, "rows": rows, "flags": flags, "note": note,
            "questions": [f["ask"] for f in flags if f["ask"]]}


# ---------------------------------------------------------------- baseline: "is the value somewhere in the chat?"


def naive(case: dict, year: int) -> list[dict]:
    from .extract import NUM, num
    text = " ".join(t.lower() for _, t in case["turns"])
    seen = set()
    for m in re.finditer(NUM, text):
        try:
            seen.add(round(num(m[1]), 2))
        except ValueError:
            pass
    seen |= {round(year - int(y), 2) for y in re.findall(r"\b((?:19|20)\d\d)\b", text)}
    if re.search(r"\b(no|none|nope|never)\b", text):
        seen.add(0.0)  # "no claims", "no subs": count a spoken zero
    out = []
    for f in CHECKED:
        v = case["submission"].get(f)
        if isinstance(v, (int, float)) and not isinstance(v, bool) and f not in case["assumed"] and round(float(v), 2) not in seen:
            out.append({"field": f, "code": "UNSOURCED"})
    return out
