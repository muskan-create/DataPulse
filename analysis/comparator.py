import pandas as pd


def compare_datasets(df1, df2):

    common_columns = sorted(
        set(df1.columns).intersection(set(df2.columns))
    )

    numerical_columns = [
        col for col in common_columns
        if pd.api.types.is_numeric_dtype(df1[col])
        and pd.api.types.is_numeric_dtype(df2[col])
    ]

    numerical_comparison = {}

    for column in numerical_columns:

        value1 = float(df1[column].mean())
        value2 = float(df2[column].mean())

        numerical_comparison[column] = {
            "dataset1_mean": round(value1, 2),
            "dataset2_mean": round(value2, 2),
            "difference": round(value2 - value1, 2)
        }

    return {
        "dataset1_rows": len(df1),
        "dataset2_rows": len(df2),

        "dataset1_columns": len(df1.columns),
        "dataset2_columns": len(df2.columns),

        "dataset1_missing": int(df1.isnull().sum().sum()),
        "dataset2_missing": int(df2.isnull().sum().sum()),

        "dataset1_duplicates": int(df1.duplicated().sum()),
        "dataset2_duplicates": int(df2.duplicated().sum()),

        "common_columns": common_columns,
        "only_dataset1": sorted(set(df1.columns) - set(df2.columns)),
        "only_dataset2": sorted(set(df2.columns) - set(df1.columns)),

        "numerical_comparison": numerical_comparison
    }