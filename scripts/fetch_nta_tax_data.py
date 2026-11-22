"""
Build ogjpn/data/nta_2023_salary_tax.csv from the National Tax Agency's
Statistical Survey of Actual Status for Salary in the Private Sector
(民間給与実態統計調査), 2023 (令和5年分), full-year private-sector earners
(１年を通じて勤務した給与所得者), both sexes.

  - Table 3 (第3表 給与階級別の総括表), sheet その１: number of earners and
    total salary by salary bracket.
  - Table 16 (第16表 給与階級別の納税者数・非納税者数), sheet その１: number of
    taxpayers and income tax withheld (national income tax including the
    2.1% reconstruction surtax) by salary bracket.

2023 is used rather than 2024 because 2024 withholding includes the one-off
flat income tax cut (定額減税), which would bias a permanent schedule down.

Needs pandas and openpyxl:

    uv run --with pandas --with openpyxl python scripts/fetch_nta_tax_data.py
"""

import io
import os
import urllib.request

import pandas as pd

BASE = "https://www.nta.go.jp/publication/statistics/kokuzeicho/minkan2023/excel/"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "ogjpn", "data", "nta_2023_salary_tax.csv")

# Upper bound of each salary bracket, million yen (None = open top bracket).
UPPER = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, None]


def _read(name):
    with urllib.request.urlopen(BASE + name) as resp:
        return pd.read_excel(io.BytesIO(resp.read()), "その１", header=None)


def _num(v):
    return 0.0 if str(v).strip() in ("-", "nan", "") else float(v)


def main():
    t3 = _read("R05_03.xlsx")
    t16 = _read("R05_16.xlsx")

    # Table 3: the third block (sex = 計, both sexes) of 14 bracket rows.
    start = t3.index[t3[1].astype(str).str.strip() == "計"][0]
    n = [_num(v) for v in t3.iloc[start : start + 14, 5]]
    salary = [_num(v) * 1e6 for v in t3.iloc[start : start + 14, 10]]

    # Table 16: taxpayer counts (column 9, 合計 納税者) follow the
    # 給与所得者数 header; tax withheld (column 11, 合計 計, million yen)
    # follows the 税額 header.
    c = t16.index[t16[1].astype(str).str.contains("給与所得者数")][0]
    taxpayers = [_num(v) for v in t16.iloc[c + 1 : c + 15, 9]]
    x = t16.index[t16[1].astype(str).str.strip() == "税額"][0]
    tax = [_num(v) * 1e6 for v in t16.iloc[x + 1 : x + 15, 11]]

    df = pd.DataFrame(
        {
            "upper_million_yen": UPPER,
            "earners": n,
            "taxpayers": taxpayers,
            "salary_total_yen": salary,
            "income_tax_withheld_yen": tax,
        }
    )
    # Sanity checks against the published totals.
    assert (
        abs(df.earners.sum() - 50_761_385) < 10
    )  # published total; bracket rows round
    assert abs(df.salary_total_yen.sum() / df.earners.sum() - 4.595e6) < 1e4
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    df.to_csv(OUT, index=False)
    print("wrote", OUT)
    print(df.to_string())


if __name__ == "__main__":
    main()
