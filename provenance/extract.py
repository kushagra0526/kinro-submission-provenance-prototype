"""Pull business facts out of conversation turns, with who said them and where.

Rule-based on purpose: it only has to read owners' plain statements ("me plus four guys", "$1.1M", "since 2019").
An LLM extractor can replace it; the provenance logic in check.py doesn't change.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "a": 1}
NUM = r"(\$?\d[\d,]*(?:\.\d+)?\s*(?:k|m|grand|million)?\b|\b(?:one|two|three|four|five|six|seven|eight|nine|ten)\b)"
STATES = {"texas": "TX", "arizona": "AZ", "ohio": "OH", "georgia": "GA", "north carolina": "NC", "colorado": "CO", "florida": "FL",
          "pennsylvania": "PA", "oregon": "OR", "michigan": "MI", "tennessee": "TN", "california": "CA", "illinois": "IL", "new york": "NY"}
HEDGE = r"\b(probably|likely|maybe|i'?d guess|i assume|assuming|didn'?t say|not sure|should be|must have|typically)\b"
NEG = r"\b(no|never|none|nope|don'?t|do not|without)\b"


@dataclass
class Fact:
    field: str
    value: object
    turn: int
    role: str
    quote: str
    hedged: bool = False


def num(s: str) -> float:
    s = s.strip().lower()
    if s in WORDS:
        return WORDS[s]
    mult = 1000 if re.search(r"(k|grand)$", s) else 1_000_000 if re.search(r"(m|million)$", s) else 1
    return float(re.sub(r"[^\d.]", "", s)) * mult


def sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+|,\s+(?=(?:and|but|we|i|that'?s|everything|pickup)\b)", text) if s.strip()]


def facts_in(text: str, turn: int, role: str, prev_question: str, year: int) -> list[Fact]:
    t = text.lower().replace("’", "'")
    hedged = bool(re.search(HEDGE, t)) and role != "user"
    out: list[Fact] = []

    def add(field, value, quote):
        out.append(Fact(field, value, turn, role, quote.strip(), hedged))

    for s in sentences(t):
        if m := re.search(rf"\b(?:revenue|sales)\b(?: (?:is|was|were|of|around|about|are|at|to))*\s*{NUM}", s):
            add("annual_revenue", num(m[1]), m[0])
        elif m := re.search(rf"{NUM}\s*(?:in )?(?:revenue|sales)\b", s):
            add("annual_revenue", num(m[1]), m[0])
        elif (m := re.search(rf"{NUM}\s*(?:a|per) year\b", s)) and "payroll" not in s:
            add("annual_revenue", num(m[1]), m[0])
        if m := re.search(rf"\bpayroll\b(?: (?:is|was|about|around|of|to|at))*\s*{NUM}", s):
            add("annual_payroll", num(m[1]), m[0])
        elif m := re.search(rf"{NUM}\s*(?:in )?payroll\b", s):
            add("annual_payroll", num(m[1]), m[0])
        if m := re.search(rf"\bme (?:plus|and) {NUM} (?:guys|employees|people|workers)", s) or \
                re.search(rf"{NUM} (?:full[- ]time )?(?:employees|guys|people|staff|workers)\b", s):
            add("employees", num(m[1]), m[0])
        if m := re.search(r"\b(?:since|started in|open since|opened in)\s+((?:19|20)\d\d)\b", s):
            add("years_in_business", year - int(m[1]), m[0])
        elif m := re.search(rf"\b(?:in business|been in business|been open|open)\s+{NUM}\s+years\b", s):
            add("years_in_business", num(m[1]), m[0])
        if m := re.search(r"\b(\d{5})\b", s):
            add("zip", m[1], m[0])
        for name, ab in STATES.items():
            if re.search(rf"\b{name}\b", s):
                add("state", ab, name)
        # claims
        if re.search(r"\bno claims\b|\bnone in the last\b|\bno .{0,15}claims\b", s) or \
                (re.search(r"\bclaims?\b", prev_question) and re.match(r"(none|no|nope)\b", s)):
            add("prior_claims_3y", 0, s)
        elif m := re.search(rf"{NUM}(?: small)?(?: [\w']+){{0,3}} claims?\b", s):
            add("prior_claims_3y", num(m[1]), m[0])
        # roofing
        if re.search(r"\broof", s):
            if re.search(rf"{NEG}[^.]{{0,20}}\broof", s):
                add("roofing_work", False, s)
            else:
                add("roofing_work", True, s)
        elif re.search(r"\bshingles?\b", s):
            add("roofing_work", True, s)
        # subcontractors
        if re.search(r"\bsub (?:out|contract)|\bsubcontract(?:or|ors|ing)?\b|\b1099\b", s) and not re.search(rf"{NEG}[^.]{{0,12}}sub", s):
            add("subcontractor_cost", ">0", s)
        elif re.search(r"\bno subs\b|\bdon'?t use subs\b|\bno subcontract", s) or \
                (re.search(r"\bsub", prev_question) and re.match(r"(none|no|nope)\b", s)):
            add("subcontractor_cost", 0, s)
        # alcohol
        if re.search(r"\bno alcohol\b", s):
            add("alcohol_sales_pct", 0, s)
        elif (m := re.search(r"(\d+)\s*(?:%|percent)", s)) and re.search(r"\b(beer|wine|alcohol|liquor|bar|drinks)\b", s):
            add("alcohol_sales_pct", float(m[1]), s)
        # deliveries and vehicles
        if re.search(r"\bdeliver", s):
            neg = re.search(r"\bno deliver|\bdon'?t deliver", s) or (re.search(r"\bdeliver", prev_question) and re.match(r"(no|nope)\b", s))
            add("deliveries", not neg, s)
        if re.search(r"\b(?:my|their) own (?:van|car|truck|vehicle)s?\b|\buse their cars\b", s):
            add("own_vehicle", True, s)
        # height
        for m in re.finditer(rf"{NUM}[- ]stor(?:y|ies)\b", s):
            add("max_stories", num(m[1]), m[0])
    return out


def extract(turns, year: int) -> list[Fact]:
    facts, prev_q = [], ""
    for i, (role, text) in enumerate(turns):
        if role == "leo":
            prev_q = text.lower()
            continue
        facts += facts_in(text, i, role, prev_q, year)
    # several stories mentions in one turn: keep the highest
    best = {}
    for f in facts:
        if f.field == "max_stories":
            k = (f.turn, f.role)
            if k not in best or f.value > best[k].value:
                best[k] = f
    return [f for f in facts if f.field != "max_stories"] + list(best.values())
