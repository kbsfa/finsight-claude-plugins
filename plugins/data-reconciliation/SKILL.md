---
name: data-reconciliation
description: Comprehensive data reconciliation toolkit for comparing and validating datasets from any source (CSV, Excel, databases, APIs). Uses Python for efficient data processing and Gemini AI for intelligent analysis, pattern detection, and insights. Use when reconciling financial data, inventory, transactions, master data, or any datasets requiring comparison and discrepancy identification.
---

# Data Reconciliation Skill

Reconcile and validate data across any sources using Python for processing and Gemini AI for intelligent analysis.

## Quick Start

Reconcile two datasets in 3 steps:

1. **Load data** using `data_loader.py`
2. **Configure and reconcile** using `reconcile_engine.py`
3. **Analyze results** with `gemini_analyzer.py` (optional, for AI insights)

## Reconciliation Workflow

Follow this process for any reconciliation task:

**Step 1: Understand the requirements**
- What are the source and target systems?
- What columns should match (key columns)?
- What columns should be compared (compare columns)?
- Are there tolerance requirements for numeric fields?
- Are there data quality considerations (case sensitivity, whitespace, date formats)?

**Step 2: Load and transform data**

Use `scripts/data_loader.py` for loading from various sources:
```python
from data_loader import DataLoader, DataTransformer

# Load from CSV, Excel, JSON, Database, or API
source = DataLoader.load_csv('source.csv')
target = DataLoader.load_from_database(conn_str, "SELECT * FROM target_table")

# Transform as needed
source = DataTransformer.standardize_dates(source, ['date_column'])
source = DataTransformer.standardize_numeric(source, ['amount'], decimal_places=2)
```

**Step 3: Configure reconciliation**

Use `scripts/reconcile_engine.py`:
```python
from reconcile_engine import ReconciliationEngine, ReconciliationConfig

config = ReconciliationConfig(
    source_name="system_a",
    target_name="system_b",
    key_columns=["id"],  # Columns that uniquely identify records
    compare_columns=["amount", "status"],  # Columns to compare for differences
    tolerance={"amount": 0.01},  # Optional: numeric tolerances
    ignore_case=True,  # Optional: case-insensitive string comparison
    trim_whitespace=True  # Optional: trim whitespace before comparison
)
```

**Step 4: Execute reconciliation**
```python
engine = ReconciliationEngine(config)
result = engine.reconcile(source, target)

# Export results
engine.export_results(result, "reconciliation_output")
```

**Step 5: Analyze results (use Gemini when needed)**

The reconciliation produces three key outputs:
- **Matched records**: Records that exist in both systems with matching values
- **Unmatched records**: Records that exist in only one system
- **Mismatches**: Records that exist in both but have different values

Review the summary:
```python
import json
print(json.dumps(result.summary, indent=2))
```

