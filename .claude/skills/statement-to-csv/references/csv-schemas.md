# CSV Output Schemas

Detailed column definitions and formatting rules for each CSV report file.

## Table of Contents

- [General Formatting Rules](#general-formatting-rules)
- [CSV 1: income_detail.csv](#csv-1-income_detailcsv)
- [CSV 2: portfolio_summary.csv](#csv-2-portfolio_summarycsv)
- [CSV 3: income_by_source.csv](#csv-3-income_by_sourcecsv)
- [CSV 4: investor_insights.csv](#csv-4-investor_insightscsv)

---

## General Formatting Rules

- All monetary values rounded to 2 decimal places
- Use UTF-8 encoding with BOM for Excel compatibility: `open(path, 'w', newline='', encoding='utf-8-sig')`
- Empty cells for non-applicable fields in summary rows (not 0)
- Month format: `YYYY-MM` (e.g., `2025-01`)
- Institution names: use full name as found in the PDF (e.g., "Broker A", "Broker B")
- Summary row institution names: `MONTHLY TOTAL`, `[Institution] YEARLY TOTAL`, `GRAND TOTAL`
- Sort data rows by (month, institution name) ascending

---

## CSV 1: income_detail.csv

The primary report. Every row is one statement from one institution for one month, plus subtotal and total rows.

### Columns

| Column | Type | Description |
|--------|------|-------------|
| `month` | string | `YYYY-MM` or `YYYY` for yearly totals |
| `institution` | string | Institution name or summary label |
| `account` | string | Account type and masked number |
| `file` | string | Renamed filename |
| `account_value` | float | End-of-period account value |
| `taxable_dividends` | float | Ordinary/taxable dividends |
| `qualified_dividends` | float | Qualified dividend subset |
| `tax_exempt_dividends` | float | Tax-exempt dividends |
| `taxable_interest` | float | Taxable interest |
| `tax_exempt_interest` | float | Tax-exempt interest |
| `money_market_interest` | float | Money market/sweep interest |
| `capital_gains_dist` | float | Capital gains distributions |
| `total_income` | float | Total income for the period |

### Row Structure

For each month (e.g., 3 institutions):
```
2025-01, Broker A, ..., 312.74
2025-01, Broker B, ..., 198.55
2025-01, Broker C, ..., 87.63
2025-01, MONTHLY TOTAL, ..., 598.92    <- sum of all institutions for Jan
```

After all months:
```
(blank separator row)
2025, Broker A YEARLY TOTAL, ..., 7241.08
2025, Broker B YEARLY TOTAL, ..., 5933.16
2025, Broker C YEARLY TOTAL, ..., 4518.77
2025, GRAND TOTAL,           ..., 17693.01
```

---

## CSV 2: portfolio_summary.csv

Tracks account values, cash flows, and portfolio-level performance over time.

### Columns

| Column | Type | Description |
|--------|------|-------------|
| `month` | string | `YYYY-MM` |
| `institution` | string | Institution name or `PORTFOLIO TOTAL` |
| `account` | string | Account type and masked number |
| `beginning_value` | float | Start-of-period value |
| `deposits` | float | Cash/securities deposited |
| `withdrawals` | float | Cash/securities withdrawn |
| `income` | float | Total income received |
| `change_in_value` | float | Market appreciation/depreciation |
| `ending_value` | float | End-of-period value |
| `mom_change_pct` | float | Month-over-month % change in ending value |

### Row Structure

For each month, one row per institution plus a `PORTFOLIO TOTAL` row:
```
2025-01, Broker A,        ..., 487250.00
2025-01, Broker B,        ..., 263410.80
2025-01, Broker C,        ..., 175890.45
2025-01, PORTFOLIO TOTAL, ..., 926551.25, 2.3%
```

At the end, include summary rows:
```
(blank separator)
2025, CUMULATIVE DEPOSITS,    ..., [sum of all deposits]
2025, CUMULATIVE WITHDRAWALS, ..., [sum of all withdrawals]
2025, NET CASH FLOW,          ..., [deposits - withdrawals]
2025, PORTFOLIO GROWTH,       ..., [ending - beginning - net cash flow]
```

---

## CSV 3: income_by_source.csv

Pivoted view showing income by type across months. Helps investors see which income sources are growing.

### Structure

One section per institution, then a combined section.

```
Broker A
month,      taxable_div, qualified_div, tax_exempt_div, interest, money_market, cap_gains, total
2025-01,    189.72,      0.00,          73.44,          25.68,    0.00,         0.00,      288.84
2025-02,    64.15,       0.00,          58.93,          19.42,    0.00,         0.00,      142.50
...
TOTAL,      5418.30,     0.00,          742.65,         148.12,   0.00,         0.00,      7241.08

(blank row)

Broker B
...

(blank row)

ALL INSTITUTIONS COMBINED
month,      taxable_div, qualified_div, tax_exempt_div, interest, money_market, cap_gains, total
2025-01,    412.56,      0.00,          73.44,          26.91,    0.18,         0.00,      598.92
...
```

The section headers are the institution name (plain text, no decorators like `===`) placed in the first column of an otherwise blank row. Do NOT wrap section headers in `===` or other markers — they cause parse errors in spreadsheet applications.

---

## CSV 4: investor_insights.csv

Forward-looking analytics computed from the extracted data. Each metric is a labeled row.

### Structure

```
metric,              institution,    value,      notes
--- INCOME ANALYTICS ---
Trailing 12-Mo Income, Broker A,     7241.08,   Jan-Dec 2025
Trailing 12-Mo Income, Broker B,     5933.16,   Jan-Dec 2025
Trailing 12-Mo Income, Broker C,     4518.77,   Jan-Dec 2025
Trailing 12-Mo Income, COMBINED,     17693.01,  Jan-Dec 2025

(blank row)
--- YIELD ANALYSIS ---
Annualized Yield %,    Broker A,     1.49,      Based on latest account value
Annualized Yield %,    Broker B,     2.25,      Based on latest account value
Annualized Yield %,    Broker C,     2.57,      Based on latest account value
Annualized Yield %,    COMBINED,     [weighted], Weighted by account value

(blank row)
--- INCOME TREND ---
H1 Total Income,       COMBINED,     [sum],     Jan-Jun
H2 Total Income,       COMBINED,     [sum],     Jul-Dec
H2 vs H1 Change %,    COMBINED,     [pct],     Positive = income growing
Q1 Income,            COMBINED,     [sum],     Jan-Mar
Q2 Income,            COMBINED,     [sum],     Apr-Jun
Q3 Income,            COMBINED,     [sum],     Jul-Sep
Q4 Income,            COMBINED,     [sum],     Oct-Dec

(blank row)
--- INCOME RUN RATE ---
Avg Monthly Income (Last 3 Mo), Broker A,  [avg],  Based on Oct-Dec
Avg Monthly Income (Last 3 Mo), Broker B,  [avg],  Based on Oct-Dec
Avg Monthly Income (Last 3 Mo), Broker C,  [avg],  Based on Oct-Dec
Avg Monthly Income (Last 3 Mo), COMBINED,  [avg],  Based on Oct-Dec
Est. Annual Income (Run Rate),  COMBINED,  [x12],  Last 3-mo avg * 12

(blank row)
--- PORTFOLIO CONCENTRATION ---
Portfolio Share %,     Broker A,     [pct],     Of total portfolio value
Portfolio Share %,     Broker B,     [pct],     Of total portfolio value
Portfolio Share %,     Broker C,     [pct],     Of total portfolio value

(blank row)
--- INCOME DIVERSIFICATION ---
Income Share %,        Broker A,     [pct],     Of total annual income
Income Share %,        Broker B,     [pct],     Of total annual income
Income Share %,        Broker C,     [pct],     Of total annual income

(blank row)
--- TAX EFFICIENCY ---
Tax-Exempt Income %,   Broker A,     [pct],     Tax-exempt / total income
Tax-Exempt Income %,   Broker B,     [pct],
Tax-Exempt Income %,   Broker C,     [pct],
Tax-Exempt Income %,   COMBINED,     [pct],
Qualified Div %,       COMBINED,     [pct],     Qualified / total dividends
```

### Computation Notes

- **Annualized Yield**: Use the most recent month's ending account value as denominator
- **Income Trend**: Compare first half (Jan-Jun) vs second half (Jul-Dec); also show quarterly
- **Run Rate**: Average the last 3 months of available data, multiply by 12 for annual estimate
- **Portfolio Concentration**: Each institution's latest ending value / sum of all latest ending values
- **Tax Efficiency**: Higher tax-exempt % means more tax-efficient income
- **Qualified Dividend %**: Qualified dividends receive preferential tax rates - higher is better for after-tax returns
