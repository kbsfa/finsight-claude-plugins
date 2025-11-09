# Reconciliation Strategies Reference

This document provides guidance on choosing and implementing reconciliation strategies for different scenarios.

## Strategy Selection Guide

### One-to-One Matching (Standard)
**Use when:** Each record in source should match exactly one record in target

**Key columns:** Unique identifier (ID, reference number, etc.)

**Example scenarios:**
- Database table synchronization
- File transfer validation
- Invoice matching between systems

**Python approach:**
```python
config = ReconciliationConfig(
    source_name="system_a",
    target_name="system_b",
    key_columns=["transaction_id"],
    compare_columns=["amount", "status", "date"]
)
```

### Composite Key Matching
**Use when:** No single unique identifier exists; multiple columns form a unique key

**Key columns:** Combination of 2+ columns that together are unique

**Example scenarios:**
- Customer + Date combinations
- Product + Location + Period
- Account + Transaction Type

**Python approach:**
```python
config = ReconciliationConfig(
    source_name="sales_db",
    target_name="reporting_db",
    key_columns=["customer_id", "order_date", "product_code"],
    compare_columns=["quantity", "price", "total"]
)
```

### Fuzzy Matching
**Use when:** Exact matches aren't possible due to data quality issues

**Techniques:**
- String similarity (Levenshtein distance)
- Phonetic matching (Soundex, Metaphone)
- Token-based matching

**When to use Gemini:** For semantic understanding of similar but not identical text

**Python approach (for simple cases):**
```python
from fuzzywuzzy import fuzz

def fuzzy_key_match(s1, s2, threshold=85):
    return fuzz.ratio(s1, s2) >= threshold
```

**Gemini approach (for complex cases):**
Use `GeminiReconciliationAnalyzer.suggest_reconciliation_strategy()` to get AI-powered matching recommendations

### Time-Based Reconciliation
**Use when:** Records represent the same entity at different points in time

**Strategies:**
- Same-day matching
- Within tolerance window (±N hours/days)
- End-of-period snapshots

**Python approach:**
```python
import pandas as pd

# Match within 24 hours
source['match_date'] = pd.to_datetime(source['timestamp']).dt.date
target['match_date'] = pd.to_datetime(target['timestamp']).dt.date

# Use match_date as key column
```

### Aggregated Reconciliation
**Use when:** One system has detail records, another has aggregates

**Approach:**
1. Aggregate the detail-level data
2. Compare aggregated totals
3. Drill down into discrepancies

**Python approach:**
```python
# Aggregate source to match target granularity
source_agg = source.groupby(['account', 'date']).agg({
    'amount': 'sum',
    'count': 'count'
}).reset_index()

# Now reconcile aggregated data
```

### Many-to-One Matching
**Use when:** Multiple source records correspond to one target record

**Example scenarios:**
- Payment splits mapping to single invoice
- Multiple shipments for one order
- Partial payments to full transaction

**Python approach:**
```python
# Group source records by target key
source_grouped = source.groupby('invoice_id').agg({
    'payment_amount': 'sum',
    'payment_count': 'count'
}).reset_index()

# Compare grouped source with target
```

## Tolerance Handling

### Numeric Tolerances
**Use when:** Small differences are acceptable due to rounding or calculation methods

**Example scenarios:**
- Currency conversions (±0.01)
- Percentage calculations (±0.001%)
- Quantity with decimals (±0.01 units)

**Python approach:**
```python
config = ReconciliationConfig(
    # ...
    tolerance={
        'amount': 0.01,  # ±1 cent
        'quantity': 0.01,  # ±0.01 units
        'percentage': 0.0001  # ±0.01%
    }
)
```

### Date Tolerances
**Use when:** Timestamps may differ slightly between systems

**Python approach:**
```python
# Compare dates only (ignore time)
source['date_only'] = pd.to_datetime(source['timestamp']).dt.date
target['date_only'] = pd.to_datetime(target['timestamp']).dt.date

# Or use date within tolerance
import numpy as np

def dates_within_tolerance(date1, date2, days=1):
    return abs((date1 - date2).days) <= days
```

