# Finsight Claude Code Plugins

Professional data analytics plugins for Claude Code by Finsight Analytics LLP.

## Available Plugins

### 🔄 Data Reconciliation (v2.0.0)

Intelligent data reconciliation toolkit with:
- **AI-powered strategy detection**: Automatically determines the best reconciliation approach
- **Automatic key column detection**: Finds unique identifiers in your data
- **Data quality profiling**: Proactively detects issues before reconciliation
- **Interactive visualizations**: HTML dashboards and charts
- **Multi-source support**: CSV, Excel, databases (PostgreSQL, MySQL, SQL Server), REST APIs, JSON, Parquet

**Installation:**

```bash
# Add this marketplace
/plugin marketplace add kbsfa/finsight-claude-plugins

# Install the plugin
/plugin install data-reconciliation@finsight-plugins
```

**Quick Start:**

```bash
# Use the skill
/skill data-reconciliation

# Then tell Claude what you need:
"Reconcile sales_jan.csv with erp_jan.xlsx"
```

**Features:**

- ✅ Context-aware: Analyzes data structure before reconciliation
- ✅ Universal: Works with any data format automatically
- ✅ Intelligent: Detects keys, types, and quality issues
- ✅ Production-ready: Logging, error handling, progress tracking
- ✅ Professional: Excel reports, visualizations, dashboards

## Documentation

- [Complete Documentation](./plugins/data-reconciliation/README.md)
- [Plugin Guide](./plugins/data-reconciliation/PLUGIN_GUIDE.md)
- [How to Publish](./plugins/data-reconciliation/HOW_TO_PUBLISH.md)
- [Requirements & Implementation](./plugins/data-reconciliation/REQUIREMENTS_AND_IMPLEMENTATION.md)

## License

MIT License - See individual plugin directories for details.

## Support

For issues or questions:
- GitHub Issues: https://github.com/kbsfa/finsight-claude-plugins/issues
- Email: contact@finsightanalytics.com

## About Finsight Analytics LLP

We build professional data analytics tools and solutions.
