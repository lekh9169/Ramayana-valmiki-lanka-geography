"""Build report.html from the computed JSON/CSV outputs (all numbers come from data/)."""
import csv
import html
import json
from pathlib import Path

import rsl

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


def j(name):
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def esc(x):
    return html.escape(str(x))


def table(headers, rows, cls=""):
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<table class="{cls}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def fig(src, caption):
    return (f'<figure><a href="maps/{src}" target="_blank" rel="noopener"><img src="maps/{src}" alt="{esc(caption)}" loading="lazy"/></a>'
            f'<figcaption>{caption}</figcaption></figure>')


def sea_level_rows():
    with open(DATA / "rsl_curve.csv", newline="", encoding="utf-8") as handle:
        rows = [r for r in csv.DictReader(handle) if not r["age_ka"].startswith("#")]
    return [[r["age_ka"], f"{float(r['rsl_m']):+.1f}", f"±{float(r['sigma_m']):.1f}", esc(r["source"])] for r in rows]


ROCK_SILL_M = -10.0  # present sand crest (~-1 to -3 m) minus 7-9 m of loose sand (Dandabathula et al. 2024)


def link_state(level, sigma, sill):
    if level < sill - sigma:
        return "<b>Land bridge</b>"
    if level < sill + sigma:
        return "<b>Threshold</b> (within ±1σ)"
    return f"<b>Island</b> ({level - sill:.1f} m over the sill)"


def epoch_rows(sill):
    rows = []
    for e in j("epochs.json"):
        level, sigma = rsl.rsl_at(e["age_ka"])
        year = rsl.bp_to_year(e["age_ka"])
        n = 1 - year
        era = f"{year} CE" if year > 0 else (f"{n:,} BCE" if n >= 10000 else f"{n} BCE")
        rows.append([esc(e["label"]), era, f"{max(e['age_ka'], 0):.2f}", f"{level:+.1f} ± {sigma:.1f}",
                     link_state(level, sigma, sill), link_state(level, sigma, ROCK_SILL_M)])
    return rows


def build(sections, title="Lanka and the places of the Valmiki Ramayana — historical edition", edition="historical",
          description="Historical edition: GEBCO 2026 bathymetry, JPL DE441 astronomy and the Sanskrit text locate Lanka, "
                      "the Setu and the places of Rama's route."):
    """Wrap report sections in the site shell (top bar, contents panel, footer with attributions)."""
    import site_template
    body = site_template.report_shell("".join(sections), edition)
    active = {"historical": "historical", "treta": "treta"}[edition]
    return site_template.page(title, body, active, description, body_class=f"edition-{edition}")


if __name__ == "__main__":
    import report_text  # narrative sections, kept separate from the table plumbing
    out = ROOT / "report.html"
    out.write_text(build(report_text.sections()), encoding="utf-8")
    print(out)
