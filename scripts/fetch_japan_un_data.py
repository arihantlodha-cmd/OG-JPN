"""
Fetch Japan's demographic data from the UN World Population Prospects data
portal and write it in the offline-mirror CSV format
(EAPD-DRB/Population-Data), so it can (a) unblock OG-Japan without the API
and (b) be contributed upstream so Japan works offline like the other
country models.

Requires a UN Data Portal API token. Put it in `un_api_token.txt` next to
this script, or pass it as the first CLI argument. The transform below
mirrors ogcore.demographics.get_un_data exactly (Median variant, Both
sexes, single ages < 100), so the output matches what OG-Core expects.

Usage:
    python scripts/fetch_japan_un_data.py [TOKEN]

Writes:
    Data/JPN/UN_fertility_rates_data.csv
    Data/JPN/UN_mortality_rates_data.csv
    Data/JPN/UN_population_data.csv
"""

import os
import sys
import time
from io import StringIO

import pandas as pd
import requests


def get_with_retry(url, headers, attempts=6):
    """GET a URL, retrying on transient errors (the UN API 502s often)."""
    for i in range(attempts):
        try:
            resp = requests.get(url, headers=headers, timeout=60)
            if resp.status_code in (502, 503, 504):
                raise requests.exceptions.HTTPError(f"{resp.status_code}")
            resp.raise_for_status()
            return resp
        except requests.exceptions.RequestException as exc:
            if i == attempts - 1:
                raise
            wait = 2 ** i
            print(f"    transient error ({exc}); retrying in {wait}s...")
            time.sleep(wait)

BASE = "https://population.un.org/dataportalapi/api/v1"
JAPAN = "392"
# Same indicator ids OG-Core uses (see ogcore.demographics):
INDICATORS = {"68": "fertility_rates", "80": "mortality_rates", "47": "population"}
START_YEAR, END_YEAR = 1950, 2030
OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Data", "JPN")


def get_token():
    if len(sys.argv) > 1:
        return sys.argv[1].strip()
    path = os.path.join(os.path.dirname(__file__), "un_api_token.txt")
    if os.path.exists(path):
        return open(path).read().strip()
    sys.exit(
        "No UN API token found. Pass it as an argument or save it in "
        "scripts/un_api_token.txt (see the Data API docs to request one)."
    )


def fetch_indicator(code, token):
    """Return a year,age,value DataFrame for one indicator, Japan only."""
    url = (
        f"{BASE}/data/indicators/{code}/locations/{JAPAN}"
        f"/start/{START_YEAR}/end/{END_YEAR}"
        "?format=csv&pageSize=1000&pagingInHeader=true"
    )
    headers = {"Authorization": "Bearer " + token}
    frames = []
    while url:
        resp = get_with_retry(url, headers)
        # The CSV response has a header line before the pipe-separated table
        df = pd.read_csv(StringIO(resp.text), sep="|", header=1)
        frames.append(df)
        # follow pagination via the X-Pagination header if present
        nxt = None
        if "X-Pagination" in resp.headers:
            import json

            nxt = json.loads(resp.headers["X-Pagination"]).get("NextPage")
        url = nxt
    df = pd.concat(frames, ignore_index=True)

    # Same filtering/renaming as ogcore.demographics.get_un_data
    df = df[df.Variant == "Median"]
    df = df[df.Sex == "Both sexes"][["TimeLabel", "AgeLabel", "Value"]]
    df = df.rename(
        columns={"TimeLabel": "year", "AgeLabel": "age", "Value": "value"}
    )
    df.age = df.age.astype(str)
    df.loc[df.age == "100+", "age"] = "100"
    df.age = df.age.astype(int)
    df.year = df.year.astype(int)
    df = df[df.age < 100]
    # the API returns identical rows across sub-dimensions; keep one per
    # (year, age)
    df = df.drop_duplicates(subset=["year", "age"])
    return df.sort_values(["year", "age"]).reset_index(drop=True)


def main():
    token = get_token()
    os.makedirs(OUT_DIR, exist_ok=True)
    for code, name in INDICATORS.items():
        print(f"Fetching {name} (indicator {code}) for Japan...")
        df = fetch_indicator(code, token)
        out = os.path.join(OUT_DIR, f"UN_{name}_data.csv")
        df.to_csv(out, index=False)
        print(f"  wrote {len(df)} rows -> {out}")
    print(
        "\nDone. To let OG-Core read these offline, add "
        '\'"392": "JPN"\' to the country_dict in ogcore/demographics.py, '
        "or contribute this Data/JPN folder to EAPD-DRB/Population-Data."
    )


if __name__ == "__main__":
    main()
