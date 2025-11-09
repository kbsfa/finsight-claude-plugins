# Data Type Specific Reconciliation

This document provides specific patterns for reconciling different types of data.

## Financial Data

### Bank Reconciliation
**Challenge:** Matching GL entries with bank statements

**Key considerations:**
- Timing differences (checks in transit, deposits not yet cleared)
- Transaction fees may differ
- Multiple GL entries may map to one bank entry

**Python approach:**
```python
# Handle multiple GL entries for one bank transaction
gl_grouped = gl_data.groupby('check_number').agg({
    'amount': 'sum',
    'count': 'count'
}).reset_index()

config = ReconciliationConfig(
    key_columns=['check_number'],
    compare_columns=['amount'],
    tolerance={'amount': 0.01}
)
```

**Gemini use case:**
Analyze unmatched items to identify timing differences vs. errors:
```python
analyzer.analyze_unmatched_records(
    gl_unmatched, 
    bank_unmatched,
    context="GL to Bank reconciliation, possible timing differences"
)
```

### Revenue Recognition
**Challenge:** Comparing invoiced amounts with recognized revenue

**Python approach:**
```python
# Aggregate by period
invoice_monthly = invoices.groupby([
    pd.Grouper(key='invoice_date', freq='M'),
    'customer_id'
]).agg({'amount': 'sum'}).reset_index()

revenue_monthly = revenue.groupby([
    pd.Grouper(key='recognition_date', freq='M'),
    'customer_id'
]).agg({'amount': 'sum'}).reset_index()

# Match by month and customer
```

### Credit Card Reconciliation
**Challenge:** Foreign currency, exchange rates, transaction fees

**Python approach:**
```python
# Standardize to base currency
def convert_to_usd(amount, rate):
    return amount * rate

source['amount_usd'] = source.apply(
    lambda x: convert_to_usd(x['amount'], x['exchange_rate']), 
    axis=1
)

# Allow tolerance for exchange rate fluctuations
config = ReconciliationConfig(
    tolerance={'amount_usd': 0.05}  # 5 cent tolerance
)
```

## Inventory Data

### Physical Count vs. System Records
**Challenge:** Identifying discrepancies between physical inventory and system

**Python approach:**
```python
# Calculate variance
config = ReconciliationConfig(
    key_columns=['item_id', 'location'],
    compare_columns=['quantity', 'unit_value']
)

result = engine.reconcile(physical_count, system_inventory)

# Calculate value impact
result.mismatches['value_difference'] = (
    result.mismatches['physical_quantity'] - 
    result.mismatches['system_quantity']
) * result.mismatches['unit_value']
```

**Gemini use case:**
Identify patterns in discrepancies:
```python
insights = analyzer.analyze_mismatch_patterns(
    result.mismatches,
    context="Physical inventory count vs ERP system. Looking for shrinkage patterns."
)
```

### Multi-location Inventory
**Challenge:** Consolidating inventory across multiple warehouses

**Python approach:**
```python
# Load from multiple locations
all_locations = DataLoader.load_multiple_files(
    'inventory/warehouse_*.csv',
    DataLoader.load_csv
)

# Aggregate by item
consolidated = all_locations.groupby('item_id').agg({
    'quantity': 'sum',
    'value': 'sum'
}).reset_index()

# Compare with central system
```

## Customer/Vendor Data

### Master Data Reconciliation
**Challenge:** Fuzzy matching of customer/vendor names

**Python approach (simple):**
```python
from fuzzywuzzy import fuzz

# Find potential matches with similarity score
for idx, row in source.iterrows():
    target['similarity'] = target['name'].apply(
        lambda x: fuzz.ratio(row['name'], x)
    )
    best_match = target[target['similarity'] >= 85]
```

