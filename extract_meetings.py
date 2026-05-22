"""
Parse certification meeting dates/times from the 'notes' field.
Strategy: find the FIRST date that appears in a clause containing a meeting/scheduling
keyword. Ignore dates that appear in "As of <date>" reference timestamps.
"""
import csv
import re
import json
from datetime import datetime

TODAY = datetime(2026, 5, 21).date()

MONTHS = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
    'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12,
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6, 'jul': 7, 'aug': 8,
    'sep': 9, 'sept': 9, 'oct': 10, 'nov': 11, 'dec': 12,
}

# Keywords indicating a scheduled certification meeting (not a timestamp reference)
SCHEDULE_KEYWORDS = re.compile(
    r'\b(scheduled|will be held|will certify|to certify|certification meeting|'
    r'pre-?certification|precertification|special called meeting|special meeting|'
    r'board meeting|board of elections meeting|meeting on|meeting is|'
    r'computation and canvassing|meeting was rescheduled|certification is scheduled|'
    r'will be certifying|set to certify|expected to certify|certify .* (election|results)|'
    r'meeting scheduled)\b',
    re.IGNORECASE
)

# Anti-pattern: skip the "as of <date>" reference timestamp
AS_OF_RE = re.compile(r'\bas of\s+[^,;.]+', re.IGNORECASE)


def find_date_in_text(text):
    """Find first date in text that appears in a future window. Returns iso string or None."""
    month_alt = '|'.join(MONTHS.keys())
    # Pattern: optionally preceded by weekday, e.g. "Friday, May 22, 2026"
    pat = re.compile(
        r'(?:(?:mon|tue|wed|thu|fri|sat|sun)[a-z]*,?\s+)?'
        r'(' + month_alt + r')\s+(\d{1,2})(?:st|nd|rd|th)?'
        r'(?:,?\s+(\d{4}))?',
        re.IGNORECASE
    )
    for m in pat.finditer(text):
        month = MONTHS.get(m.group(1).lower())
        day = int(m.group(2))
        year = int(m.group(3)) if m.group(3) else 2026
        try:
            d = datetime(year, month, day).date()
        except ValueError:
            continue
        delta = (d - TODAY).days
        if 0 <= delta <= 60:
            return d.isoformat()

    # Numeric: 5/22 or 5/22/26
    pat2 = re.compile(r'\b(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?\b')
    for m in pat2.finditer(text):
        mm, dd = int(m.group(1)), int(m.group(2))
        yy = m.group(3)
        year = 2026
        if yy:
            year = int(yy)
            if year < 100:
                year += 2000
        try:
            d = datetime(year, mm, dd).date()
        except ValueError:
            continue
        delta = (d - TODAY).days
        if 0 <= delta <= 60:
            return d.isoformat()
    return None


def parse_time(text):
    pat = re.compile(r'\b(\d{1,2})(?::(\d{2}))?\s*([apAP])\.?\s*[mM]\.?\b')
    m = pat.search(text)
    if m:
        h = int(m.group(1))
        mi = m.group(2) or '00'
        ampm = m.group(3).upper() + 'M'
        return f"{h}:{mi} {ampm}"
    if re.search(r'\bnoon\b', text, re.IGNORECASE):
        return "12:00 PM"
    return ''


def extract_meeting(notes):
    """
    Strategy: remove 'as of <date>' phrases, then split into sentences/clauses.
    For each clause that contains a scheduling keyword, find a date in it.
    Return the earliest such future date and its time.
    """
    if not notes:
        return '', ''

    # Remove "as of ..." reference phrases
    cleaned = AS_OF_RE.sub(' ', notes)

    # Split into sentences/clauses
    clauses = re.split(r'[.;]\s+', cleaned)

    candidates = []
    for clause in clauses:
        if SCHEDULE_KEYWORDS.search(clause):
            d = find_date_in_text(clause)
            if d:
                t = parse_time(clause)
                candidates.append((d, t, clause))

    if not candidates:
        return '', ''

    # Return earliest future date
    candidates.sort(key=lambda x: x[0])
    return candidates[0][0], candidates[0][1]


def main():
    from pathlib import Path
    src = str(Path(__file__).parent / 'ga_certification_tracker.csv')

    with open(src, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        cols = list(reader.fieldnames)
        rows = list(reader)

    # Ensure meeting columns exist
    if 'meeting_date' not in cols:
        idx = cols.index('certification_deadline')
        cols = cols[:idx+1] + ['meeting_date', 'meeting_time'] + cols[idx+1:]

    found = 0
    for row in rows:
        if row.get('certified') == 'Yes':
            row['meeting_date'] = ''
            row['meeting_time'] = ''
            continue
        d, t = extract_meeting(row.get('notes', ''))
        row['meeting_date'] = d
        row['meeting_time'] = t
        if d:
            found += 1

    with open(src, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, '') for k in cols})

    # Regenerate JSON
    with open(src.replace('.csv', '.json'), 'w') as f:
        json.dump(rows, f, indent=2)

    print(f"Extracted scheduled meeting date for {found} counties out of {len(rows)} total\n")

    upcoming = sorted(
        [r for r in rows if r.get('meeting_date')],
        key=lambda r: (r['meeting_date'], r.get('meeting_time') or 'zz', r['county'])
    )
    by_date = {}
    for r in upcoming:
        by_date.setdefault(r['meeting_date'], []).append(r)
    for d in sorted(by_date.keys()):
        print(f"{d}: {len(by_date[d])} meetings")
        for r in by_date[d]:
            print(f"  - {r['county']:<18} {r.get('meeting_time') or '(time TBD)':<12}")


if __name__ == '__main__':
    main()
