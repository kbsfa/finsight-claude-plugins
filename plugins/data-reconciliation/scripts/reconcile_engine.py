#!/usr/bin/env python3
"""
Core reconciliation engine for comparing datasets.
Maximizes Python for data manipulation, uses Gemini for intelligent analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
import logging
from tqdm import tqdm
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ReconciliationConfig:
    """Configuration for reconciliation process."""
    source_name: str
    target_name: str
    key_columns: List[str]
    compare_columns: List[str]
    tolerance: Optional[Dict[str, float]] = None  # For numeric comparisons
    ignore_case: bool = True
    trim_whitespace: bool = True
    date_format: Optional[str] = None

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.source_name or not self.target_name:
            raise ValueError("source_name and target_name are required")
        if not self.key_columns:
            raise ValueError("key_columns must contain at least one column")
        if not self.compare_columns:
            raise ValueError("compare_columns must contain at least one column")

        # Check for overlap between key and compare columns
        overlap = set(self.key_columns) & set(self.compare_columns)
        if overlap:
            logger.warning(f"Columns appear in both key_columns and compare_columns: {overlap}")

        logger.info(f"Reconciliation config validated: {self.source_name} <-> {self.target_name}")


@dataclass
class ReconciliationResult:
    """Results from reconciliation process."""
    matched_count: int
    unmatched_source: pd.DataFrame
    unmatched_target: pd.DataFrame
    mismatches: pd.DataFrame
    summary: Dict[str, Any]
    timestamp: str


class ReconciliationEngine:
    """Core engine for data reconciliation."""

    def __init__(self, config: ReconciliationConfig):
        self.config = config
        self.tolerance = config.tolerance or {}
        logger.info(f"Initialized ReconciliationEngine with tolerance: {self.tolerance}")

    def validate_dataframes(self, source_df: pd.DataFrame, target_df: pd.DataFrame):
        """Validate dataframes before reconciliation."""
        # Check for empty dataframes
        if source_df.empty:
            raise ValueError("Source dataframe is empty")
        if target_df.empty:
            raise ValueError("Target dataframe is empty")

        # Validate key columns exist
        missing_source_keys = set(self.config.key_columns) - set(source_df.columns)
        if missing_source_keys:
            raise ValueError(f"Key columns missing in source: {missing_source_keys}")

        missing_target_keys = set(self.config.key_columns) - set(target_df.columns)
        if missing_target_keys:
            raise ValueError(f"Key columns missing in target: {missing_target_keys}")

        # Validate compare columns exist
        missing_source_compare = set(self.config.compare_columns) - set(source_df.columns)
        if missing_source_compare:
            raise ValueError(f"Compare columns missing in source: {missing_source_compare}")

        missing_target_compare = set(self.config.compare_columns) - set(target_df.columns)
        if missing_target_compare:
            raise ValueError(f"Compare columns missing in target: {missing_target_compare}")

        logger.info(f"Dataframes validated - Source: {len(source_df)} rows, Target: {len(target_df)} rows")
        
    def normalize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize data based on configuration."""
        df = df.copy()
        
        # Trim whitespace
        if self.config.trim_whitespace:
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].str.strip() if df[col].dtype == 'object' else df[col]
        
        # Handle case insensitivity
        if self.config.ignore_case:
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].str.lower() if df[col].dtype == 'object' else df[col]
        
        # Parse dates if format specified
        if self.config.date_format:
            date_cols = df.select_dtypes(include=['object']).columns
            for col in date_cols:
                try:
                    df[col] = pd.to_datetime(df[col], format=self.config.date_format, errors='coerce')
                except:
                    pass
        
        return df
    
    def create_composite_key(self, df: pd.DataFrame) -> pd.Series:
        """Create composite key from key columns."""
        key_parts = [df[col].astype(str) for col in self.config.key_columns]
        return pd.Series(['|'.join(parts) for parts in zip(*key_parts)], index=df.index)
    
    def compare_values(self, val1: Any, val2: Any, column: str) -> Tuple[bool, Optional[float]]:
        """
        Compare two values with tolerance handling.
        Returns (is_match, difference)
        """
        # Handle null values
        if pd.isna(val1) and pd.isna(val2):
            return True, None
        if pd.isna(val1) or pd.isna(val2):
            return False, None
        
        # Numeric comparison with tolerance
        if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
            diff = abs(val1 - val2)
            tolerance = self.tolerance.get(column, 0)
            return diff <= tolerance, diff
        
        # String comparison
        return val1 == val2, None
    
    def reconcile(self, source_df: pd.DataFrame, target_df: pd.DataFrame, show_progress: bool = True) -> ReconciliationResult:
        """
        Perform reconciliation between source and target datasets.

        Args:
            source_df: Source dataframe
            target_df: Target dataframe
            show_progress: Show progress bars (default: True)

        Returns:
            ReconciliationResult with all reconciliation findings
        """
        try:
            start_time = datetime.now()
            logger.info("Starting reconciliation process...")

            # Validate dataframes
            self.validate_dataframes(source_df, target_df)

            # Normalize data
            logger.info("Normalizing data...")
            source_norm = self.normalize_data(source_df)
            target_norm = self.normalize_data(target_df)

            # Create composite keys
            logger.info("Creating composite keys...")
            source_norm['_key'] = self.create_composite_key(source_norm)
            target_norm['_key'] = self.create_composite_key(target_norm)

            # Check for duplicate keys
            source_dup_keys = source_norm['_key'].duplicated().sum()
            target_dup_keys = target_norm['_key'].duplicated().sum()
            if source_dup_keys > 0:
                logger.warning(f"Found {source_dup_keys} duplicate keys in source data")
            if target_dup_keys > 0:
                logger.warning(f"Found {target_dup_keys} duplicate keys in target data")

            # Find matching keys
            logger.info("Matching keys...")
            source_keys = set(source_norm['_key'])
            target_keys = set(target_norm['_key'])

            matched_keys = source_keys & target_keys
            unmatched_source_keys = source_keys - target_keys
            unmatched_target_keys = target_keys - source_keys

            logger.info(f"Matched: {len(matched_keys)}, Unmatched Source: {len(unmatched_source_keys)}, Unmatched Target: {len(unmatched_target_keys)}")

            # Extract unmatched records
            unmatched_source = source_df[source_norm['_key'].isin(unmatched_source_keys)].copy()
            unmatched_target = target_df[target_norm['_key'].isin(unmatched_target_keys)].copy()

            # Compare matched records
            logger.info("Comparing matched records...")
            mismatches = []

            # Use tqdm for progress tracking if enabled
            key_iterator = tqdm(matched_keys, desc="Comparing records", disable=not show_progress) if show_progress else matched_keys

            for key in key_iterator:
                source_row = source_norm[source_norm['_key'] == key].iloc[0]
                target_row = target_norm[target_norm['_key'] == key].iloc[0]

                for col in self.config.compare_columns:
                    is_match, diff = self.compare_values(source_row[col], target_row[col], col)

                    if not is_match:
                        # Get original values (before normalization)
                        orig_source = source_df[source_norm['_key'] == key].iloc[0]
                        orig_target = target_df[target_norm['_key'] == key].iloc[0]

                        mismatch = {
                            'key': key,
                            'column': col,
                            f'{self.config.source_name}_value': orig_source[col],
                            f'{self.config.target_name}_value': orig_target[col],
                            'difference': diff
                        }
                        # Add key column values for context
                        for key_col in self.config.key_columns:
                            mismatch[key_col] = orig_source[key_col]

                        mismatches.append(mismatch)

            mismatches_df = pd.DataFrame(mismatches) if mismatches else pd.DataFrame()
            logger.info(f"Found {len(mismatches)} mismatches")
        
            # Create summary
            processing_time = (datetime.now() - start_time).total_seconds()
            summary = {
                'total_source_records': len(source_df),
                'total_target_records': len(target_df),
                'matched_records': len(matched_keys),
                'unmatched_source_records': len(unmatched_source_keys),
                'unmatched_target_records': len(unmatched_target_keys),
                'mismatched_values': len(mismatches),
                'match_rate': len(matched_keys) / max(len(source_keys), 1) * 100,
                'accuracy_rate': (len(matched_keys) - len(mismatches_df)) / max(len(matched_keys), 1) * 100 if len(matched_keys) > 0 else 0,
                'processing_time_seconds': processing_time,
                'source_duplicate_keys': int(source_dup_keys),
                'target_duplicate_keys': int(target_dup_keys)
            }

            logger.info(f"Reconciliation completed in {processing_time:.2f} seconds")
            logger.info(f"Match rate: {summary['match_rate']:.2f}%")

            return ReconciliationResult(
                matched_count=len(matched_keys),
                unmatched_source=unmatched_source,
                unmatched_target=unmatched_target,
                mismatches=mismatches_df,
                summary=summary,
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            logger.error(f"Reconciliation failed: {str(e)}", exc_info=True)
            raise
    
    def export_results(self, result: ReconciliationResult, output_dir: str, format: str = 'csv'):
        """
        Export reconciliation results to files.

        Args:
            result: ReconciliationResult to export
            output_dir: Output directory path
            format: Export format ('csv', 'excel', 'both') - default 'csv'
        """
        try:
            import os
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            logger.info(f"Exporting results to {output_dir} in {format} format...")

            if format in ['csv', 'both']:
                # Export unmatched records
                if not result.unmatched_source.empty:
                    source_file = output_path / f"unmatched_{self.config.source_name}.csv"
                    result.unmatched_source.to_csv(source_file, index=False)
                    logger.info(f"Exported {len(result.unmatched_source)} unmatched source records")

                if not result.unmatched_target.empty:
                    target_file = output_path / f"unmatched_{self.config.target_name}.csv"
                    result.unmatched_target.to_csv(target_file, index=False)
                    logger.info(f"Exported {len(result.unmatched_target)} unmatched target records")

                # Export mismatches
                if not result.mismatches.empty:
                    mismatch_file = output_path / "mismatches.csv"
                    result.mismatches.to_csv(mismatch_file, index=False)
                    logger.info(f"Exported {len(result.mismatches)} mismatches")

            if format in ['excel', 'both']:
                # Export to Excel with multiple sheets
                excel_file = output_path / "reconciliation_report.xlsx"
                with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
                    # Summary sheet
                    summary_df = pd.DataFrame([result.summary]).T
                    summary_df.columns = ['Value']
                    summary_df.to_excel(writer, sheet_name='Summary')

                    # Unmatched source
                    if not result.unmatched_source.empty:
                        result.unmatched_source.to_excel(writer, sheet_name='Unmatched Source', index=False)

                    # Unmatched target
                    if not result.unmatched_target.empty:
                        result.unmatched_target.to_excel(writer, sheet_name='Unmatched Target', index=False)

                    # Mismatches
                    if not result.mismatches.empty:
                        result.mismatches.to_excel(writer, sheet_name='Mismatches', index=False)

                logger.info(f"Exported Excel report to {excel_file}")

            # Export summary JSON
            summary_file = output_path / "summary.json"
            with open(summary_file, 'w') as f:
                json.dump(result.summary, f, indent=2, default=str)

            logger.info(f"Results exported successfully to {output_dir}/")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to export results: {str(e)}", exc_info=True)
            raise


# Example usage
if __name__ == "__main__":
    # Example: Reconcile two CSV files
    config = ReconciliationConfig(
        source_name="system_a",
        target_name="system_b",
        key_columns=["id"],
        compare_columns=["amount", "status"],
        tolerance={"amount": 0.01},
        ignore_case=True,
        trim_whitespace=True
    )
    
    # Load data
    source = pd.read_csv("source_data.csv")
    target = pd.read_csv("target_data.csv")
    
    # Reconcile
    engine = ReconciliationEngine(config)
    result = engine.reconcile(source, target)
    
    # Export results
    engine.export_results(result, "reconciliation_results")
    
    # Print summary
    print(json.dumps(result.summary, indent=2))
