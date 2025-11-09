#!/usr/bin/env python3
"""
Gemini AI integration for intelligent data reconciliation analysis.
Use this when Python analysis needs enhancement with AI insights.
"""

import google.generativeai as genai
import pandas as pd
import json
from typing import Dict, List, Any, Optional
import os


class GeminiReconciliationAnalyzer:
    """
    Use Gemini AI for intelligent analysis where Python alone is insufficient:
    - Pattern detection in mismatches
    - Root cause analysis
    - Data quality insights
    - Anomaly detection explanations
    - Reconciliation strategy recommendations
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini AI client.
        API key from environment variable GEMINI_API_KEY or parameter.
        """
        api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("Gemini API key required. Set GEMINI_API_KEY or pass api_key parameter")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def analyze_mismatch_patterns(self, mismatches_df: pd.DataFrame, context: str = "") -> Dict[str, Any]:
        """
        Use Gemini to identify patterns in mismatches that Python can't easily detect.
        
        When to use this:
        - Need to identify semantic patterns in discrepancies
        - Looking for business logic issues
        - Require human-readable insights about data quality
        """
        if mismatches_df.empty:
            return {"patterns": [], "insights": "No mismatches to analyze"}
        
        # Prepare data summary (sample for large datasets)
        sample_size = min(100, len(mismatches_df))
        sample = mismatches_df.head(sample_size)
        
        # Create structured summary
        summary = {
            "total_mismatches": len(mismatches_df),
            "columns_affected": mismatches_df['column'].unique().tolist(),
            "sample_mismatches": sample.to_dict('records')
        }
        
        prompt = f"""Analyze these data reconciliation mismatches and identify patterns:

Context: {context}

Summary:
- Total mismatches: {summary['total_mismatches']}
- Columns affected: {', '.join(summary['columns_affected'])}

Sample mismatches (first {sample_size}):
{json.dumps(summary['sample_mismatches'], indent=2, default=str)}

Please provide:
1. **Common patterns**: What patterns do you see in the mismatches?
2. **Root causes**: What might be causing these discrepancies?
3. **Data quality issues**: Are there systematic data quality problems?
4. **Recommendations**: What should be done to resolve or prevent these issues?

Format as JSON with keys: patterns, root_causes, data_quality_issues, recommendations
"""
        
        response = self.model.generate_content(prompt)
        
        try:
            # Extract JSON from response
            text = response.text
            # Remove markdown code blocks if present
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]
            
            analysis = json.loads(text.strip())
            return analysis
        except:
            # Fallback to text response if JSON parsing fails
            return {"analysis": response.text}
    
    def analyze_unmatched_records(self, 
                                  unmatched_source: pd.DataFrame, 
                                  unmatched_target: pd.DataFrame,
                                  context: str = "") -> Dict[str, Any]:
        """
        Use Gemini to understand why records don't match between sources.
        
        When to use this:
        - Need to understand business reasons for unmatched records
        - Looking for data entry patterns or timing issues
        - Require insights on data synchronization problems
        """
        source_sample = unmatched_source.head(50).to_dict('records')
        target_sample = unmatched_target.head(50).to_dict('records')
        
        prompt = f"""Analyze unmatched records from data reconciliation:

Context: {context}

Unmatched in Source ({len(unmatched_source)} total, showing first 50):
{json.dumps(source_sample, indent=2, default=str)}

Unmatched in Target ({len(unmatched_target)} total, showing first 50):
{json.dumps(target_sample, indent=2, default=str)}

Provide insights on:
1. Why these records might not match
2. Potential business process issues
3. Data synchronization problems
4. Recommended investigation steps

Format as JSON with keys: likely_causes, business_insights, sync_issues, investigation_steps
"""
        
        response = self.model.generate_content(prompt)
        
        try:
            text = response.text
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]
            
            return json.loads(text.strip())
        except:
            return {"analysis": response.text}
    
    def suggest_reconciliation_strategy(self, 
                                       source_info: Dict[str, Any],
                                       target_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Gemini to recommend optimal reconciliation approach based on data characteristics.
        
        When to use this:
        - Starting a new reconciliation project
        - Dealing with complex or unfamiliar data structures
        - Need guidance on matching keys and comparison logic
        """
        prompt = f"""Recommend a reconciliation strategy for these datasets:

Source System: {source_info.get('name', 'Unknown')}
- Columns: {source_info.get('columns', [])}
- Record count: {source_info.get('record_count', 0)}
- Sample data: {json.dumps(source_info.get('sample', []), indent=2, default=str)}

Target System: {target_info.get('name', 'Unknown')}
- Columns: {target_info.get('columns', [])}
- Record count: {target_info.get('record_count', 0)}
- Sample data: {json.dumps(target_info.get('sample', []), indent=2, default=str)}

Provide:
1. **Key columns**: Which columns should be used as matching keys?
2. **Compare columns**: Which columns should be compared for differences?
3. **Transformations**: What data transformations are needed before comparison?
4. **Tolerances**: Should numeric comparisons use tolerances? If so, what values?
5. **Special considerations**: Any data quality or business logic considerations?

Format as JSON with keys: key_columns, compare_columns, transformations, tolerances, special_considerations
"""
        
        response = self.model.generate_content(prompt)
        
        try:
            text = response.text
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]
            
            return json.loads(text.strip())
        except:
            return {"strategy": response.text}
    
    def explain_discrepancy(self, 
                           source_value: Any, 
                           target_value: Any, 
                           column_name: str,
                           context: Dict[str, Any] = None) -> str:
        """
        Use Gemini to explain a specific discrepancy in business terms.
        
        When to use this:
        - Need to explain complex discrepancies to non-technical stakeholders
        - Value differences require business context interpretation
        - Debugging individual high-priority mismatches
        """
        context_str = json.dumps(context, indent=2, default=str) if context else "None provided"
        
        prompt = f"""Explain this data discrepancy in clear business terms:

Column: {column_name}
Source value: {source_value}
Target value: {target_value}
Additional context: {context_str}

Provide:
1. A clear explanation of the discrepancy
2. Possible business reasons for the difference
3. Whether this is likely a data quality issue or a timing/process difference
4. Recommended action

Keep it concise and business-focused.
"""
        
        response = self.model.generate_content(prompt)
        return response.text
    
    def detect_anomalies(self, data: pd.DataFrame, column: str) -> Dict[str, Any]:
        """
        Use Gemini to identify anomalies that statistical methods might miss.
        
        When to use this:
        - Need semantic anomaly detection beyond statistical outliers
        - Looking for business logic violations
        - Require contextual understanding of what's "normal"
        """
        # Get statistical summary
        stats = data[column].describe().to_dict()
        sample = data[column].dropna().head(100).tolist()
        
        prompt = f"""Analyze this data column for anomalies:

Column: {column}
Statistics: {json.dumps(stats, indent=2, default=str)}
Sample values (first 100): {sample}

Identify:
1. **Anomalies**: Values or patterns that seem unusual
2. **Business concerns**: Issues from a business logic perspective
3. **Data quality**: Systematic data quality problems
4. **Recommendations**: What to investigate or fix

Format as JSON with keys: anomalies, business_concerns, data_quality, recommendations
"""
        
        response = self.model.generate_content(prompt)
        
        try:
            text = response.text
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0]
            elif '```' in text:
                text = text.split('```')[1].split('```')[0]
            
            return json.loads(text.strip())
        except:
            return {"analysis": response.text}


# Example usage
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = GeminiReconciliationAnalyzer()
    
    # Example: Analyze mismatch patterns
    mismatches = pd.DataFrame({
        'column': ['amount', 'amount', 'status'],
        'source_value': [100.50, 200.00, 'pending'],
        'target_value': [100.00, 201.00, 'complete']
    })
    
    insights = analyzer.analyze_mismatch_patterns(
        mismatches, 
        context="Financial transaction reconciliation between ERP and payment gateway"
    )
    
    print(json.dumps(insights, indent=2))
