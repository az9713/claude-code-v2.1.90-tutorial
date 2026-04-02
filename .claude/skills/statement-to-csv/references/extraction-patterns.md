# Extraction Patterns for Common Institutions

Reference patterns for parsing income and financial data from brokerage statement PDFs. Each section illustrates a common PDF text layout style as extracted by `pymupdf`, with regex patterns that work for that style. Real institutions may use one of these styles or a variation.

## Table of Contents

- [General Approach](#general-approach)
- [Style A: Labels and Values on Separate Lines](#style-a-labels-and-values-on-separate-lines)
- [Style B: Multi-Column Grid (4 Values per Row)](#style-b-multi-column-grid-4-values-per-row)
- [Style C: Uppercase Headers with Two-Column Layout](#style-c-uppercase-headers-with-two-column-layout)
- [Style D: Tabular Fund-Level Distributions](#style-d-tabular-fund-level-distributions)
- [Style E: Compact Inline Summary](#style-e-compact-inline-summary)
- [Style F: Detailed Per-Security Breakdown](#style-f-detailed-per-security-breakdown)
- [Adding New Institutions](#adding-new-institutions)

---

## General Approach

### PDF Text Extraction Setup

```python
import fitz  # pymupdf
import sys, io

# Windows encoding fix
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def get_full_text(filepath):
    doc = fitz.open(filepath)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    doc.close()
    return text

def parse_amount(s):
    """Parse dollar amount string to float. Handles $, commas, parentheses for negatives."""
    if not s:
        return 0.0
    s = s.replace('$', '').replace(',', '').replace('(', '-').replace(')', '').strip()
    if s in ('—', '-', 'N/A', 'n/a', ''):
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0
```

### Key Extraction Principles

1. **Sample first**: Read 2-3 pages and use `repr()` to see the exact text with newlines
2. **Values may be on separate lines**: `get_text()` often puts each value on its own line
3. **Period vs YTD**: When two columns exist, period values come first (left column)
4. **Section boundaries**: Use the next section heading as a regex boundary to avoid bleeding into other sections
5. **Amount patterns**: `[\d,]+\.\d+` captures most dollar amounts; prefix with `\$?` for optional dollar signs

### Institution Detection

Read page 1 of each PDF and search for institution-identifying keywords in the text. Common patterns:

- Full institution name in header or footer
- Clearing firm name (e.g., "National Financial Services", "Pershing")
- Account branding (e.g., product names, registered trademarks)
- FINRA/SIPC disclosures mentioning the firm

---

## Style A: Labels and Values on Separate Lines

**When you'll see this**: Institutions that render income summaries with each label on its own line, followed by the value on the next line. Period and YTD values alternate.

### Statement Period
Text pattern (values on separate lines):
```
INVESTMENT REPORT\n
March 1, 2025 - March 31, 2025\n
```

Regex:
```python
re.search(r'(\w+)\s+\d+,\s*(\d{4})\s*-\s*(\w+)\s+(\d+),\s*(\d{4})', text)
# group(3) = end month name, group(5) = end year
```

### Income Summary
Text layout (each label and value on its own line):
```
Income Summary\n
This Period\n
Year-to-Date\n
Taxable\n
$215.40\n          <- This Period taxable total
$648.93\n          <- YTD taxable total
Dividends\n
189.72\n            <- This Period taxable dividends
562.15\n            <- YTD taxable dividends
Interest\n
25.68\n             <- This Period taxable interest
86.78\n
Tax-exempt\n
73.44\n             <- This Period tax-exempt total
221.07\n
Dividends\n
73.44\n             <- This Period tax-exempt dividends
221.07\n
Total\n
$288.84\n           <- This Period total income
$869.99\n
```

Extraction approach:
```python
inc_match = re.search(r'Income Summary\n.*?Total\n\$?([\d,]+\.\d+)', text, re.DOTALL)
if inc_match:
    lines = inc_match.group(0).split('\n')
    # Walk lines tracking state: in_taxable vs in_exempt
    # When you see "Dividends" or "Interest", the NEXT line has the period value
```

### Account Value
Field names vary by month: "Your Net Account Value", "Your Account Value", "Ending Net Account Value", "Ending Account Value"

```python
re.search(r'(?:Ending (?:Net )?Account Value|Your (?:Net )?Account Value)[:\s]*\$?([\d,]+\.\d+)', text)
```

---

## Style B: Multi-Column Grid (4 Values per Row)

**When you'll see this**: Institutions that show income in a 4-column grid with Tax-Exempt Period, Taxable Period, Tax-Exempt YTD, and Taxable YTD values on consecutive lines after each label.

### Statement Period
Text pattern:
```
Statement Period\n
March 1-31, 2025\n
```

### Income Summary
Text layout (4 columns: Tax-Exempt Period, Taxable Period, Tax-Exempt YTD, Taxable YTD):
```
Income Summary\n
...chart data...\n
This Period\n
YTD\n
Federal Tax Status\n
Tax-Exempt\n
Taxable\n
Tax-Exempt\n
Taxable\n
Interest\n
0.00\n              <- Tax-Exempt period
1.47\n              <- Taxable period
0.00\n              <- Tax-Exempt YTD
4.22\n              <- Taxable YTD
Cash Dividends\n
0.00\n              <- Tax-Exempt period
176.38\n            <- Taxable period
0.00\n              <- Tax-Exempt YTD
512.94\n            <- Taxable YTD
Total Income\n
$0.00\n             <- Tax-Exempt period
$177.85\n           <- Taxable period
$0.00\n             <- Tax-Exempt YTD
$517.16\n           <- Taxable YTD
```

Extraction approach:
```python
inc_match = re.search(r'Income Summary(.*?)(?:Margin Loan|Change in|$)', text, re.DOTALL)
# Interest: 4 values after "Interest\n" -> [tax_exempt_period, taxable_period, tax_exempt_ytd, taxable_ytd]
# Cash Dividends: same 4-value pattern
# Total Income: same 4-value pattern
```

Note: `\s+` in regex matches `\n`, so patterns like `Interest\s*\n?([\d,.]+)\s+([\d,.]+)\s+([\d,.]+)\s+([\d,.]+)` work because `\s+` spans the newlines between values.

### Account Value
```python
re.search(r'Ending Account Value\s*\n?\$?([\d,]+\.\d+)', text)
```

---

## Style C: Uppercase Headers with Two-Column Layout

**When you'll see this**: Institutions that use uppercase section headers and show This Period / This Year (or YTD) as two consecutive values after each label.

### Statement Period
Text pattern (uppercase):
```
MARCH 1, 2025 - MARCH 31, 2025\n
ACCOUNT NUMBER: XXXX-XXXX\n
```

Regex:
```python
re.search(r'(\w+)\s+\d+,\s*(\d{4})\s*-\s*(\w+)\s+\d+,\s*(\d{4})', text)
```

### Income Summary
Text layout (two columns: This Period and This Year):
```
Income summary *\n
THIS PERIOD\n
THIS YEAR\n
TAXABLE Money market/sweep funds\n
0.35\n              <- This Period
2.87\n              <- This Year
Ordinary dividends and ST capital gains\n
1,542.17\n          <- This Period
8,730.64\n          <- This Year
Qualified dividends\n
116.83\n
437.59\n
Total taxable income\n
$1,659.35\n
$9,171.10\n
Total federally tax-exempt income\n
$0.00\n
$0.00\n
Total income\n
$1,659.35\n
$9,171.10\n
```

Extraction:
```python
inc_match = re.search(r'Income summary.*?Total income\s+\$?([\d,]+\.\d+)', text, re.DOTALL | re.IGNORECASE)
# Each label followed by two values on separate lines (period, then YTD)
# Use the first value (This Period)
```

### Account Value
```python
re.search(r'Closing value\s+\$?([\d,]+\.\d+)', text)
```

### Progress Summary (deposits/withdrawals)
```
Opening value    $523,814.60    $438,172.35
Cash deposited   0.00           12,500.00
Cash withdrawn   -5,000.00      -15,000.00
Change in value  -2,817.42      87,325.43
Closing value    $515,997.18    $515,997.18
```

---

## Style D: Tabular Fund-Level Distributions

**When you'll see this**: Institutions that list distributions per fund in a clean tabular format, with a summary section for total dividends and capital gains.

### Typical Layout
Statements with this style often use a clean tabular format:
- Account summary with beginning/ending values
- "Dividends and capital gains" section listing each fund's distributions
- Income may be categorized as: Dividends, Short-term capital gains, Long-term capital gains

### Key Fields
```
Account value: Look for "Ending balance" or "Total account value"
Income: Look for "Dividends and capital gains" section, sum all distribution amounts
Period: Usually in header "Statement period: March 1-31, 2025"
```

---

## Style E: Compact Inline Summary

**When you'll see this**: Institutions that present income in a compact format under headings like "Account Summary" or "Income Summary", with categories listed as line items.

### Typical Layout
- Uses "Account Summary" with "Ending Market Value"
- Income under "Income Summary" or "Estimated Income"
- Categories: Interest income, Dividend income, Capital gain distributions, Tax-exempt income

### Variations
Some institutions in this style use:
- "Account Value Summary" as the section header
- "Income & Distributions" as the income section
- Categories: Dividends, Interest, Capital gains

---

## Style F: Detailed Per-Security Breakdown

**When you'll see this**: Institutions that provide highly detailed statements with per-security income and performance data.

### Typical Layout
Detailed statements may include:
- "Mark-to-Market Performance Summary"
- "Dividends" section with per-security detail
- "Interest" section for margin interest and credit interest
- "Withholding Tax" section for foreign dividend taxes

---

## Adding New Institutions

When encountering an unfamiliar institution:

1. **Identify**: Read page 1 to find the institution name and assign a prefix
2. **Sample**: Use `repr(page.get_text())` on 2-3 pages to see exact text layout with `\n` markers
3. **Find income**: Search for keywords: "income", "dividend", "interest", "distribution", "capital gain"
4. **Find account value**: Search for: "ending value", "closing value", "account value", "market value", "total value"
5. **Find period**: Search for: date ranges, "statement period", month names near the top
6. **Build patterns**: Write regex patterns matching the observed layout
7. **Test on all months**: Verify patterns work across all 12 months (format may vary slightly)
8. **Document**: Add the new institution's patterns to this file for future reference

### Pattern Template
```python
# [Institution Name]
# Detection: re.search(r'KEYWORD', text)
# Period: re.search(r'PERIOD_REGEX', text)
# Account value: re.search(r'VALUE_REGEX', text)
# Income section: re.search(r'INCOME_SECTION_REGEX', text, re.DOTALL)
#   - Dividends: re.search(r'DIV_REGEX', income_section)
#   - Interest: re.search(r'INT_REGEX', income_section)
#   - Total: re.search(r'TOTAL_REGEX', income_section)
```
