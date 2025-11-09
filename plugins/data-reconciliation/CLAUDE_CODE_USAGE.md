# Using Data Reconciliation Skill with Claude Code

This guide shows how to use the data reconciliation skill through Claude Code, leveraging Claude's AI intelligence directly.

## Quick Start

### Step 1: Activate the Skill

```bash
/skill data-reconciliation
```

### Step 2: Describe Your Task

Simply tell Claude what you need in natural language:

```
"I need to reconcile sales_jan.csv with erp_jan.xlsx"
```

## What Happens Automatically

### 1. Data Loading & Profiling

Claude will automatically:
- Load both files using the appropriate data loader
- Run the intelligent data profiler
- Analyze data structure, types, and quality
- Detect potential issues proactively

**You see:**
```
✓ Loaded 5,234 source records from sales_jan.csv
✓ Loaded 5,190 target records from erp_jan.xlsx

Analyzing data structure...
✓ Source quality score: 88/100
✓ Target quality score: 92/100

Issues detected:
⚠ Whitespace in customer_name (45 records in source)
⚠ 15% null values in notes column (target)
```

### 2. Strategy Recommendation

Claude analyzes and recommends the best approach:

```
Recommended Reconciliation Strategy:
- Key columns: transaction_id (99.8% unique)
- Compare columns: amount, customer_name, order_date, status
- Tolerance: 0.01 for amount (financial data detected)
- Confidence: 95%

Shall I proceed with this strategy?
```

### 3. Interactive Confirmation

You can:
- Accept the recommendation: "Yes, proceed"
- Modify the approach: "Use composite key of customer_id + date instead"
- Ask questions: "Why did you choose transaction_id?"

### 4. Execution with Progress

Claude runs the reconciliation with real-time updates:

```
Executing reconciliation...
[Progress] ████████████████████ 100% 5,190/5,190

Results:
✓ Match rate: 97.8%
✓ 5,120 perfectly matched
✓ 70 unmatched in sales
✓ 114 mismatches found
```

### 5. Intelligent Analysis

Claude automatically analyzes the results:

```
I've analyzed the reconciliation results. Here's what I found:

Mismatch Analysis:
1. Amount Discrepancies (82% of mismatches)
   - Pattern: Source has 2 decimals, target rounds to integers
   - Total variance: $45.23
   - Business impact: Low - rounding differences only
   - Recommendation: Apply 0.01 tolerance in config

2. Timing Issues (12% of mismatches)
   - Pattern: End-of-month vs start-of-month dating
   - Count: 18 transactions
   - Business impact: Medium - affects period reporting
   - Recommendation: Investigate batch processing timing

3. Data Entry Errors (6% of mismatches)
   - Pattern: Customer name typos
   - Count: 9 records
   - Business impact: Low - doesn't affect amounts
   - Recommendation: Implement data validation

Would you like me to:
- Generate detailed visualizations?
- Export results to Excel?
- Investigate specific mismatches?
- Create a summary report for stakeholders?
```

## Advanced Usage Examples

### Example 1: Database to CSV Reconciliation

```
You: /skill data-reconciliation

You: Reconcile the transactions table from PostgreSQL with the CSV export

Claude: I'll help you with that. First, I need the database connection details.
What's your PostgreSQL connection string?

You: postgresql://user:pass@localhost:5432/mydb

Claude: Got it. And the CSV file path?

You: exports/transactions_export.csv

Claude:
[Loads from database: 10,523 records]
[Loads from CSV: 10,500 records]

Analyzing... The database has 23 more records than the CSV.

Database columns: id, amount, customer_id, date, status, created_at
CSV columns: transaction_id, total, customer, date, state

I notice the column names differ. Here's my mapping suggestion:
- id → transaction_id
- amount → total
- customer_id → customer
- status → state

Should I proceed with this mapping?
```

### Example 2: Complex Multi-Source Reconciliation

