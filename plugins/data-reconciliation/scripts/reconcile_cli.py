#!/usr/bin/env python3
"""
Intelligent CLI for data reconciliation.
Automatically analyzes data and recommends optimal reconciliation strategy.
"""

import click
import pandas as pd
import json
import sys
from pathlib import Path
from typing import Optional
import logging
from colorama import Fore, Style, init
from tabulate import tabulate

# Initialize colorama for cross-platform colored terminal
init(autoreset=True)

from data_loader import DataLoader
from data_profiler import IntelligentDataProfiler
from reconcile_engine import ReconciliationEngine, ReconciliationConfig
from visualizer import ReconciliationVisualizer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_success(message: str):
    """Print success message in green."""
    click.echo(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def print_error(message: str):
    """Print error message in red."""
    click.echo(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")


def print_warning(message: str):
    """Print warning message in yellow."""
    click.echo(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")


def print_info(message: str):
    """Print info message in cyan."""
    click.echo(f"{Fore.CYAN}ℹ {message}{Style.RESET_ALL}")


def print_section(title: str):
    """Print section header."""
    click.echo(f"\n{Fore.BLUE}{'='*70}")
    click.echo(f"{Fore.BLUE}{title:^70}")
    click.echo(f"{Fore.BLUE}{'='*70}{Style.RESET_ALL}\n")


@click.group()
def cli():
    """Intelligent Data Reconciliation Tool - Automatically analyzes and reconciles datasets."""
    pass


@cli.command()
@click.argument('source', type=click.Path(exists=True))
@click.argument('target', type=click.Path(exists=True))
@click.option('--auto', is_flag=True, help='Automatically determine reconciliation strategy')
@click.option('--key-columns', '-k', multiple=True, help='Key columns for matching')
@click.option('--compare-columns', '-c', multiple=True, help='Columns to compare')
@click.option('--output', '-o', default='reconciliation_output', help='Output directory')
@click.option('--format', '-f', type=click.Choice(['csv', 'excel', 'both']), default='both',
              help='Output format')
@click.option('--visualize', is_flag=True, help='Generate visualizations')
@click.option('--interactive', is_flag=True, help='Use interactive mode for confirmation')
def reconcile(source: str, target: str, auto: bool, key_columns: tuple,
              compare_columns: tuple, output: str, format: str, visualize: bool,
              interactive: bool):
    """
    Reconcile two datasets intelligently.

    Examples:
        # Auto mode (recommended) - analyzes data and suggests strategy
        reconcile-cli reconcile source.csv target.csv --auto

        # Manual mode - specify columns
        reconcile-cli reconcile source.csv target.csv -k id -c amount -c status

        # With visualization
        reconcile-cli reconcile source.csv target.csv --auto --visualize
    """
    try:
        print_section("INTELLIGENT DATA RECONCILIATION")

        # Load datasets
        print_info(f"Loading source: {source}")
        source_df = DataLoader.auto_detect_and_load(source)
        print_success(f"Loaded {len(source_df)} source records")

        print_info(f"Loading target: {target}")
        target_df = DataLoader.auto_detect_and_load(target)
        print_success(f"Loaded {len(target_df)} target records")

        # Auto mode: Use intelligent profiler
        if auto or (not key_columns and not compare_columns):
            print_section("ANALYZING DATA STRUCTURE")
            print_info("Running intelligent data profiler...")

            profiler = IntelligentDataProfiler()

            # Profile both datasets
            source_profile = profiler.profile_dataset(source_df, "Source")
            target_profile = profiler.profile_dataset(target_df, "Target")

            # Display data quality summary
            print_section("DATA QUALITY SUMMARY")

            source_quality_data = [
                ["Source Quality Score", f"{source_profile.overall_quality_score:.1f}/100"],
                ["Target Quality Score", f"{target_profile.overall_quality_score:.1f}/100"],
                ["Source Rows", f"{source_profile.row_count:,}"],
                ["Target Rows", f"{target_profile.row_count:,}"],
                ["Common Columns", len(set(source_df.columns) & set(target_df.columns))]
            ]
            click.echo(tabulate(source_quality_data, tablefmt="grid"))

            # Show data quality issues
            all_issues = source_profile.data_quality_issues + target_profile.data_quality_issues
            if all_issues:
                print_warning(f"\nFound {len(all_issues)} data quality issues:")
                for issue in all_issues[:5]:  # Show top 5
                    severity_color = Fore.RED if issue['severity'] == 'critical' else Fore.YELLOW
                    click.echo(f"  {severity_color}[{issue['severity'].upper()}] {issue['column']}: {issue['issue']}{Style.RESET_ALL}")
                    click.echo(f"    → {issue['recommendation']}")

            # Get strategy recommendation
            print_section("RECOMMENDED RECONCILIATION STRATEGY")
            strategy = profiler.suggest_reconciliation_strategy(source_profile, target_profile)

            if strategy['status'] == 'error':
                print_error(strategy['message'])
                print_info(strategy['recommendation'])
                sys.exit(1)

            # Display strategy
            strategy_data = [
                ["Key Columns", ", ".join(strategy['recommended_key_columns']) or "None found"],
                ["Compare Columns", ", ".join(strategy['recommended_compare_columns'][:5]) + "..." if len(strategy['recommended_compare_columns']) > 5 else ", ".join(strategy['recommended_compare_columns'])],
                ["Tolerance Settings", json.dumps(strategy['recommended_tolerance']) if strategy['recommended_tolerance'] else "None"],
                ["Strategy Confidence", f"{strategy['confidence']:.0f}%"]
            ]
            click.echo(tabulate(strategy_data, tablefmt="grid"))

            # Show recommended transformations
            if strategy['recommended_transformations']:
                print_info(f"\nRecommended {len(strategy['recommended_transformations'])} transformations:")
                for trans in strategy['recommended_transformations'][:5]:
                    click.echo(f"  • {trans['column']}: {trans['transformation']} - {trans['reason']}")

            # Interactive confirmation
            if interactive:
                if not click.confirm(f"\n{Fore.CYAN}Proceed with this strategy?{Style.RESET_ALL}"):
                    print_warning("Reconciliation cancelled by user")
                    sys.exit(0)

            # Use strategy recommendations
            key_columns = strategy['recommended_key_columns']
            compare_columns = strategy['recommended_compare_columns']
            tolerance = strategy['recommended_tolerance']

        else:
            # Manual mode
            key_columns = list(key_columns)
            compare_columns = list(compare_columns)
            tolerance = {}

        # Validate configuration
        if not key_columns:
            print_error("No key columns specified or detected. Cannot proceed.")
            print_info("Try using --auto mode for automatic key detection")
            sys.exit(1)

        if not compare_columns:
            print_warning("No compare columns specified. Will compare all common columns except keys.")
            common_cols = set(source_df.columns) & set(target_df.columns)
            compare_columns = list(common_cols - set(key_columns))

        # Configure reconciliation
        print_section("RECONCILIATION CONFIGURATION")
        config_data = [
            ["Source", Path(source).name],
            ["Target", Path(target).name],
            ["Key Columns", ", ".join(key_columns)],
            ["Compare Columns", ", ".join(compare_columns[:5]) + ("..." if len(compare_columns) > 5 else "")],
            ["Output Directory", output]
        ]
        click.echo(tabulate(config_data, tablefmt="grid"))

        config = ReconciliationConfig(
            source_name=Path(source).stem,
            target_name=Path(target).stem,
            key_columns=key_columns,
            compare_columns=compare_columns,
            tolerance=tolerance,
            ignore_case=True,
            trim_whitespace=True
        )

        # Execute reconciliation
        print_section("EXECUTING RECONCILIATION")
        print_info("Reconciling datasets...")

        engine = ReconciliationEngine(config)
        result = engine.reconcile(source_df, target_df, show_progress=True)

        # Display results
        print_section("RECONCILIATION RESULTS")

        results_data = [
            ["Total Source Records", f"{result.summary['total_source_records']:,}"],
            ["Total Target Records", f"{result.summary['total_target_records']:,}"],
            ["Matched Records", f"{Fore.GREEN}{result.summary['matched_records']:,}{Style.RESET_ALL}"],
            ["Unmatched Source", f"{Fore.YELLOW}{result.summary['unmatched_source_records']:,}{Style.RESET_ALL}"],
            ["Unmatched Target", f"{Fore.YELLOW}{result.summary['unmatched_target_records']:,}{Style.RESET_ALL}"],
            ["Mismatched Values", f"{Fore.RED}{result.summary['mismatched_values']:,}{Style.RESET_ALL}"],
            ["Match Rate", f"{result.summary['match_rate']:.2f}%"],
            ["Accuracy Rate", f"{result.summary['accuracy_rate']:.2f}%"],
            ["Processing Time", f"{result.summary['processing_time_seconds']:.2f}s"]
        ]
        click.echo(tabulate(results_data, tablefmt="grid"))

        # Export results
        print_section("EXPORTING RESULTS")
        print_info(f"Exporting to {output} in {format} format...")

        output_path = engine.export_results(result, output, format=format)
        print_success(f"Results exported to {output_path}")

        # Generate visualizations
        if visualize:
            print_section("GENERATING VISUALIZATIONS")
            print_info("Creating visualizations...")

            viz = ReconciliationVisualizer(result)

            # Create dashboard
            dashboard_file = Path(output) / "dashboard.html"
            viz.create_dashboard(str(dashboard_file))
            print_success(f"Dashboard saved to {dashboard_file}")

            # Create summary chart
            summary_file = Path(output) / "summary_chart.png"
            viz.create_summary_chart(str(summary_file), interactive=False)
            print_success(f"Summary chart saved to {summary_file}")

            if not result.mismatches.empty:
                mismatch_file = Path(output) / "mismatch_analysis.png"
                viz.create_mismatch_analysis(str(mismatch_file))
                print_success(f"Mismatch analysis saved to {mismatch_file}")

        # Final summary
        print_section("RECONCILIATION COMPLETE")
        if result.summary['match_rate'] >= 95:
            print_success(f"Excellent! {result.summary['match_rate']:.1f}% match rate")
        elif result.summary['match_rate'] >= 80:
            print_warning(f"Good {result.summary['match_rate']:.1f}% match rate, but room for improvement")
        else:
            print_warning(f"Low match rate: {result.summary['match_rate']:.1f}% - investigate data quality")

    except Exception as e:
        print_error(f"Reconciliation failed: {str(e)}")
        logger.exception("Detailed error:")
        sys.exit(1)


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--detailed', is_flag=True, help='Show detailed column profiles')
def profile(file_path: str, detailed: bool):
    """
    Profile a dataset to understand its structure and quality.

    Example:
        reconcile-cli profile data.csv --detailed
    """
    try:
        print_section("DATA PROFILING")

        # Load dataset
        print_info(f"Loading: {file_path}")
        df = DataLoader.auto_detect_and_load(file_path)
        print_success(f"Loaded {len(df)} records with {len(df.columns)} columns")

        # Profile
        profiler = IntelligentDataProfiler()
        profile = profiler.profile_dataset(df, Path(file_path).name)

        # Display overview
        print_section("DATASET OVERVIEW")
        overview_data = [
            ["File", Path(file_path).name],
            ["Rows", f"{profile.row_count:,}"],
            ["Columns", profile.column_count],
            ["Overall Quality Score", f"{profile.overall_quality_score:.1f}/100"]
        ]
        click.echo(tabulate(overview_data, tablefmt="grid"))

        # Display candidate keys
        print_section("CANDIDATE KEY COLUMNS")
        if profile.candidate_key_columns:
            for i, key in enumerate(profile.candidate_key_columns, 1):
                click.echo(f"  {i}. {' + '.join(key)}")
        else:
            print_warning("No candidate key columns found")

        # Display column summary
        if detailed:
            print_section("COLUMN PROFILES")
            for col_name, col_profile in profile.column_profiles.items():
                click.echo(f"\n{Fore.CYAN}Column: {col_name}{Style.RESET_ALL}")
                col_data = [
                    ["Type", col_profile.inferred_type],
                    ["Unique Values", f"{col_profile.unique_count:,} ({col_profile.unique_percentage:.1f}%)"],
                    ["Null Values", f"{col_profile.null_count:,} ({col_profile.null_percentage:.1f}%)"],
                    ["Quality Score", f"{col_profile.data_quality_score:.1f}/100"],
                    ["Recommended for Key", "Yes" if col_profile.recommended_for_key else "No"]
                ]
                click.echo(tabulate(col_data, tablefmt="plain"))

                if col_profile.issues:
                    print_warning("  Issues:")
                    for issue in col_profile.issues:
                        click.echo(f"    • {issue}")

        # Display quality issues
        if profile.data_quality_issues:
            print_section("DATA QUALITY ISSUES")
            for issue in profile.data_quality_issues:
                severity_color = Fore.RED if issue['severity'] == 'critical' else Fore.YELLOW
                click.echo(f"{severity_color}[{issue['severity'].upper()}] {issue['column']}{Style.RESET_ALL}")
                click.echo(f"  Issue: {issue['issue']}")
                click.echo(f"  Impact: {issue['impact']}")
                click.echo(f"  Recommendation: {issue['recommendation']}\n")

        # Display transformation recommendations
        if profile.recommended_transformations:
            print_section("RECOMMENDED TRANSFORMATIONS")
            for trans in profile.recommended_transformations:
                priority_color = Fore.RED if trans['priority'] == 'high' else Fore.YELLOW
                click.echo(f"{priority_color}[{trans['priority'].upper()}] {trans['column']}{Style.RESET_ALL}")
                click.echo(f"  Transformation: {trans['transformation']}")
                click.echo(f"  Reason: {trans['reason']}\n")

    except Exception as e:
        print_error(f"Profiling failed: {str(e)}")
        logger.exception("Detailed error:")
        sys.exit(1)


@cli.command()
def version():
    """Show version information."""
    click.echo("Intelligent Data Reconciliation Tool v2.0")
    click.echo("Enhanced with AI-powered strategy recommendations")


if __name__ == '__main__':
    cli()
