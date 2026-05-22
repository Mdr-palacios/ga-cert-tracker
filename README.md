# Georgia County Certification Tracker

Live tracker of which Georgia counties have certified results from the **May 19, 2026 General Primary**. Built by Common Cause Georgia.

**Statutory deadline**: 5:00 PM Monday, May 25, 2026 (per [O.C.G.A. § 21-2-493(k)](https://law.justia.com/codes/georgia/title-21/chapter-2/article-11/section-21-2-493/)).

## Live URL

Once deployed to GitHub Pages, the tracker is viewable at:
`https://<your-org>.github.io/ga-cert-tracker/`

## Files

| File | Purpose |
|---|---|
| `index.html` | The interactive tracker (map + table + stats). Loads data client-side. |
| `ga_certification_tracker.csv` | **Master data file.** Update this as counties certify. |
| `ga_certification_tracker.json` | Auto-generated from CSV for the web app. Regenerate after edits (see below). |
| `ga_counties.geojson` | Georgia county boundaries with FIPS IDs. No need to edit. |
| `update.py` | Helper script to regenerate JSON from CSV. |
| `extract_meetings.py` | Re-parses `meeting_date` / `meeting_time` from the `notes` field. Run when you add new meeting info to notes. |

## How to update the tracker

When a county certifies, edit `ga_certification_tracker.csv`:

1. Find the row for the county
2. Change `certified` from `No` → `Yes`
3. Fill in `certification_date` (YYYY-MM-DD)
4. Update `ballots_cast`, `registered_voters`, `turnout_pct` with final numbers if available
5. Add anything notable to `notes` (e.g., recount, board challenge)
6. Update `source_url` with link to certified results PDF or board minutes

Then regenerate the JSON file that the dashboard reads:

```bash
python3 extract_meetings.py   # re-parses meeting_date / meeting_time from notes
python3 update.py             # regenerates ga_certification_tracker.json
```

If you set `meeting_date` and `meeting_time` directly in the CSV, you can skip `extract_meetings.py` — but running it is safe (it only overwrites blank rows).

Commit and push. GitHub Pages will redeploy in ~1 minute.

## CSV schema

| Column | Description |
|---|---|
| `fips` | 5-digit county FIPS code (13xxx) — do not change |
| `county` | County name — do not change |
| `certified` | `Yes` / `No` / `Unknown` |
| `certification_date` | YYYY-MM-DD, blank if not certified |
| `certification_deadline` | Default `2026-05-25` |
| `meeting_date` | YYYY-MM-DD of scheduled certification board meeting (auto-extracted from notes by `extract_meetings.py`, or set manually) |
| `meeting_time` | e.g. `3:00 PM` — blank if TBD |
| `ballots_cast` | Total ballots, free-text |
| `registered_voters` | Free-text |
| `turnout_pct` | Percentage with `%`, e.g. `23.31%` |
| `notes` | Free-text, brief |
| `source_url` | Markdown link(s): `[Label](url), [Label2](url2)` |

## Data collection methodology

Georgia's Secretary of State **does not** publish a centralized real-time view of county certification status. The initial baseline (May 21, 2026) was collected by visiting each of the 159 county elections websites and recording status, meeting agendas, certification notices, and unofficial result postings.

Counties marked `Unknown` either have no public elections website, the site was not updated for the May 19 primary, or the certification status could not be determined. These should be the first targets for direct outreach.

## Embedding in WordPress

The map can be embedded in a WordPress page via iframe:

```html
<iframe src="https://<your-org>.github.io/ga-cert-tracker/"
        width="100%" height="1400" frameborder="0"
        title="GA County Certification Tracker"></iframe>
```

## License & contact

Data sources cited per-row in `source_url` column. Tracker code: MIT. Contact: Common Cause Georgia.
