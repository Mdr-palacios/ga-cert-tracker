#!/usr/bin/env python3
"""
Regenerate ga_certification_tracker.json from ga_certification_tracker.csv.
Run this after editing the CSV.
"""
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
CSV = HERE / 'ga_certification_tracker.csv'
JSON_OUT = HERE / 'ga_certification_tracker.json'

def main():
    if not CSV.exists():
        print(f"ERROR: {CSV} not found", file=sys.stderr)
        sys.exit(1)
    rows = []
    with CSV.open(newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            # normalize whitespace
            rows.append({k: (v or '').strip() for k, v in row.items()})
    with JSON_OUT.open('w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    # Print summary
    counts = {}
    for r in rows:
        s = r.get('certified') or 'Unknown'
        counts[s] = counts.get(s, 0) + 1
    print(f"Wrote {JSON_OUT.name} with {len(rows)} counties")
    print(f"Status breakdown: {counts}")

if __name__ == '__main__':
    main()
