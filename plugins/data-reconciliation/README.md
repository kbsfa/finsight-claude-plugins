# Data Reconciliation Skill Plugin

An intelligent data reconciliation toolkit for Claude Code that automatically analyzes datasets, detects data quality issues, and suggests optimal reconciliation strategies.

## Features

### 🤖 AI-Powered Intelligence
- **Automatic Strategy Detection**: Analyzes your data and recommends the best reconciliation approach
- **Smart Key Detection**: Automatically identifies unique keys and composite keys
- **Data Type Inference**: Understands semantic types (IDs, amounts, dates, categories)
- **Quality Scoring**: Rates data quality and identifies issues proactively

### 🔍 Comprehensive Analysis
- **Data Profiling**: Deep analysis of structure, types, and patterns
- **Quality Issues Detection**: Finds nulls, duplicates, whitespace, case issues, outliers
- **Transformation Recommendations**: Suggests data cleaning steps
- **Confidence Scoring**: Tells you how confident the strategy is

### 💪 Powerful Reconciliation
- **Multi-Source Support**: CSV, Excel, databases (PostgreSQL, MySQL, SQL Server), APIs, JSON, Parquet
- **Flexible Matching**: Single keys, composite keys, fuzzy matching, time-based
- **Tolerance Handling**: Numeric tolerances for amounts, dates, percentages
- **Progress Tracking**: Real-time progress bars for large datasets

### 📊 Rich Reporting
- **Multiple Export Formats**: CSV, Excel with multiple sheets, JSON
- **Visual Dashboards**: Interactive HTML dashboards and static charts
- **Detailed Metrics**: Match rates, accuracy rates, processing times
- **Issue Tracking**: Comprehensive logging of all discrepancies

### 🧠 Claude AI Integration (Automatic in Claude Code)
- **Conversational Pattern Detection**: Ask Claude to identify business patterns in mismatches
- **Interactive Root Cause Analysis**: Claude explains why discrepancies occur in plain language
- **Real-time Anomaly Explanation**: Get instant explanations for unusual values
- **Stakeholder-Ready Communication**: Claude translates technical issues to business language
- **No API Keys Required**: Works automatically when using the skill through Claude Code

## Installation as Claude Code Plugin

### Method 1: Via Claude Code Plugin Manager (Recommended)

```bash
# In Claude Code, use the command:
/install-plugin data-reconciliation
```

### Method 2: Manual Installation

1. Clone or download this repository
2. Place the `data-reconciliation` folder in `.claude/skills/`
3. Install Python dependencies:

```bash
cd .claude/skills/data-reconciliation
pip install -r requirements.txt
```

4. Verify installation:
```bash
python scripts/reconcile_cli.py version
```

## Quick Start

### Using with Claude Code

Simply invoke the skill in your conversation:

```
/skill data-reconciliation
```

Then describe your reconciliation task:
```
I need to reconcile sales_data.csv with erp_extract.xlsx
```

Claude will automatically:
1. Load and analyze both datasets
2. Profile the data structure and quality
3. Recommend the best reconciliation strategy
4. Execute the reconciliation
5. Generate reports and visualizations

### Using the CLI Directly

#### Auto Mode (Recommended)
```bash
python scripts/reconcile_cli.py reconcile source.csv target.csv --auto --visualize
```

#### Manual Mode
```bash
python scripts/reconcile_cli.py reconcile source.csv target.csv \
  -k transaction_id \
  -c amount -c status -c date \
  --output results/ \
  --format both \
  --visualize
```

#### Profile a Dataset
```bash
python scripts/reconcile_cli.py profile data.csv --detailed
```

## Usage Examples

### Example 1: Simple CSV Reconciliation
```python
from data_loader import DataLoader
from data_profiler import IntelligentDataProfiler
from reconcile_engine import ReconciliationEngine, ReconciliationConfig

# Load data
source = DataLoader.load_csv('source.csv')
target = DataLoader.load_csv('target.csv')

# Auto-detect strategy
profiler = IntelligentDataProfiler()
source_profile = profiler.profile_dataset(source, "Source")
target_profile = profiler.profile_dataset(target, "Target")
strategy = profiler.suggest_reconciliation_strategy(source_profile, target_profile)

# Create config from strategy
config = ReconciliationConfig(
    source_name="source",
    target_name="target",
    key_columns=strategy['recommended_key_columns'],
    compare_columns=strategy['recommended_compare_columns'],
    tolerance=strategy['recommended_tolerance']
)

# Reconcile
engine = ReconciliationEngine(config)
result = engine.reconcile(source, target)

# Export
engine.export_results(result, "output/", format='both')
```

