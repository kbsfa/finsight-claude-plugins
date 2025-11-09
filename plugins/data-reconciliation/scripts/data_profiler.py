#!/usr/bin/env python3
"""
Intelligent data profiler for automatic reconciliation strategy detection.
Analyzes datasets to understand structure, types, and recommend optimal matching strategies.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import logging
from collections import Counter

logger = logging.getLogger(__name__)


@dataclass
class ColumnProfile:
    """Profile of a single column."""
    name: str
    dtype: str
    null_count: int
    null_percentage: float
    unique_count: int
    unique_percentage: float
    is_unique: bool
    sample_values: List[Any]
    inferred_type: str  # 'id', 'numeric', 'date', 'category', 'text', 'boolean'
    recommended_for_key: bool
    data_quality_score: float  # 0-100
    issues: List[str]


@dataclass
class DatasetProfile:
    """Comprehensive dataset profile."""
    row_count: int
    column_count: int
    column_profiles: Dict[str, ColumnProfile]
    candidate_key_columns: List[List[str]]  # Single or composite keys
    recommended_transformations: List[Dict[str, Any]]
    data_quality_issues: List[Dict[str, Any]]
    overall_quality_score: float


class IntelligentDataProfiler:
    """
    Analyze datasets and automatically recommend reconciliation strategies.
    This is the brain that makes reconciliation smarter.
    """

    def __init__(self):
        self.min_uniqueness_for_key = 0.95  # 95% unique to be considered a key
        self.sample_size = 100

    def profile_column(self, df: pd.DataFrame, col_name: str) -> ColumnProfile:
        """Profile a single column comprehensively."""
        col = df[col_name]
        total_rows = len(df)

        # Basic statistics
        null_count = col.isna().sum()
        null_percentage = (null_count / total_rows) * 100
        unique_count = col.nunique()
        unique_percentage = (unique_count / total_rows) * 100
        is_unique = unique_percentage >= self.min_uniqueness_for_key

        # Sample values (non-null)
        sample_values = col.dropna().head(self.sample_size).tolist()

        # Infer semantic type
        inferred_type = self._infer_column_type(col, col_name)

        # Data quality issues
        issues = self._detect_column_issues(col, col_name, inferred_type)

        # Calculate quality score
        quality_score = self._calculate_quality_score(
            null_percentage, unique_percentage, inferred_type, issues
        )

        # Recommend for key?
        recommended_for_key = self._recommend_for_key(
            is_unique, inferred_type, null_percentage, unique_percentage, issues
        )

        return ColumnProfile(
            name=col_name,
            dtype=str(col.dtype),
            null_count=int(null_count),
            null_percentage=float(null_percentage),
            unique_count=int(unique_count),
            unique_percentage=float(unique_percentage),
            is_unique=bool(is_unique),
            sample_values=sample_values,
            inferred_type=inferred_type,
            recommended_for_key=recommended_for_key,
            data_quality_score=float(quality_score),
            issues=issues
        )

    def _infer_column_type(self, col: pd.Series, col_name: str) -> str:
        """Infer semantic type of column."""
        # Check column name patterns
        name_lower = col_name.lower()
        id_patterns = ['id', '_id', 'key', 'code', 'number', 'ref', 'transaction']
        date_patterns = ['date', 'time', 'datetime', 'created', 'updated', 'timestamp']
        amount_patterns = ['amount', 'price', 'cost', 'value', 'total', 'balance']

        # Check if it's an ID column by name
        if any(pattern in name_lower for pattern in id_patterns):
            return 'id'

        # Check data type
        if pd.api.types.is_numeric_dtype(col):
            # Check if it looks like an ID (integers, sequential, or unique)
            if pd.api.types.is_integer_dtype(col):
                uniqueness = col.nunique() / len(col)
                if uniqueness > 0.9:
                    return 'id'

            # Check if it's an amount
            if any(pattern in name_lower for pattern in amount_patterns):
                return 'numeric_amount'

            return 'numeric'

        elif pd.api.types.is_datetime64_any_dtype(col):
            return 'date'

        elif pd.api.types.is_bool_dtype(col):
            return 'boolean'

        elif pd.api.types.is_object_dtype(col):
            # String column - try to infer further
            non_null = col.dropna()
            if len(non_null) == 0:
                return 'text'

            # Try to parse as date
            if any(pattern in name_lower for pattern in date_patterns):
                try:
                    pd.to_datetime(non_null.head(100), errors='coerce')
                    return 'date_string'
                except:
                    pass

            # Check uniqueness for category vs text
            uniqueness = non_null.nunique() / len(non_null)
            if uniqueness < 0.1:  # Less than 10% unique = category
                return 'category'
            elif uniqueness > 0.9:  # More than 90% unique = id or text
                # Check average length
                avg_len = non_null.astype(str).str.len().mean()
                if avg_len < 20:
                    return 'id'
                else:
                    return 'text'
            else:
                return 'text'

        return 'unknown'

    def _detect_column_issues(self, col: pd.Series, col_name: str, inferred_type: str) -> List[str]:
        """Detect data quality issues in a column."""
        issues = []

        # High null percentage
        null_pct = (col.isna().sum() / len(col)) * 100
        if null_pct > 50:
            issues.append(f"High null percentage: {null_pct:.1f}%")
        elif null_pct > 10:
            issues.append(f"Moderate null percentage: {null_pct:.1f}%")

        non_null = col.dropna()
        if len(non_null) == 0:
            issues.append("Column is entirely null")
            return issues

        # String-specific issues
        if pd.api.types.is_object_dtype(col):
            # Leading/trailing whitespace
            has_whitespace = non_null.astype(str).str.strip() != non_null.astype(str)
            if has_whitespace.any():
                issues.append(f"Whitespace issues in {has_whitespace.sum()} values")

            # Case inconsistency (same value in different cases)
            lower_values = non_null.astype(str).str.lower()
            if lower_values.nunique() < non_null.nunique():
                issues.append("Case inconsistency detected")

            # Special characters
            has_special = non_null.astype(str).str.contains(r'[^\w\s-]', regex=True, na=False)
            if has_special.any():
                issues.append(f"Special characters in {has_special.sum()} values")

        # Numeric-specific issues
        if pd.api.types.is_numeric_dtype(col):
            # Outliers (simple IQR method)
            Q1 = non_null.quantile(0.25)
            Q3 = non_null.quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((non_null < (Q1 - 3 * IQR)) | (non_null > (Q3 + 3 * IQR))).sum()
            if outliers > 0:
                issues.append(f"Potential outliers: {outliers} values")

            # Negative values where unexpected
            if 'amount' in col_name.lower() or 'price' in col_name.lower():
                negatives = (non_null < 0).sum()
                if negatives > 0:
                    issues.append(f"Negative values: {negatives}")

        # Duplicate values (for ID columns)
        if inferred_type == 'id':
            dup_count = col.duplicated().sum()
            if dup_count > 0:
                issues.append(f"Duplicate values: {dup_count} (expected unique)")

        return issues

    def _calculate_quality_score(self, null_pct: float, unique_pct: float,
                                  inferred_type: str, issues: List[str]) -> float:
        """Calculate overall quality score for a column (0-100)."""
        score = 100.0

        # Penalize for nulls
        score -= min(null_pct, 50)  # Max 50 point deduction

        # Penalize for issues
        score -= len(issues) * 5  # 5 points per issue

        # Bonus for good characteristics
        if inferred_type in ['id', 'numeric', 'date']:
            score += 10  # Clean data types get bonus

        return max(0, min(100, score))

    def _recommend_for_key(self, is_unique: bool, inferred_type: str,
                           null_pct: float, unique_pct: float, issues: List[str]) -> bool:
        """Determine if column is recommended as a key."""
        # Must be highly unique
        if not is_unique or unique_pct < 95:
            return False

        # Should not have many nulls
        if null_pct > 5:
            return False

        # Prefer ID types
        if inferred_type == 'id':
            return True

        # Avoid text columns unless very clean
        if inferred_type == 'text' and len(issues) > 0:
            return False

        # No duplicate issues
        if any('Duplicate' in issue for issue in issues):
            return False

        return True

    def profile_dataset(self, df: pd.DataFrame, dataset_name: str = "Dataset") -> DatasetProfile:
        """Profile entire dataset comprehensively."""
        logger.info(f"Profiling {dataset_name} with {len(df)} rows and {len(df.columns)} columns...")

        # Profile each column
        column_profiles = {}
        for col in df.columns:
            try:
                column_profiles[col] = self.profile_column(df, col)
            except Exception as e:
                logger.error(f"Error profiling column {col}: {str(e)}")

        # Find candidate key columns
        candidate_keys = self._find_candidate_keys(df, column_profiles)

        # Recommend transformations
        transformations = self._recommend_transformations(column_profiles)

        # Identify data quality issues
        data_quality_issues = self._identify_data_quality_issues(column_profiles)

        # Overall quality score
        overall_quality = np.mean([p.data_quality_score for p in column_profiles.values()])

        profile = DatasetProfile(
            row_count=len(df),
            column_count=len(df.columns),
            column_profiles=column_profiles,
            candidate_key_columns=candidate_keys,
            recommended_transformations=transformations,
            data_quality_issues=data_quality_issues,
            overall_quality_score=float(overall_quality)
        )

        logger.info(f"{dataset_name} profiling complete. Quality score: {overall_quality:.1f}/100")
        return profile

    def _find_candidate_keys(self, df: pd.DataFrame,
                             column_profiles: Dict[str, ColumnProfile]) -> List[List[str]]:
        """Find candidate key columns (single or composite)."""
        candidates = []

        # Single column keys
        for col_name, profile in column_profiles.items():
            if profile.recommended_for_key:
                candidates.append([col_name])

        # Composite keys (2-column combinations)
        high_unique_cols = [
            name for name, profile in column_profiles.items()
            if profile.unique_percentage > 80 and profile.null_percentage < 10
        ]

        for i, col1 in enumerate(high_unique_cols):
            for col2 in high_unique_cols[i+1:]:
                # Check if combination is unique
                combo_unique = df[[col1, col2]].drop_duplicates().shape[0]
                combo_unique_pct = (combo_unique / len(df)) * 100
                if combo_unique_pct >= 95:
                    candidates.append([col1, col2])

        # Sort by preference (single keys first, then by uniqueness)
        candidates.sort(key=lambda x: (len(x), -sum(column_profiles[col].unique_percentage for col in x)))

        return candidates[:5]  # Return top 5 candidates

    def _recommend_transformations(self, column_profiles: Dict[str, ColumnProfile]) -> List[Dict[str, Any]]:
        """Recommend data transformations based on column profiles."""
        transformations = []

        for col_name, profile in column_profiles.items():
            # Date parsing recommendations
            if profile.inferred_type == 'date_string':
                transformations.append({
                    'column': col_name,
                    'transformation': 'parse_date',
                    'reason': 'Column appears to contain dates as strings',
                    'priority': 'high'
                })

            # Whitespace trimming
            if any('Whitespace' in issue for issue in profile.issues):
                transformations.append({
                    'column': col_name,
                    'transformation': 'trim_whitespace',
                    'reason': 'Leading/trailing whitespace detected',
                    'priority': 'high'
                })

            # Case normalization
            if any('Case inconsistency' in issue for issue in profile.issues):
                transformations.append({
                    'column': col_name,
                    'transformation': 'normalize_case',
                    'reason': 'Inconsistent casing detected',
                    'priority': 'medium'
                })

            # Numeric standardization
            if profile.inferred_type == 'numeric_amount':
                transformations.append({
                    'column': col_name,
                    'transformation': 'round_numeric',
                    'reason': 'Amount field should be standardized to 2 decimal places',
                    'priority': 'medium',
                    'params': {'decimal_places': 2}
                })

        return transformations

    def _identify_data_quality_issues(self, column_profiles: Dict[str, ColumnProfile]) -> List[Dict[str, Any]]:
        """Identify critical data quality issues."""
        critical_issues = []

        for col_name, profile in column_profiles.items():
            # High null percentage
            if profile.null_percentage > 50:
                critical_issues.append({
                    'severity': 'high',
                    'column': col_name,
                    'issue': f'High null percentage: {profile.null_percentage:.1f}%',
                    'impact': 'May cause many unmatched records',
                    'recommendation': 'Investigate source data quality or exclude column from comparison'
                })

            # Duplicates in ID columns
            if profile.inferred_type == 'id' and any('Duplicate' in issue for issue in profile.issues):
                critical_issues.append({
                    'severity': 'critical',
                    'column': col_name,
                    'issue': 'Duplicate values in ID column',
                    'impact': 'Cannot use as unique key',
                    'recommendation': 'Investigate duplicates or use composite key'
                })

        return critical_issues

    def suggest_reconciliation_strategy(self, source_profile: DatasetProfile,
                                       target_profile: DatasetProfile) -> Dict[str, Any]:
        """
        Suggest optimal reconciliation strategy based on dataset profiles.
        This is the intelligent recommendation engine.
        """
        logger.info("Analyzing datasets to suggest optimal reconciliation strategy...")

        # Find common columns
        source_cols = set(source_profile.column_profiles.keys())
        target_cols = set(target_profile.column_profiles.keys())
        common_cols = source_cols & target_cols

        if not common_cols:
            return {
                'status': 'error',
                'message': 'No common columns found between datasets',
                'recommendation': 'Check column names - may need renaming or mapping'
            }

        # Find best key columns from candidates
        source_keys = source_profile.candidate_key_columns
        target_keys = target_profile.candidate_key_columns

        # Find keys that exist in both datasets
        valid_keys = []
        for source_key in source_keys:
            if all(col in common_cols for col in source_key):
                # Check if target also has these columns with good uniqueness
                target_unique = all(
                    target_profile.column_profiles[col].unique_percentage > 90
                    for col in source_key if col in target_profile.column_profiles
                )
                if target_unique:
                    valid_keys.append(source_key)

        # Determine recommended key columns
        if valid_keys:
            recommended_key = valid_keys[0]  # Best candidate
        else:
            # Fallback: find columns with high uniqueness in both
            high_unique_common = [
                col for col in common_cols
                if source_profile.column_profiles[col].unique_percentage > 80
                and target_profile.column_profiles[col].unique_percentage > 80
            ]
            if high_unique_common:
                recommended_key = [high_unique_common[0]]
            else:
                recommended_key = []

        # Find compare columns (common columns that are not keys)
        key_set = set(recommended_key) if recommended_key else set()
        compare_candidates = [
            col for col in common_cols
            if col not in key_set
            and source_profile.column_profiles[col].inferred_type in ['numeric', 'numeric_amount', 'date', 'category']
        ]

        # Determine tolerance requirements
        tolerance = {}
        for col in compare_candidates:
            if source_profile.column_profiles[col].inferred_type == 'numeric_amount':
                tolerance[col] = 0.01  # 1 cent for amounts

        # Aggregate transformations
        all_transformations = source_profile.recommended_transformations + target_profile.recommended_transformations

        # Aggregate quality issues
        all_issues = source_profile.data_quality_issues + target_profile.data_quality_issues

        strategy = {
            'status': 'success',
            'recommended_key_columns': recommended_key,
            'recommended_compare_columns': compare_candidates[:10],  # Top 10
            'recommended_tolerance': tolerance,
            'recommended_transformations': all_transformations,
            'data_quality_warnings': all_issues,
            'common_columns_count': len(common_cols),
            'source_quality_score': source_profile.overall_quality_score,
            'target_quality_score': target_profile.overall_quality_score,
            'confidence': self._calculate_strategy_confidence(
                recommended_key, compare_candidates, all_issues
            )
        }

        logger.info(f"Strategy confidence: {strategy['confidence']:.0f}%")
        return strategy

    def _calculate_strategy_confidence(self, key_cols: List[str],
                                       compare_cols: List[str],
                                       issues: List[Dict]) -> float:
        """Calculate confidence level in the recommended strategy."""
        confidence = 100.0

        # Reduce confidence if no good key found
        if not key_cols:
            confidence -= 50

        # Reduce confidence if few compare columns
        if len(compare_cols) < 2:
            confidence -= 20

        # Reduce confidence for critical issues
        critical_count = sum(1 for issue in issues if issue.get('severity') == 'critical')
        confidence -= critical_count * 15

        return max(0, min(100, confidence))


# Example usage
if __name__ == "__main__":
    print("Intelligent Data Profiler loaded successfully")
