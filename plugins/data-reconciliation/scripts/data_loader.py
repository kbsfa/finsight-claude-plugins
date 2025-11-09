#!/usr/bin/env python3
"""
Data loader for various data sources.
Maximize Python for data loading and transformation.
"""

import pandas as pd
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
import sqlalchemy
from sqlalchemy import create_engine


class DataLoader:
    """Load data from various sources for reconciliation."""
    
    @staticmethod
    def load_csv(file_path: str, **kwargs) -> pd.DataFrame:
        """
        Load CSV file.
        
        Common kwargs:
        - encoding: 'utf-8', 'latin1', etc.
        - sep: ',' (default), '\t', '|', etc.
        - dtype: dict of column types
        - parse_dates: list of date columns
        """
        return pd.read_csv(file_path, **kwargs)
    
    @staticmethod
    def load_excel(file_path: str, sheet_name: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        Load Excel file.
        
        Args:
            sheet_name: Sheet to load (default: first sheet)
        
        Common kwargs:
        - header: row number for column names
        - usecols: columns to load
        - dtype: dict of column types
        """
        return pd.read_excel(file_path, sheet_name=sheet_name or 0, **kwargs)
    
    @staticmethod
    def load_json(file_path: str, orient: str = 'records', **kwargs) -> pd.DataFrame:
        """
        Load JSON file.
        
        Args:
            orient: 'records' (list of dicts), 'split', 'index', 'columns', 'values'
        """
        return pd.read_json(file_path, orient=orient, **kwargs)
    
    @staticmethod
    def load_parquet(file_path: str, **kwargs) -> pd.DataFrame:
        """Load Parquet file."""
        return pd.read_parquet(file_path, **kwargs)
    
    @staticmethod
    def load_from_database(connection_string: str, query: str) -> pd.DataFrame:
        """
        Load data from database using SQL query.
        
        Args:
            connection_string: SQLAlchemy connection string
                Examples:
                - PostgreSQL: 'postgresql://user:pass@host:port/db'
                - MySQL: 'mysql+pymysql://user:pass@host:port/db'
                - SQL Server: 'mssql+pyodbc://user:pass@host:port/db?driver=...'
                - SQLite: 'sqlite:///path/to/db.sqlite'
            query: SQL query to execute
        
        Example:
            df = load_from_database(
                'postgresql://user:pass@localhost:5432/mydb',
                'SELECT * FROM transactions WHERE date >= CURRENT_DATE - 7'
            )
        """
        engine = create_engine(connection_string)
        return pd.read_sql(query, engine)
    
    @staticmethod
    def load_from_api(url: str, 
                     auth: Optional[Dict[str, str]] = None,
                     params: Optional[Dict[str, Any]] = None,
                     headers: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """
        Load data from REST API.
        
        Args:
            url: API endpoint URL
            auth: Authentication dict (e.g., {'username': 'user', 'password': 'pass'})
            params: Query parameters
            headers: HTTP headers
        
        Example:
            df = load_from_api(
                'https://api.example.com/data',
                headers={'Authorization': 'Bearer token'},
                params={'start_date': '2024-01-01'}
            )
        """
        import requests
        
        auth_tuple = None
        if auth and 'username' in auth:
            auth_tuple = (auth['username'], auth.get('password', ''))
        
        response = requests.get(url, auth=auth_tuple, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        
        # Handle different response formats
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            # Try to find the data array in common API response patterns
            for key in ['data', 'results', 'items', 'records']:
                if key in data and isinstance(data[key], list):
                    return pd.DataFrame(data[key])
            # If no standard key, try to convert the dict directly
            return pd.DataFrame([data])
        else:
            raise ValueError(f"Unsupported API response format: {type(data)}")
    
    @staticmethod
    def load_multiple_files(pattern: str, loader_func: callable, **kwargs) -> pd.DataFrame:
        """
        Load and concatenate multiple files matching a pattern.
        
        Args:
            pattern: File pattern (e.g., 'data/*.csv', 'reports_*.xlsx')
            loader_func: Function to load each file (e.g., DataLoader.load_csv)
            **kwargs: Arguments to pass to loader_func
        
        Example:
            df = load_multiple_files('data/transactions_*.csv', DataLoader.load_csv)
        """
        from glob import glob
        
        files = glob(pattern)
        if not files:
            raise ValueError(f"No files found matching pattern: {pattern}")
        
        dfs = []
        for file in files:
            df = loader_func(file, **kwargs)
            df['_source_file'] = Path(file).name  # Track source file
            dfs.append(df)
        
        return pd.concat(dfs, ignore_index=True)
    
    @staticmethod
    def auto_detect_and_load(file_path: str, **kwargs) -> pd.DataFrame:
        """
        Automatically detect file type and load with appropriate loader.
        
        Supports: .csv, .xlsx, .xls, .json, .parquet, .tsv
        """
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        loaders = {
            '.csv': DataLoader.load_csv,
            '.tsv': lambda f, **kw: DataLoader.load_csv(f, sep='\t', **kw),
            '.xlsx': DataLoader.load_excel,
            '.xls': DataLoader.load_excel,
            '.json': DataLoader.load_json,
            '.parquet': DataLoader.load_parquet,
        }
        
        loader = loaders.get(suffix)
        if not loader:
            raise ValueError(f"Unsupported file type: {suffix}")
        
        return loader(file_path, **kwargs)


class DataTransformer:
    """Common data transformations before reconciliation."""
    
    @staticmethod
    def deduplicate(df: pd.DataFrame, subset: Optional[List[str]] = None, keep: str = 'first') -> pd.DataFrame:
        """
        Remove duplicate records.
        
        Args:
            subset: Columns to consider for duplicates (None = all columns)
            keep: 'first', 'last', or False (remove all duplicates)
        """
        return df.drop_duplicates(subset=subset, keep=keep)
    
    @staticmethod
    def standardize_dates(df: pd.DataFrame, date_columns: List[str], format: str = None) -> pd.DataFrame:
        """
        Standardize date columns to datetime format.
        
        Args:
            date_columns: List of column names containing dates
            format: Date format string (None = auto-detect)
        """
        df = df.copy()
        for col in date_columns:
            df[col] = pd.to_datetime(df[col], format=format, errors='coerce')
        return df
    
    @staticmethod
    def standardize_numeric(df: pd.DataFrame, 
                           numeric_columns: List[str], 
                           decimal_places: Optional[int] = None) -> pd.DataFrame:
        """
        Standardize numeric columns.
        
        Args:
            numeric_columns: List of column names containing numbers
            decimal_places: Round to this many decimal places (None = no rounding)
        """
        df = df.copy()
        for col in numeric_columns:
            # Remove currency symbols and commas
            if df[col].dtype == 'object':
                df[col] = df[col].str.replace('[$,€£¥]', '', regex=True)
            
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
            if decimal_places is not None:
                df[col] = df[col].round(decimal_places)
        
        return df
    
    @staticmethod
    def map_values(df: pd.DataFrame, column: str, mapping: Dict[Any, Any]) -> pd.DataFrame:
        """
        Map values in a column using a mapping dictionary.
        
        Example:
            mapping = {'Y': 'Yes', 'N': 'No', 1: 'Yes', 0: 'No'}
            df = map_values(df, 'status', mapping)
        """
        df = df.copy()
        df[column] = df[column].map(mapping).fillna(df[column])
        return df
    
    @staticmethod
    def filter_date_range(df: pd.DataFrame, 
                         date_column: str, 
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Filter dataframe to a date range.
        
        Args:
            date_column: Name of date column
            start_date: Start date (inclusive, format: 'YYYY-MM-DD')
            end_date: End date (inclusive, format: 'YYYY-MM-DD')
        """
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        
        if start_date:
            df = df[df[date_column] >= pd.to_datetime(start_date)]
        if end_date:
            df = df[df[date_column] <= pd.to_datetime(end_date)]
        
        return df


# Example usage
if __name__ == "__main__":
    # Example 1: Load CSV
    source = DataLoader.load_csv('source_data.csv')
    
    # Example 2: Load from database
    target = DataLoader.load_from_database(
        'postgresql://user:pass@localhost:5432/mydb',
        'SELECT * FROM transactions WHERE date >= CURRENT_DATE - 7'
    )
    
    # Example 3: Transform data
    source = DataTransformer.standardize_dates(source, ['transaction_date'])
    source = DataTransformer.standardize_numeric(source, ['amount'], decimal_places=2)
    
    print(f"Source: {len(source)} records")
    print(f"Target: {len(target)} records")
