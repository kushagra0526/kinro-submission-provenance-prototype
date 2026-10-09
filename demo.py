"""14 conversations → per-field provenance, flags, verdicts; compared with "is the value somewhere in the chat?" → out/report.html

    python demo.py
"""
from __future__ import annotations

import html
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "data"))

from cases import CASES, TODAY_YEAR, TRUTH  # noqa: E402

from provenance.check import check, naive  # noqa: E402

COL = {"QUOTE-READY": "#16a34a", "ASK-FIRST": "#d97706", "LICENSED REVIEW": "#dc2626"}
SCOL = {"STATED": "#16a34a", "RELAYED": "#0d9488", "ASSUMED": "#6b7280", "INFERRED": "#d97706", "CONTRADICTED": "#dc2626",
        "OPS_CONFLICT": "#dc2626", "UNSOURCED": "#d97706", "CHANGED_AFTER_QUOTE": "#dc2626"}


def main() -> int:
    results = [check(c, TODAY_YEAR) for c in CASES]
    truth = set(TRUTH)
    got = {(r["id"], f["field"], f["code"]) for r in results for f in r["flags"]}
    base = {(c["id"], f["field"]) for c in CASES for f in naive(c, TODAY_YEAR)}
    base_hits = {t for t in truth if (t[0], t[1]) in base}
    base_false = {b for b in base if not any((t[0], t[1]) == b for t in truth)}

    print(f"\n== {len(CASES)} conversations → submissions")
    for r in results:
        print(f"  {r['id']}  {r['verdict']:<16} " + ", ".join(f"{f['code']}({f['field']})" for f in r["flags"]))
    print(f"\n  planted issues found: {len(truth & got)}/{len(truth)} · false flags: {len(got - truth)}")
    print(f"  'value appears somewhere in the chat' check: found {len(base_hits)}/{len(truth)} · false flags: {len(base_false)}")
    stat = {}
    for r in results:
        for row in r["rows"]:
            stat[row["status"]] = stat.get(row["status"], 0) + 1
    print("  field statuses: " + ", ".join(f"{k} {v}" for k, v in sorted(stat.items(), key=lambda x: -x[1])))
    for cid in ("K05", "K04"):
        r = next(x for x in results if x["id"] == cid)
        print(f"\n== {cid} packet ({r['verdict']})")
        for f in r["flags"]:
            print(f"  {f['code']}: {f['msg']}")
        for q in r["questions"]:
            print(f"  ask the owner: {q}")
    report(results, truth, got, base_hits, base_false, stat)
    print("\nreport: out/report.html")
    return 0 if got == truth else 1


def report(results, truth, got, base_hits, base_false, stat):
    e = html.escape
    out = HERE / "out"
    out.mkdir(exist_ok=True)
    cards = []
    for r, c in zip(results, CASES):
        fl = "".join(f"<li><b>{e(f['code'])}</b> · {e(f['msg'])}</li>" for f in r["flags"])
        qs = "".join(f"<li>{e(q)}</li>" for q in r["questions"])
        cards.append(f"<div class=card><div><b>{c['id']}</b> {e(c['submission']['class'])}, {c['submission']['state']} "
                     f"<span class=pill style='background:{COL[r['verdict']]}'>{r['verdict']}</span></div>"
                     f"<ul>{fl or '<li class=ok>every field traced to the owner, the relay, or a disclosed assumption</li>'}</ul>"
                     + (f"<div class=sub>Ask the owner:</div><ul>{qs}</ul>" if qs else "") + (f"<div class=sub>{e(r['note'])}</div>" if r["note"] else "") + "</div>")
    k = next(x for x in results if x["id"] == "K05")
    prow = "".join(f"<tr><td>{e(x['field'])}</td><td>{e(x['value'])}</td><td style='color:{SCOL.get(x['status'], '#333')}'><b>{x['status']}</b></td>"
                   f"<td>{'turn ' + str(x['turn']) + ' · ' + x['who'] if x['who'] else '—'}</td><td>{e(x['quote'] or '')}</td></tr>" for x in k["rows"])
    (out / "report.html").write_text(f"""<!doctype html><meta charset=utf-8><title>Submission provenance</title>
<style>body{{font:14px/1.45 'Segoe UI',system-ui,sans-serif;margin:28px;max-width:1400px;color:#1d1d1f;background:#fafaf8}}h1{{font-size:23px;margin:0}}
h2{{font-size:17px;margin:24px 0 8px}}.sub{{color:#666}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}
.card{{background:#fff;border:1px solid #e5e5e0;border-radius:8px;padding:10px 14px}}.card ul{{margin:6px 0;padding-left:18px}}.ok{{color:#16a34a}}
.pill{{color:#fff;border-radius:4px;padding:1px 7px;font-size:12px}}table{{border-collapse:collapse;background:#fff}}td,th{{border-top:1px solid #e5e5e0;padding:5px 10px;text-align:left}}
.kpi{{display:flex;gap:24px;margin:10px 0}}.kpi div{{background:#fff;border:1px solid #e5e5e0;border-radius:8px;padding:10px 16px}}.kpi b{{font-size:22px;display:block}}</style>
<h1>Before it goes to carriers: who said each fact in the submission?</h1>
<div class=sub>14 invented conversations (owner, the owner's AI assistant over MCP, and the broker's advisor) and the submission each would produce.</div>
<div class=kpi><div><b>{len(truth & got)}/{len(truth)}</b>planted issues found</div><div><b>{len(got - truth)}</b>false flags</div>
<div><b>{len(base_hits)}/{len(truth)}</b>found by “is the value somewhere in the chat?” ({len(base_false)} false)</div>
<div><b>{sum(r['verdict'] == 'QUOTE-READY' for r in results)}</b>quote-ready with no human touch</div></div>
<h2>Packet: K05 (landscaping, workers' comp)</h2><table><tr><th>field</th><th>value sent</th><th>status</th><th>source</th><th>evidence</th></tr>{prow}</table>
<h2>All submissions</h2><div class=grid>{''.join(cards)}</div>
<p class=sub>Unofficial prototype by Kushagra Pratap Singh. Not affiliated with Kinro.</p>""", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
