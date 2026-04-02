---
name: statement-to-csv
description: >
  Use when user has brokerage statement PDFs and wants income, dividends, interest
  extracted into CSVs. Triggers on: statement PDFs, brokerage statements, extract income,
  dividend tracking, portfolio income. Multi-institution, monthly/annual rollups,
  investor insights.
context: fork
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
---

# Statement-to-CSV Processor

Transform brokerage/investment statement PDFs into structured CSV reports with income breakdowns, portfolio analytics, and forward-looking insights.

## When This Skill Applies

- User has PDF statements from one or more brokerage institutions
- User wants income, dividend, interest, or financial data extracted
- User wants to track portfolio performance across accounts
- User wants CSV summaries for tax prep, financial planning, or record-keeping

## High-Level Workflow

1. **Discover** - Find all PDF statements and identify institutions
2. **Sample** - Read a few pages from each institution to learn the format
3. **Extract** - Parse income and financial data from every statement
4. **Rename** - Standardize filenames as `[prefix]-[MM]-[YYYY].pdf`
5. **Generate CSVs** - Produce multiple sheets/files with rollups and insights
6. **Validate** - Spot-check extracted values against source PDFs

## Step 1: Discover Statements

Scan the target directory for PDF files. Group them by subdirectory or filename pattern to identify institutions. If the directory structure is flat, read page 1 of each PDF to identify the institution from logos, headers, or account info.

Assign a short lowercase prefix for each institution (e.g., `bka`, `bkb`, `bkc`). Use 2-4 lowercase characters derived from the institution name. If the user has a preference, use that.

## Step 2: Sample and Learn Formats

For each institution, read 2-3 sample statements (first few pages) using `pymupdf` (`fitz`). The goal is to understand:

- **Statement period** - how the date range is expressed
- **Income summary location** - which page and what section heading
- **Income categories** - taxable dividends, tax-exempt dividends, interest, qualified dividends, capital gains distributions, money market/sweep interest, etc.
- **Account value** - ending/closing value field name
- **Other useful data** - gains/losses, deposits/withdrawals, asset allocation, margin info

Read `references/extraction-patterns.md` for known patterns from common institutions. For unknown institutions, use the sampled text to build new regex patterns following the same approach.

**Key parsing principle:** PDF text extraction via `page.get_text()` often places values on separate lines from their labels. Always check whether values follow labels on the same line or on subsequent lines, and build regex patterns accordingly.

## Step 3: Extract Data

For each PDF, extract:

### Required Fields
| Field | Description |
|-------|-------------|
| `month` | YYYY-MM format |
| `institution` | Institution name |
| `account` | Account type and masked number |
| `statement_period` | Human-readable period |
| `account_value` | End-of-period account value |
| `total_income` | Sum of all income for the period |

### Income Breakdown (extract what's available)
| Field | Description |
|-------|-------------|
| `taxable_dividends` | Ordinary/taxable dividends |
| `qualified_dividends` | Qualified dividend subset |
| `tax_exempt_dividends` | Federally tax-exempt dividends |
| `taxable_interest` | Taxable interest income |
| `tax_exempt_interest` | Tax-exempt interest |
| `money_market_interest` | Money market/sweep fund interest |
| `capital_gains_distributions` | Capital gains distributions |
| `return_of_capital` | Return of capital distributions |

### Portfolio Context (extract if present)
| Field | Description |
|-------|-------------|
| `beginning_value` | Start-of-period account value |
| `deposits` | Cash/securities deposited |
| `withdrawals` | Cash/securities withdrawn |
| `change_in_value` | Market appreciation/depreciation |
| `realized_gains_st` | Short-term realized gains/losses |
| `realized_gains_lt` | Long-term realized gains/losses |
| `unrealized_gains` | Total unrealized gains/losses |

### Parsing Tips

- Use `pymupdf` (`import fitz`) for PDF text extraction - it works on all platforms without external dependencies like `poppler`
- Handle encoding: on Windows, wrap stdout with `sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')`
- Parse amounts with a helper that strips `$`, `,`, and handles `(negative)` parentheses notation
- Some statements use `—` or `-` for zero values instead of `0.00`
- YTD figures appear alongside period figures - extract the **period** (this-period) column, not the YTD column
- Account values may use varying field names: "Ending Net Account Value", "Your Account Value", "Closing value", "Ending Account Value", etc.

## Step 4: Rename Files

Rename each PDF using the pattern: `[prefix]-[MM]-[YYYY].pdf`

- `prefix` = institution abbreviation (lowercase, 2-4 chars)
- `MM` = two-digit month
- `YYYY` = four-digit year

Check for conflicts before renaming. Skip if already named correctly.

## Step 5: Generate CSV Reports

Produce **multiple CSV files** (not just one) to give the investor a complete picture. Round all monetary values to 2 decimal places.

Read `references/csv-schemas.md` for the detailed schemas of each CSV file.

### CSV 1: `income_detail.csv` - Full Income Breakdown
Every row is one statement (one institution, one month). Include all extracted fields. After each month's institution rows, insert a **MONTHLY TOTAL** subtotal row. At the end, append:
- **YEARLY TOTAL** rows per institution
- A **GRAND TOTAL** row across all institutions

### CSV 2: `portfolio_summary.csv` - Account Values & Performance
Monthly snapshot of each account's value, deposits, withdrawals, and change. Include:
- Monthly total portfolio value across all institutions
- Month-over-month change in total portfolio value
- Cumulative deposits and withdrawals

### CSV 3: `income_by_source.csv` - Pivot by Income Type
Rows = months, Columns = income types (taxable dividends, qualified dividends, tax-exempt dividends, interest, capital gains, etc.), with a total column. One section per institution, plus a combined section. This helps investors see which income sources are growing or shrinking.

### CSV 4: `investor_insights.csv` - Forward-Looking Analytics
Compute and present:
- **Trailing 12-month income** per institution and combined
- **Annualized yield** = (trailing 12-month income / latest account value) * 100
- **Income trend** = compare H1 vs H2 income, or Q-over-Q
- **Portfolio concentration** = each institution's share of total portfolio value
- **Income diversification** = each institution's share of total income
- **Estimated monthly income run-rate** = trailing 3-month average
- **Tax efficiency ratio** = tax-exempt income / total income

## Step 6: Validate

After generating CSVs, spot-check a few values:
- Pick 2-3 statements and verify the extracted `total_income` matches the PDF
- Verify monthly totals add up to yearly totals
- Flag any months with $0 income or missing data for manual review

Print a summary to the terminal showing:
- Number of statements processed per institution
- Yearly income totals per institution
- Grand total income
- Any warnings or anomalies detected

## Common Mistakes to Avoid

- **Grabbing YTD instead of period values**: Many statements show both side-by-side. The period value is typically the first/left column.
- **Missing income categories**: Some institutions split income differently. If the total doesn't match the sum of parts, note the discrepancy.
- **Encoding errors on Windows**: Always set UTF-8 encoding for stdout and file output.
- **Regex too rigid**: Institution formats evolve over time. Build patterns that tolerate minor variations in spacing, labels, and line breaks.
- **Forgetting to handle `$0` or missing sections**: Some months may have no dividends at all - handle gracefully with 0.0 defaults.
- **Not rounding**: Floating-point arithmetic produces ugly numbers like `3769525.139999999`. Always round to 2 decimal places in output.