### Example 2: Database to API Reconciliation
```python
from data_loader import DataLoader

# Load from database
db_data = DataLoader.load_from_database(
    'postgresql://user:pass@localhost/db',
    'SELECT * FROM transactions WHERE date >= CURRENT_DATE - 7'
)

# Load from API
api_data = DataLoader.load_from_api(
    'https://api.example.com/transactions',
    headers={'Authorization': 'Bearer token'},
    params={'start_date': '2024-01-01'}
)

# Use intelligent profiler to auto-reconcile
# ... (same as Example 1)
```

### Example 3: With Gemini AI Analysis
```python
from gemini_analyzer import GeminiReconciliationAnalyzer
import os

# After reconciliation
if len(result.mismatches) > 0:
    os.environ['GEMINI_API_KEY'] = 'your-key'
    analyzer = GeminiReconciliationAnalyzer()

    insights = analyzer.analyze_mismatch_patterns(
        result.mismatches,
        context="Financial reconciliation between GL and bank"
    )

    print(insights)
```

## What Makes This Special?

### Traditional Reconciliation Tools
- Manual configuration required
- No data quality analysis
- Fixed matching logic
- Limited insights

### This Skill
- ✅ **Automatic configuration** - analyzes data and suggests strategy
- ✅ **Proactive quality detection** - finds issues before reconciliation
- ✅ **Intelligent matching** - adapts to your data structure
- ✅ **AI-powered insights** - understands business context

## Use Cases

### Financial Data
- Bank reconciliation
- GL to sub-ledger matching
- Payment reconciliation
- Revenue recognition
- Credit card reconciliation

### Inventory & Operations
- Physical count vs system records
- Multi-location inventory
- Order fulfillment tracking
- Shipment reconciliation

### Master Data
- Customer/vendor deduplication
- Contact information matching
- Cross-system data validation

### Transaction Data
- API vs database sync
- Multi-system transaction matching
- Time-series data validation

## Architecture

```
data-reconciliation/
├── SKILL.md                 # Skill definition for Claude Code
├── plugin.json              # Plugin metadata
├── requirements.txt         # Python dependencies
├── scripts/
│   ├── data_loader.py       # Multi-source data loading
│   ├── data_profiler.py     # Intelligent data analysis ⭐ NEW
│   ├── reconcile_engine.py  # Core reconciliation logic (enhanced)
│   ├── gemini_analyzer.py   # AI-powered analysis
│   ├── visualizer.py        # Visualization module ⭐ NEW
│   └── reconcile_cli.py     # CLI interface ⭐ NEW
├── references/
│   ├── reconciliation_strategies.md
│   └── data_type_patterns.md
└── examples/
    └── sample_reconciliation.py
```

## Configuration

### Environment Variables
```bash
# For Gemini AI features
export GEMINI_API_KEY=your-api-key

# For database connections
export DB_CONNECTION_STRING=postgresql://user:pass@host/db
```

### Claude Code Settings
Add to your `.claude/settings.json`:
```json
{
  "skills": {
    "data-reconciliation": {
      "auto_profile": true,
      "default_output_format": "both",
      "enable_visualization": true,
      "gemini_api_key": "${GEMINI_API_KEY}"
    }
  }
}
```

## Contributing

To enhance this plugin:

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Test thoroughly
5. Submit a pull request

## Roadmap

- [ ] Web UI for reconciliation
- [ ] Real-time reconciliation monitoring
- [ ] Scheduled reconciliation jobs
- [ ] Machine learning-based fuzzy matching
- [ ] Integration with more data sources
- [ ] Reconciliation templates library

## License

MIT License - see LICENSE file for details

## Support

- Documentation: See `SKILL.md` and `references/`
- Issues: GitHub Issues
- Examples: See `examples/` directory

## Version History

### 2.0.0 (Current)
- ⭐ Added intelligent data profiler with auto-strategy detection
- ⭐ Added comprehensive visualization module
- ⭐ Added CLI interface
- Enhanced error handling and logging
- Progress tracking for large datasets
- Excel export with formatted reports
- Improved data quality detection

### 1.0.0 (Original)
- Basic reconciliation engine
- Multi-source data loading
- Gemini AI integration
- Reference documentation