**Step 6: Use Gemini for intelligent analysis** (optional, when Python analysis isn't sufficient)

Use `scripts/gemini_analyzer.py` for AI-powered insights:

```python
from gemini_analyzer import GeminiReconciliationAnalyzer
import os

# Set API key
os.environ['GEMINI_API_KEY'] = 'your-api-key'

analyzer = GeminiReconciliationAnalyzer()

# Analyze patterns in mismatches
insights = analyzer.analyze_mismatch_patterns(
    result.mismatches,
    context="Financial reconciliation between GL and bank statements"
)

# Analyze unmatched records
unmatched_insights = analyzer.analyze_unmatched_records(
    result.unmatched_source,
    result.unmatched_target,
    context="Looking for timing differences vs data errors"
)

# Get reconciliation strategy recommendations
strategy = analyzer.suggest_reconciliation_strategy(source_info, target_info)
```

## When to Use Python vs. Gemini

### Maximize Python for:
- Loading data from any source (CSV, Excel, JSON, databases, APIs)
- Data transformations (cleaning, normalization, aggregation)
- Exact matching and comparison logic
- Numeric calculations and tolerances
- Statistical analysis
- Batch processing and performance-critical operations
- Generating structured output files

### Use Gemini when Python alone is insufficient:
- **Pattern detection**: Identifying business patterns in mismatches that require semantic understanding
- **Root cause analysis**: Understanding why discrepancies occur from a business perspective
- **Strategy recommendations**: Determining optimal reconciliation approach for new/complex datasets
- **Anomaly explanation**: Explaining unusual values in business terms
- **Stakeholder communication**: Translating technical discrepancies into business language
- **Semantic matching**: Fuzzy matching that requires contextual understanding

## Core Scripts

### `reconcile_engine.py`
Core reconciliation engine. Handles:
- Data normalization (case, whitespace, dates)
- Composite key generation
- Value comparison with tolerance handling
- Mismatch identification
- Result summarization and export

### `data_loader.py`
Universal data loader supporting:
- CSV/TSV files
- Excel spreadsheets (single or multiple sheets)
- JSON files
- Parquet files
- SQL databases (PostgreSQL, MySQL, SQL Server, SQLite)
- REST APIs
- Multiple files with pattern matching
- Auto-detection of file types

Also includes `DataTransformer` for common transformations:
- Deduplication
- Date standardization
- Numeric standardization
- Value mapping
- Date range filtering

### `gemini_analyzer.py`
AI-powered analysis using Gemini. Provides:
- `analyze_mismatch_patterns()`: Pattern detection in discrepancies
- `analyze_unmatched_records()`: Business insights on unmatched data
- `suggest_reconciliation_strategy()`: Strategy recommendations for new projects
- `explain_discrepancy()`: Explain specific differences in business terms
- `detect_anomalies()`: Semantic anomaly detection

Requires: `GEMINI_API_KEY` environment variable

## Reference Documentation

### `reconciliation_strategies.md`
Comprehensive guide on choosing reconciliation strategies:
- One-to-one matching
- Composite key matching
- Fuzzy matching
- Time-based reconciliation
- Aggregated reconciliation
- Many-to-one matching
- Tolerance handling
- Data quality issue resolution
- Performance optimization

**Read this when:**
- Starting a new reconciliation project
- Need to choose the right matching strategy
- Dealing with data quality issues
- Optimizing performance for large datasets

### `data_type_patterns.md`
Specific patterns for different data types:
- Financial data (bank reconciliation, revenue recognition, credit cards)
- Inventory data (physical counts, multi-location)
- Customer/vendor master data
- Transaction data (payments, orders)
- Time-series data
- API data reconciliation
- File format specific handling
- Large dataset strategies

**Read this when:**
- Working with specific data types (financial, inventory, etc.)
- Need examples for your use case
- Dealing with format-specific challenges
- Handling large datasets

## Common Patterns

### Pattern 1: Simple CSV to CSV Reconciliation
```python
from data_loader import DataLoader
from reconcile_engine import ReconciliationEngine, ReconciliationConfig

# Load
source = DataLoader.load_csv('file1.csv')
target = DataLoader.load_csv('file2.csv')

# Configure
config = ReconciliationConfig(
    source_name="file1",
    target_name="file2",
    key_columns=["id"],
    compare_columns=["value1", "value2"]
)

# Reconcile
engine = ReconciliationEngine(config)
result = engine.reconcile(source, target)
engine.export_results(result, "output")
```

### Pattern 2: Database to API Reconciliation with Gemini Analysis
```python
from data_loader import DataLoader
from reconcile_engine import ReconciliationEngine, ReconciliationConfig
from gemini_analyzer import GeminiReconciliationAnalyzer

# Load from database
source = DataLoader.load_from_database(
    'postgresql://user:pass@host/db',
    'SELECT * FROM transactions WHERE date >= CURRENT_DATE - 7'
)

# Load from API
target = DataLoader.load_from_api(
    'https://api.example.com/transactions',
    headers={'Authorization': 'Bearer token'},
    params={'start_date': '2024-10-23'}
)

# Configure and reconcile
config = ReconciliationConfig(
    source_name="database",
    target_name="api",
    key_columns=["transaction_id"],
    compare_columns=["amount", "status"]
)

engine = ReconciliationEngine(config)
result = engine.reconcile(source, target)

# Use Gemini for intelligent analysis if there are mismatches
if len(result.mismatches) > 0:
    analyzer = GeminiReconciliationAnalyzer()
    insights = analyzer.analyze_mismatch_patterns(
        result.mismatches,
        context="Database vs API transaction reconciliation"
    )
    print(json.dumps(insights, indent=2))
```

### Pattern 3: Multi-file Aggregation and Reconciliation
```python
from data_loader import DataLoader, DataTransformer

# Load multiple files
source = DataLoader.load_multiple_files('data/*.csv', DataLoader.load_csv)

# Aggregate
source_agg = source.groupby(['date', 'category']).agg({
    'amount': 'sum',
    'count': 'count'
}).reset_index()

# Load target
target = DataLoader.load_excel('summary.xlsx')

# Reconcile aggregated data
config = ReconciliationConfig(
    key_columns=['date', 'category'],
    compare_columns=['amount', 'count']
)

engine = ReconciliationEngine(config)
result = engine.reconcile(source_agg, target)
```

### Pattern 4: Complex Reconciliation with Strategy Recommendation
```python
from gemini_analyzer import GeminiReconciliationAnalyzer

# Use Gemini to recommend strategy for unfamiliar data
analyzer = GeminiReconciliationAnalyzer()

source_info = {
    'name': 'Legacy System',
    'columns': source.columns.tolist(),
    'record_count': len(source),
    'sample': source.head(10).to_dict('records')
}

target_info = {
    'name': 'New System',
    'columns': target.columns.tolist(),
    'record_count': len(target),
    'sample': target.head(10).to_dict('records')
}

# Get AI-powered strategy
strategy = analyzer.suggest_reconciliation_strategy(source_info, target_info)

# Implement the recommended strategy
config = ReconciliationConfig(
    key_columns=strategy['key_columns'],
    compare_columns=strategy['compare_columns'],
    # Apply other recommendations
)
```

## Required Dependencies

Install required Python packages:
```bash
pip install pandas numpy sqlalchemy google-generativeai requests openpyxl pyarrow
```

For database-specific drivers:
```bash
# PostgreSQL
pip install psycopg2-binary

# MySQL
pip install pymysql

# SQL Server
pip install pyodbc
```

## Tips for Success

1. **Start with strategy**: Use Gemini's `suggest_reconciliation_strategy()` for new or complex reconciliation projects
2. **Transform first**: Clean and standardize data before reconciliation for better results
3. **Use appropriate tolerances**: Set realistic tolerances for numeric comparisons
4. **Sample large datasets**: Test with samples first before processing millions of records
5. **Leverage Gemini for insights**: Use AI analysis when patterns aren't obvious
6. **Export results**: Always export results for audit trail and further analysis
7. **Iterate**: Refine your reconciliation config based on initial results