**Gemini use case (complex):**
Use for intelligent matching with business context:
```python
# Prepare sample data
source_info = {
    'name': 'ERP System',
    'columns': source.columns.tolist(),
    'sample': source.head(10).to_dict('records')
}

target_info = {
    'name': 'CRM System',
    'columns': target.columns.tolist(),
    'sample': target.head(10).to_dict('records')
}

# Get AI recommendation
strategy = analyzer.suggest_reconciliation_strategy(
    source_info, 
    target_info
)
```

### Contact Information Reconciliation
**Challenge:** Phone numbers, emails in different formats

**Python approach:**
```python
import re

def normalize_phone(phone):
    """Extract digits only"""
    if pd.isna(phone):
        return phone
    return re.sub(r'\D', '', str(phone))

def normalize_email(email):
    """Lowercase and strip"""
    if pd.isna(email):
        return email
    return str(email).lower().strip()

source['phone_clean'] = source['phone'].apply(normalize_phone)
source['email_clean'] = source['email'].apply(normalize_email)
```

## Transaction Data

### Payment Reconciliation
**Challenge:** Matching payments across multiple systems with timing differences

**Python approach:**
```python
# Match within date range
source['date_key'] = pd.to_datetime(source['payment_date']).dt.date
target['date_key'] = pd.to_datetime(target['received_date']).dt.date

# For each source payment, find target within ±2 days
import datetime

def find_matching_payments(source_row, target_df, days=2):
    date_min = source_row['date_key'] - datetime.timedelta(days=days)
    date_max = source_row['date_key'] + datetime.timedelta(days=days)
    
    matches = target_df[
        (target_df['date_key'] >= date_min) &
        (target_df['date_key'] <= date_max) &
        (abs(target_df['amount'] - source_row['amount']) <= 0.01)
    ]
    return matches
```

### Order Fulfillment
**Challenge:** Multi-step process with partial fulfillments

**Python approach:**
```python
# Aggregate shipments by order
shipments_agg = shipments.groupby('order_id').agg({
    'quantity_shipped': 'sum',
    'shipment_count': 'count'
}).reset_index()

# Compare with orders
orders_merged = orders.merge(
    shipments_agg, 
    on='order_id', 
    how='left'
)

# Identify partial fulfillments
orders_merged['fulfillment_status'] = orders_merged.apply(
    lambda x: 'Complete' if x['quantity_shipped'] >= x['quantity_ordered']
              else 'Partial' if x['quantity_shipped'] > 0
              else 'Not Shipped',
    axis=1
)
```

## Time-Series Data

### Daily Metrics Reconciliation
**Challenge:** Comparing metrics calculated at different times or with different methods

**Python approach:**
```python
# Ensure same date range
common_start = max(source['date'].min(), target['date'].min())
common_end = min(source['date'].max(), target['date'].max())

source_filtered = source[
    (source['date'] >= common_start) & 
    (source['date'] <= common_end)
]

target_filtered = target[
    (target['date'] >= common_start) & 
    (target['date'] <= common_end)
]

# Configure reconciliation
config = ReconciliationConfig(
    key_columns=['date', 'metric_name'],
    compare_columns=['value']
)
```

### Periodic Snapshots
**Challenge:** Comparing end-of-period balances

**Python approach:**
```python
# Extract period-end dates
source['period_end'] = pd.to_datetime(source['date']) + pd.offsets.MonthEnd(0)
target['period_end'] = pd.to_datetime(target['date']) + pd.offsets.MonthEnd(0)

# Get last record for each period
source_period_end = source.groupby(['account', 'period_end']).last().reset_index()
target_period_end = target.groupby(['account', 'period_end']).last().reset_index()
```

## API Data Reconciliation

### REST API vs. Database
**Challenge:** API response structure differs from database schema

**Python approach:**
```python
# Load from API
api_data = DataLoader.load_from_api(
    'https://api.example.com/transactions',
    headers={'Authorization': f'Bearer {api_token}'},
    params={'start_date': '2024-01-01'}
)

# Flatten nested JSON if needed
from pandas import json_normalize

api_flattened = json_normalize(
    api_data.to_dict('records'),
    sep='_'
)

# Load from database
db_data = DataLoader.load_from_database(
    conn_str,
    "SELECT * FROM transactions WHERE date >= '2024-01-01'"
)

# Map API field names to database field names
field_mapping = {
    'transaction_id': 'id',
    'transaction_amount': 'amount',
    'created_at': 'date'
}

api_flattened = api_flattened.rename(columns=field_mapping)
```

