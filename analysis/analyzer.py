import pandas as pd
import numpy as np


# =====================================================
# 01. SAFE NUMBER CONVERSION
# =====================================================

def safe_number(value):

    if pd.isna(value):
        return None

    return round(float(value), 2)


# =====================================================
# 02. MAIN DATASET ANALYSIS
# =====================================================

def analyze_dataset(df):

    # Empty dataset protection
    if df is None or df.empty:

        return {
            "overview": {
                "total_rows": 0,
                "total_columns": 0,
                "missing_values": 0,
                "duplicate_rows": 0,
                "memory_usage": 0
            },
            "numerical": {},
            "categorical": {},
            "numerical_columns": [],
            "categorical_columns": [],
            "missing_by_column": {},
            "columns": {}
        }

    # Work on a copy
    df = df.copy()

    # =================================================
    # 03. COLUMN IDENTIFICATION
    # =================================================

    numerical_columns = df.select_dtypes(
        include=np.number
    ).columns.tolist()

    categorical_columns = df.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()

    # =================================================
    # 04. DATASET OVERVIEW
    # =================================================

    total_rows = len(df)

    total_columns = len(df.columns)

    missing_values = int(
        df.isnull().sum().sum()
    )

    duplicate_rows = int(
        df.duplicated().sum()
    )

    memory_usage = round(
        df.memory_usage(deep=True).sum() / 1024,
        2
    )

    overview = {
        "total_rows": total_rows,
        "total_columns": total_columns,
        "missing_values": missing_values,
        "duplicate_rows": duplicate_rows,
        "memory_usage": memory_usage
    }

    # =================================================
    # 05. NUMERICAL ANALYSIS
    # =================================================

    numerical_summary = {}

    for column in numerical_columns:

        series = df[column]

        numerical_summary[column] = {
            "mean": safe_number(series.mean()),
            "median": safe_number(series.median()),
            "minimum": safe_number(series.min()),
            "maximum": safe_number(series.max()),
            "std": safe_number(series.std()),
            "sum": safe_number(series.sum()),
            "unique": int(series.nunique()),
            "missing": int(series.isnull().sum())
        }

    # =================================================
    # 06. CATEGORICAL ANALYSIS
    # =================================================

    categorical_summary = {}

    for column in categorical_columns:

        series = df[column]

        mode_values = series.mode(
            dropna=True
        )

        top_value = (
            str(mode_values.iloc[0])
            if not mode_values.empty
            else "N/A"
        )

        categorical_summary[column] = {
            "unique": int(series.nunique()),
            "top_value": top_value,
            "missing": int(series.isnull().sum()),
            "total_values": int(series.count())
        }

    # =================================================
    # 07. MISSING VALUES BY COLUMN
    # =================================================

    missing_by_column = {}

    for column in df.columns:

        missing_by_column[column] = int(
            df[column].isnull().sum()
        )

    # =================================================
    # 08. COLUMN INFORMATION
    # =================================================

    column_details = {}

    for column in df.columns:

        column_details[column] = {
            "data_type": str(df[column].dtype),
            "unique_values": int(df[column].nunique()),
            "missing_values": int(
                df[column].isnull().sum()
            ),
            "non_null_values": int(
                df[column].count()
            )
        }

    # =================================================
    # 09. FINAL ANALYSIS RESULT
    # =================================================

    return {
        "overview": overview,
        "numerical": numerical_summary,
        "categorical": categorical_summary,
        "numerical_columns": numerical_columns,
        "categorical_columns": categorical_columns,
        "missing_by_column": missing_by_column,
        "columns": column_details
    }