```
You: I need to reconcile data from 3 sources:
- sales.csv
- erp_extract.xlsx
- api data from https://api.example.com/transactions

Claude: I'll reconcile all three sources. Let me start by profiling each:

[Loads and profiles all 3 sources]

Analysis:
- Sales: 5,234 records, quality 88%
- ERP: 5,190 records, quality 92%
- API: 5,245 records, quality 94%

Common key found: transaction_id (present in all 3)

Reconciliation approach:
1. First reconcile Sales ↔ ERP
2. Then reconcile combined result ↔ API
3. Identify which source is authoritative for each discrepancy

Proceeding...

[Executes 3-way reconciliation]

Results:
- Perfect 3-way match: 4,987 records (95.2%)
- In Sales & ERP only: 203 records
- In Sales & API only: 247 records
- In ERP & API only: 3 records
- In Sales only: 44 records
- Unique to each source...

Pattern detected: API is most up-to-date (newest records)
Recommendation: Use API as authoritative source
```

### Example 3: Iterative Refinement

```
You: The match rate is only 75%, that's too low

Claude: You're right. Let me investigate why the match rate is low.

[Analyzes unmatched records]

I found the issue - there are data quality problems:

1. Leading/trailing whitespace in customer_id (source)
2. Date format mismatch (source: MM/DD/YYYY, target: YYYY-MM-DD)
3. Case sensitivity in status field

Let me clean the data and re-run:

[Applies transformations]
[Re-runs reconciliation]

New results:
✓ Match rate: 96.8% (up from 75%)
✓ 4,840 matched (was 3,750)

Much better! The transformations fixed most issues.
Remaining 3.2% are legitimate differences.
```

## Conversational Commands

### Ask for Analysis
```
"What patterns do you see in the mismatches?"
"Why are these records unmatched?"
"What's causing the amount discrepancies?"
"Analyze the unmatched records"
```

### Request Actions
```
"Export to Excel with all details"
"Create a visualization dashboard"
"Generate a summary report for management"
"Show me the top 10 largest discrepancies"
```

### Refine Approach
```
"Use customer_id + date as composite key instead"
"Apply 0.05 tolerance to all amount fields"
"Ignore the notes column in comparison"
"Re-run with case-insensitive matching"
```

### Get Recommendations
```
"What should I do about these mismatches?"
"Recommend next steps"
"How do I prevent this in the future?"
"What's the business impact?"
```

## No Gemini API Key Needed!

When using this skill through Claude Code:

❌ **Don't need:**
- Gemini API key
- `gemini_analyzer.py` imports
- Separate AI calls

✅ **Claude provides:**
- Real-time pattern analysis
- Conversational interaction
- Business context understanding
- Iterative refinement
- Stakeholder-ready explanations

## Tips for Best Results

1. **Be Specific**: Provide context about your data
   - "This is financial data from our GL system"
   - "These are inventory counts, need exact matching"

2. **Ask Questions**: Claude can explain its reasoning
   - "Why did you choose that key?"
   - "What makes you confident in this strategy?"

3. **Iterate**: Refine based on results
   - "The match rate is low, investigate why"
   - "These mismatches look like rounding, confirm"

4. **Request Explanations**: Get business insights
   - "Explain these discrepancies in simple terms"
   - "What should I tell my manager about this?"

5. **Leverage Visualizations**: Make results clear
   - "Create a dashboard showing the breakdown"
   - "Generate charts for the presentation"

## Comparison: Claude Code vs Standalone

| Feature | With Claude Code | Standalone Python |
|---------|------------------|-------------------|
| AI Analysis | ✅ Automatic (Claude) | ⚠️ Optional (Gemini) |
| Interaction | ✅ Conversational | ❌ Code-only |
| Setup | ✅ No API keys | ⚠️ Need Gemini key |
| Refinement | ✅ Interactive | ❌ Manual re-run |
| Explanations | ✅ Natural language | ⚠️ JSON output |
| Context | ✅ Full conversation | ❌ Per-call only |

**Recommendation**: Use through Claude Code for the best experience!

## Getting Help

If you encounter issues:

```
"I'm getting an error: [paste error]"
"The results don't look right"
"How do I handle [specific scenario]?"
"Show me an example of [use case]"
```

Claude will help debug and guide you through solutions!
