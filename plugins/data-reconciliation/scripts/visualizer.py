#!/usr/bin/env python3
"""
Visualization module for reconciliation results.
Creates charts and graphs to help understand reconciliation outcomes.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List
from pathlib import Path
import logging

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from reconcile_engine import ReconciliationResult

logger = logging.getLogger(__name__)

# Set style
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


class ReconciliationVisualizer:
    """Create visualizations for reconciliation results."""

    def __init__(self, result: ReconciliationResult):
        """
        Initialize visualizer with reconciliation result.

        Args:
            result: ReconciliationResult to visualize
        """
        self.result = result
        self.summary = result.summary

    def create_summary_chart(self, output_file: Optional[str] = None, interactive: bool = False):
        """
        Create a summary chart showing match/mismatch statistics.

        Args:
            output_file: Path to save the chart (None = display only)
            interactive: Use plotly for interactive chart (default: False, uses matplotlib)
        """
        if interactive and PLOTLY_AVAILABLE:
            return self._create_summary_chart_plotly(output_file)
        else:
            return self._create_summary_chart_matplotlib(output_file)

    def _create_summary_chart_matplotlib(self, output_file: Optional[str] = None):
        """Create summary chart using matplotlib."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Chart 1: Match/Unmatch breakdown
        categories = ['Matched', 'Unmatched Source', 'Unmatched Target']
        values = [
            self.summary['matched_records'],
            self.summary['unmatched_source_records'],
            self.summary['unmatched_target_records']
        ]
        colors = ['#2ecc71', '#e74c3c', '#f39c12']

        axes[0].bar(categories, values, color=colors)
        axes[0].set_title('Record Matching Overview', fontsize=14, fontweight='bold')
        axes[0].set_ylabel('Number of Records')
        axes[0].grid(axis='y', alpha=0.3)

        # Add value labels on bars
        for i, v in enumerate(values):
            axes[0].text(i, v, str(v), ha='center', va='bottom')

        # Chart 2: Match rate pie chart
        match_rate = self.summary['match_rate']
        unmatch_rate = 100 - match_rate

        axes[1].pie([match_rate, unmatch_rate],
                    labels=['Matched', 'Unmatched'],
                    colors=['#2ecc71', '#e74c3c'],
                    autopct='%1.1f%%',
                    startangle=90)
        axes[1].set_title('Match Rate', fontsize=14, fontweight='bold')

        plt.tight_layout()

        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            logger.info(f"Summary chart saved to {output_file}")

        plt.show()
        return fig

    def _create_summary_chart_plotly(self, output_file: Optional[str] = None):
        """Create summary chart using plotly (interactive)."""
        from plotly.subplots import make_subplots

        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Record Matching Overview', 'Match Rate'),
            specs=[[{"type": "bar"}, {"type": "pie"}]]
        )

        # Chart 1: Match/Unmatch breakdown
        categories = ['Matched', 'Unmatched<br>Source', 'Unmatched<br>Target']
        values = [
            self.summary['matched_records'],
            self.summary['unmatched_source_records'],
            self.summary['unmatched_target_records']
        ]
        colors = ['#2ecc71', '#e74c3c', '#f39c12']

        fig.add_trace(
            go.Bar(x=categories, y=values, marker_color=colors, text=values, textposition='auto'),
            row=1, col=1
        )

        # Chart 2: Match rate pie chart
        match_rate = self.summary['match_rate']
        unmatch_rate = 100 - match_rate

        fig.add_trace(
            go.Pie(labels=['Matched', 'Unmatched'],
                   values=[match_rate, unmatch_rate],
                   marker_colors=['#2ecc71', '#e74c3c']),
            row=1, col=2
        )

        fig.update_layout(height=500, showlegend=False, title_text="Reconciliation Summary")

        if output_file:
            fig.write_html(output_file)
            logger.info(f"Interactive summary chart saved to {output_file}")

        fig.show()
        return fig

    def create_mismatch_analysis(self, output_file: Optional[str] = None):
        """
        Create detailed analysis of mismatches by column.

        Args:
            output_file: Path to save the chart (None = display only)
        """
        if self.result.mismatches.empty:
            logger.warning("No mismatches to analyze")
            return None

        # Count mismatches by column
        mismatch_counts = self.result.mismatches['column'].value_counts()

        fig, ax = plt.subplots(figsize=(10, 6))
        mismatch_counts.plot(kind='barh', ax=ax, color='#e74c3c')

        ax.set_title('Mismatches by Column', fontsize=14, fontweight='bold')
        ax.set_xlabel('Number of Mismatches')
        ax.set_ylabel('Column')
        ax.grid(axis='x', alpha=0.3)

        # Add value labels
        for i, v in enumerate(mismatch_counts.values):
            ax.text(v, i, str(v), ha='left', va='center', fontweight='bold')

        plt.tight_layout()

        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            logger.info(f"Mismatch analysis saved to {output_file}")

        plt.show()
        return fig

    def create_numeric_difference_distribution(self, column: str, output_file: Optional[str] = None):
        """
        Create distribution chart for numeric differences in a specific column.

        Args:
            column: Column name to analyze
            output_file: Path to save the chart (None = display only)
        """
        if self.result.mismatches.empty:
            logger.warning("No mismatches to analyze")
            return None

        # Filter mismatches for this column
        column_mismatches = self.result.mismatches[self.result.mismatches['column'] == column]

        if column_mismatches.empty:
            logger.warning(f"No mismatches found for column: {column}")
            return None

        # Get differences
        differences = column_mismatches['difference'].dropna()

        if differences.empty:
            logger.warning(f"No numeric differences found for column: {column}")
            return None

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        # Histogram
        axes[0].hist(differences, bins=30, color='#3498db', edgecolor='black', alpha=0.7)
        axes[0].set_title(f'Distribution of Differences - {column}', fontsize=14, fontweight='bold')
        axes[0].set_xlabel('Difference')
        axes[0].set_ylabel('Frequency')
        axes[0].grid(axis='y', alpha=0.3)

        # Box plot
        axes[1].boxplot(differences, vert=True)
        axes[1].set_title(f'Box Plot of Differences - {column}', fontsize=14, fontweight='bold')
        axes[1].set_ylabel('Difference')
        axes[1].grid(axis='y', alpha=0.3)

        plt.tight_layout()

        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            logger.info(f"Difference distribution chart saved to {output_file}")

        plt.show()
        return fig

    def create_dashboard(self, output_file: str):
        """
        Create comprehensive dashboard with all visualizations.

        Args:
            output_file: Path to save the dashboard (HTML for interactive, PNG for static)
        """
        if PLOTLY_AVAILABLE and output_file.endswith('.html'):
            return self._create_dashboard_plotly(output_file)
        else:
            return self._create_dashboard_matplotlib(output_file)

    def _create_dashboard_matplotlib(self, output_file: str):
        """Create static dashboard using matplotlib."""
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

        # Summary stats
        ax1 = fig.add_subplot(gs[0, :])
        ax1.axis('off')
        summary_text = f"""
        RECONCILIATION SUMMARY
        ═══════════════════════════════════════════════════════════
        Total Source Records: {self.summary['total_source_records']:,}
        Total Target Records: {self.summary['total_target_records']:,}
        Matched Records: {self.summary['matched_records']:,}
        Unmatched Source: {self.summary['unmatched_source_records']:,}
        Unmatched Target: {self.summary['unmatched_target_records']:,}
        Mismatched Values: {self.summary['mismatched_values']:,}
        Match Rate: {self.summary['match_rate']:.2f}%
        Accuracy Rate: {self.summary['accuracy_rate']:.2f}%
        Processing Time: {self.summary['processing_time_seconds']:.2f}s
        """
        ax1.text(0.5, 0.5, summary_text, ha='center', va='center',
                fontsize=11, family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

        # Match breakdown
        ax2 = fig.add_subplot(gs[1, 0])
        categories = ['Matched', 'Unmatched\nSource', 'Unmatched\nTarget']
        values = [
            self.summary['matched_records'],
            self.summary['unmatched_source_records'],
            self.summary['unmatched_target_records']
        ]
        colors = ['#2ecc71', '#e74c3c', '#f39c12']
        ax2.bar(categories, values, color=colors)
        ax2.set_title('Record Matching', fontweight='bold')
        ax2.set_ylabel('Count')
        for i, v in enumerate(values):
            ax2.text(i, v, str(v), ha='center', va='bottom')

        # Match rate pie
        ax3 = fig.add_subplot(gs[1, 1])
        match_rate = self.summary['match_rate']
        unmatch_rate = 100 - match_rate
        ax3.pie([match_rate, unmatch_rate],
                labels=['Matched', 'Unmatched'],
                colors=['#2ecc71', '#e74c3c'],
                autopct='%1.1f%%',
                startangle=90)
        ax3.set_title('Match Rate %', fontweight='bold')

        # Mismatch analysis
        if not self.result.mismatches.empty:
            ax4 = fig.add_subplot(gs[2, :])
            mismatch_counts = self.result.mismatches['column'].value_counts()
            mismatch_counts.plot(kind='barh', ax=ax4, color='#e74c3c')
            ax4.set_title('Mismatches by Column', fontweight='bold')
            ax4.set_xlabel('Count')

        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        logger.info(f"Dashboard saved to {output_file}")
        plt.show()
        return fig

    def _create_dashboard_plotly(self, output_file: str):
        """Create interactive dashboard using plotly."""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Record Matching Overview', 'Match Rate',
                            'Reconciliation Statistics', 'Mismatches by Column'),
            specs=[[{"type": "bar"}, {"type": "pie"}],
                   [{"type": "table", "colspan": 2}, None]],
            row_heights=[0.4, 0.6]
        )

        # Chart 1: Match breakdown
        categories = ['Matched', 'Unmatched Source', 'Unmatched Target']
        values = [
            self.summary['matched_records'],
            self.summary['unmatched_source_records'],
            self.summary['unmatched_target_records']
        ]
        colors = ['#2ecc71', '#e74c3c', '#f39c12']

        fig.add_trace(
            go.Bar(x=categories, y=values, marker_color=colors, text=values, textposition='auto'),
            row=1, col=1
        )

        # Chart 2: Match rate pie
        match_rate = self.summary['match_rate']
        unmatch_rate = 100 - match_rate

        fig.add_trace(
            go.Pie(labels=['Matched', 'Unmatched'],
                   values=[match_rate, unmatch_rate],
                   marker_colors=['#2ecc71', '#e74c3c']),
            row=1, col=2
        )

        # Chart 3: Summary table
        summary_data = pd.DataFrame([self.summary]).T.reset_index()
        summary_data.columns = ['Metric', 'Value']

        fig.add_trace(
            go.Table(
                header=dict(values=['Metric', 'Value'],
                            fill_color='paleturquoise',
                            align='left'),
                cells=dict(values=[summary_data['Metric'], summary_data['Value']],
                           fill_color='lavender',
                           align='left')),
            row=2, col=1
        )

        fig.update_layout(height=800, showlegend=False, title_text="Reconciliation Dashboard")

        fig.write_html(output_file)
        logger.info(f"Interactive dashboard saved to {output_file}")
        return fig


# Example usage
if __name__ == "__main__":
    # This is a placeholder - in real usage, you would have a ReconciliationResult
    print("Visualizer module loaded successfully")
    print(f"Plotly available: {PLOTLY_AVAILABLE}")