### Paginated API Results
**Challenge:** Ensuring all pages loaded correctly

**Python approach:**
```python
import requests

def load_all_pages(base_url, headers):
    all_data = []
    page = 1
    
    while True:
        response = requests.get(
            base_url,
            headers=headers,
            params={'page': page, 'per_page': 100}
        )
        
        data = response.json()
        if not data or len(data) == 0:
            break
            
        all_data.extend(data)
        page += 1
    
    return pd.DataFrame(all_data)

# Verify total count
api_data = load_all_pages('https://api.example.com/data', headers)
expected_count = 5000  # From API documentation

if len(api_data) != expected_count:
    print(f"Warning: Expected {expected_count}, got {len(api_data)}")
```

## File Format Specific

### CSV with Different Delimiters
**Python approach:**
```python
# Auto-detect delimiter
import csv

def detect_delimiter(file_path):
    with open(file_path, 'r') as f:
        sample = f.read(1024)
        sniffer = csv.Sniffer()
        delimiter = sniffer.sniff(sample).delimiter
    return delimiter

delimiter = detect_delimiter('data.csv')
df = pd.read_csv('data.csv', sep=delimiter)
```

### Excel with Multiple Sheets
**Python approach:**
```python
# Load and reconcile multiple sheets
excel_file = pd.ExcelFile('report.xlsx')

sheets_data = {}
for sheet_name in excel_file.sheet_names:
    sheets_data[sheet_name] = pd.read_excel(excel_file, sheet_name=sheet_name)

# Reconcile summary sheet with detail sheets
summary = sheets_data['Summary']
detail = pd.concat([sheets_data[s] for s in excel_file.sheet_names if s != 'Summary'])

detail_agg = detail.groupby('category').agg({'amount': 'sum'}).reset_index()

# Compare
```

### JSON with Nested Structures
**Python approach:**
```python
from pandas import json_normalize

# Flatten nested JSON
with open('data.json', 'r') as f:
    json_data = json.load(f)

# Flatten with separator
df = json_normalize(json_data, sep='_')

# Or extract specific nested field
df = json_normalize(
    json_data,
    record_path=['items'],
    meta=['order_id', 'customer_id']
)
```

## Large Dataset Strategies

### Incremental Reconciliation
**Python approach:**
```python
# Reconcile only new records since last run
last_reconciliation_date = '2024-10-01'

source_new = source[source['created_date'] > last_reconciliation_date]
target_new = target[target['created_date'] > last_reconciliation_date]

# Reconcile new records only
result = engine.reconcile(source_new, target_new)
```

### Sampling Strategy
**Python approach:**
```python
# Statistical sampling for large datasets
sample_size = 10000
confidence_level = 0.95

# Stratified sampling by category
sample = source.groupby('category', group_keys=False).apply(
    lambda x: x.sample(min(len(x), sample_size // source['category'].nunique()))
)

# Reconcile sample
result = engine.reconcile(sample, target)

# Estimate total discrepancies
estimated_total_mismatches = (
    len(result.mismatches) / len(sample) * len(source)
)
```

### Database-Level Reconciliation
**Python approach:**
```python
# Execute aggregation in database for performance
query = """
SELECT 
    DATE_TRUNC('day', transaction_date) as date,
    account_id,
    SUM(amount) as total_amount,
    COUNT(*) as transaction_count
FROM transactions
WHERE transaction_date >= '2024-01-01'
GROUP BY DATE_TRUNC('day', transaction_date), account_id
"""

source_agg = DataLoader.load_from_database(conn_str, query)

# Now reconcile aggregated data (much smaller)
```
