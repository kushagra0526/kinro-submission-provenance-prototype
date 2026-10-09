import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "data"))

from cases import CASES, TODAY_YEAR, TRUTH  # noqa: E402

from provenance.check import check, naive  # noqa: E402
from provenance.extract import extract  # noqa: E402

BY = {c["id"]: c for c in CASES}


def flags(cid, case=None):
    return {(f["field"], f["code"]) for f in check(case or BY[cid], TODAY_YEAR)["flags"]}


def test_all_planted_found_no_false_flags():
    got = {(c["id"], f, code) for c in CASES for f, code in flags(c["id"])}
    assert got == set(TRUTH)


def test_clean_cases_quote_ready_and_baseline_weaker():
    assert {c["id"] for c in CASES if check(c, TODAY_YEAR)["verdict"] == "QUOTE-READY"} == {"K01", "K02", "K06", "K12"}
    base = {(c["id"], f["field"]) for c in CASES for f in naive(c, TODAY_YEAR)}
    assert len({t for t in TRUTH if (t[0], t[1]) in base}) <= 4


def test_correction_with_reason_is_fine_but_without_is_review():
    assert check(BY["K06"], TODAY_YEAR)["verdict"] == "QUOTE-READY"
    c = copy.deepcopy(BY["K06"])
    c["turns"][-1] = ("user", "Hmm, put revenue at $600k instead.")
    assert ("annual_revenue", "CHANGED_AFTER_QUOTE") in flags(None, c)


def test_relay_plain_vs_hedged():
    rows = {r["field"]: r for r in check(BY["K02"], TODAY_YEAR)["rows"]}
    assert rows["state"]["status"] == "RELAYED" and rows["annual_payroll"]["status"] == "STATED"
    assert {"employees", "annual_payroll"} == {f for f, c in flags("K04") if c == "INFERRED"}


def test_assumption_must_be_disclosed():
    c = copy.deepcopy(BY["K12"])
    c["assumed"] = []
    assert ("coverage_start", "UNSOURCED") in flags(None, c)


def test_extractor_paraphrases():
    turns = [("user", "We've got 6 full-time employees and gross about $2.3 million in sales. Started in 2011, zip 10001, New York."),
             ("leo", "Any claims, subcontractors or roof work?"),
             ("user", "Two claims back in 2023. We never touch roofs. I subcontract the drywall.")]
    got = {(f.field, f.value) for f in extract(turns, TODAY_YEAR)}
    assert {("employees", 6), ("annual_revenue", 2_300_000), ("years_in_business", 15), ("zip", "10001"), ("state", "NY"),
            ("prior_claims_3y", 2), ("roofing_work", False), ("subcontractor_cost", ">0")} <= got


def test_wc_note_and_questions():
    r = check(BY["K13"], TODAY_YEAR)
    assert r["note"] and "licensed agent" in r["note"]
    assert r["questions"] and "me plus four guys" in r["questions"][0]