## Common Data Quality Issues

### Issue: Case Sensitivity
**Solution:** Normalize to lowercase before comparison
```python
config = ReconciliationConfig(ignore_case=True)
```

### Issue: Whitespace
**Solution:** Trim whitespace
```python
config = ReconciliationConfig(trim_whitespace=True)
```

### Issue: Date Format Differences
**Solution:** Standardize date format
```python
from data_loader import DataTransformer

source = DataTransformer.standardize_dates(source, ['date_col'])
target = DataTransformer.standardize_dates(target, ['date_col'])
```

### Issue: Null/Missing Values
**Python approach:**
- Define how nulls should be handled
- Consider null == null as match or mismatch

**Gemini approach:**
Use `GeminiReconciliationAnalyzer.analyze_mismatch_patterns()` to understand systematic null patterns

### Issue: Encoding Problems
**Solution:** Specify correct encoding
```python
source = DataLoader.load_csv('file.csv', encoding='latin1')
```

## When to Use Python vs. Gemini

### Use Python for:
- Standard data loading and transformation
- Numeric comparisons with tolerances
- Statistical analysis
- Automated matching logic
- Performance-critical operations
- Batch processing large datasets

### Use Gemini for:
- Understanding business context of mismatches
- Identifying patterns in discrepancies
- Explaining complex differences to stakeholders
- Recommending reconciliation strategies for new projects
- Semantic analysis of text fields
- Anomaly detection requiring business logic understanding
- Root cause analysis of systematic issues

## Performance Optimization

### Large Datasets
**Strategy 1: Sample first**
```python
# Reconcile a sample first for quick validation
sample_source = source.sample(n=10000, random_state=42)
sample_target = target.sample(n=10000, random_state=42)
```

**Strategy 2: Batch processing**
```python
# Process in chunks
chunk_size = 100000
for i in range(0, len(source), chunk_size):
    chunk = source.iloc[i:i+chunk_size]
    # Process chunk
```

**Strategy 3: Use efficient data types**
```python
# Convert to categorical for repeated strings
df['category_col'] = df['category_col'].astype('category')
```

### Memory Optimization
```python
# Load only needed columns
source = DataLoader.load_csv('file.csv', usecols=['id', 'amount', 'date'])

# Use appropriate data types
dtypes = {
    'id': 'int32',
    'amount': 'float32',
    'status': 'category'
}
source = DataLoader.load_csv('file.csv', dtype=dtypes)
```

## Example Workflows

### Financial Reconciliation
```python
# 1. Load data
source = DataLoader.load_from_database(conn_str, "SELECT * FROM gl_transactions")
target = DataLoader.load_csv("bank_statement.csv")

# 2. Transform
source = DataTransformer.standardize_numeric(source, ['amount'], 2)
source = DataTransformer.standardize_dates(source, ['date'])

# 3. Configure reconciliation
config = ReconciliationConfig(
    source_name="general_ledger",
    target_name="bank",
    key_columns=["reference_number"],
    compare_columns=["amount", "date"],
    tolerance={'amount': 0.01}
)

# 4. Reconcile
engine = ReconciliationEngine(config)
result = engine.reconcile(source, target)

# 5. Analyze with Gemini if needed
if len(result.mismatches) > 0:
    analyzer = GeminiReconciliationAnalyzer()
    insights = analyzer.analyze_mismatch_patterns(
        result.mismatches,
        context="GL to Bank reconciliation"
    )
```

### Inventory Reconciliation
```python
# Multiple location files
source = DataLoader.load_multiple_files(
    'inventory/location_*.xlsx',
    DataLoader.load_excel
)

# Aggregate by product
source_agg = source.groupby('product_id').agg({
    'quantity': 'sum',
    'value': 'sum'
}).reset_index()

# Compare with ERP system
target = DataLoader.load_from_database(conn_str, "SELECT * FROM inventory_master")

# Reconcile
config = ReconciliationConfig(
    key_columns=['product_id'],
    compare_columns=['quantity', 'value'],
    tolerance={'value': 0.01}
)
```
