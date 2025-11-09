"""
Data Reconciliation Skill for Claude Code

An intelligent data reconciliation toolkit that automatically analyzes datasets,
detects data quality issues, and suggests optimal reconciliation strategies.

Main components:
- DataLoader: Load data from multiple sources (CSV, Excel, DB, API, etc.)
- IntelligentDataProfiler: Analyze data structure and quality
- ReconciliationEngine: Core reconciliation logic
- GeminiReconciliationAnalyzer: AI-powered insights
- ReconciliationVisualizer: Create charts and dashboards
"""

__version__ = "2.0.0"
__author__ = "Finsight Analytics LLP"
__license__ = "MIT"

# Core imports
from .data_loader import DataLoader, DataTransformer
from .data_profiler import (
    IntelligentDataProfiler,
    DatasetProfile,
    ColumnProfile
)
from .reconcile_engine import (
    ReconciliationEngine,
    ReconciliationConfig,
    ReconciliationResult
)
from .gemini_analyzer import GeminiReconciliationAnalyzer
from .visualizer import ReconciliationVisualizer

# Define public API
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__license__",

    # Data loading
    "DataLoader",
    "DataTransformer",

    # Data profiling
    "IntelligentDataProfiler",
    "DatasetProfile",
    "ColumnProfile",

    # Reconciliation
    "ReconciliationEngine",
    "ReconciliationConfig",
    "ReconciliationResult",

    # AI analysis
    "GeminiReconciliationAnalyzer",

    # Visualization
    "ReconciliationVisualizer",
]


def get_version():
    """Return the current version."""
    return __version__


def quick_reconcile(source_file: str, target_file: str, output_dir: str = "output"):
    """
    Quick reconciliation with automatic strategy detection.

    This is a convenience function for simple reconciliation tasks.

    Args:
        source_file: Path to source file
        target_file: Path to target file
        output_dir: Output directory for results

    Returns:
        ReconciliationResult

    Example:
        >>> from data_reconciliation import quick_reconcile
        >>> result = quick_reconcile('source.csv', 'target.csv')
        >>> print(f"Match rate: {result.summary['match_rate']:.2f}%")
    """
    # Load data
    source = DataLoader.auto_detect_and_load(source_file)
    target = DataLoader.auto_detect_and_load(target_file)

    # Profile and get strategy
    profiler = IntelligentDataProfiler()
    source_profile = profiler.profile_dataset(source, "Source")
    target_profile = profiler.profile_dataset(target, "Target")
    strategy = profiler.suggest_reconciliation_strategy(source_profile, target_profile)

    if strategy['status'] == 'error':
        raise ValueError(f"Cannot reconcile: {strategy['message']}")

    # Configure
    from pathlib import Path
    config = ReconciliationConfig(
        source_name=Path(source_file).stem,
        target_name=Path(target_file).stem,
        key_columns=strategy['recommended_key_columns'],
        compare_columns=strategy['recommended_compare_columns'],
        tolerance=strategy.get('recommended_tolerance', {})
    )

    # Reconcile
    engine = ReconciliationEngine(config)
    result = engine.reconcile(source, target)

    # Export
    engine.export_results(result, output_dir, format='both')

    return result


# Module-level docstring
"""
Usage Examples:

1. Quick reconciliation:
    from data_reconciliation import quick_reconcile
    result = quick_reconcile('source.csv', 'target.csv')

2. Detailed reconciliation:
    from data_reconciliation import DataLoader, IntelligentDataProfiler, ReconciliationEngine

    source = DataLoader.load_csv('source.csv')
    target = DataLoader.load_csv('target.csv')

    profiler = IntelligentDataProfiler()
    strategy = profiler.suggest_reconciliation_strategy(
        profiler.profile_dataset(source),
        profiler.profile_dataset(target)
    )

    config = ReconciliationConfig(
        source_name="source",
        target_name="target",
        key_columns=strategy['recommended_key_columns'],
        compare_columns=strategy['recommended_compare_columns']
    )

    engine = ReconciliationEngine(config)
    result = engine.reconcile(source, target)

3. With visualization:
    from data_reconciliation import ReconciliationVisualizer

    viz = ReconciliationVisualizer(result)
    viz.create_dashboard('dashboard.html')
"""
