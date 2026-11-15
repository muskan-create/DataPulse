import pandas as pd


# =========================================================
# 01. DATA CLEANING REPORT
# =========================================================

def get_cleaning_report(df):

    if df is None:
        raise ValueError("Dataset not found.")

    rows = len(df)
    columns = len(df.columns)

    missing = df.isnull().sum()
    total_missing = int(missing.sum())
    duplicates = int(df.duplicated().sum())

    total_cells = rows * columns

    if total_cells > 0:
        quality_score = round(
            max(
                0,
                100 - ((total_missing + duplicates) / total_cells * 100)
            ),
            2
        )
    else:
        quality_score = 0

    return {
        "missing": missing.to_dict(),
        "total_missing": total_missing,
        "duplicates": duplicates,
        "quality_score": quality_score,
        "rows": rows,
        "columns": columns
    }


# =========================================================
# 02. HANDLE MISSING VALUES
# =========================================================

def handle_missing_values(df, method):

    cleaned = df.copy()

    if method == "drop":
        cleaned = cleaned.dropna()

    elif method == "mean":

        numeric_columns = cleaned.select_dtypes(
            include="number"
        ).columns

        for column in numeric_columns:
            if cleaned[column].isnull().any():
                value = cleaned[column].mean()

                if pd.notna(value):
                    cleaned[column] = cleaned[column].fillna(value)

    elif method == "median":

        numeric_columns = cleaned.select_dtypes(
            include="number"
        ).columns

        for column in numeric_columns:
            if cleaned[column].isnull().any():
                value = cleaned[column].median()

                if pd.notna(value):
                    cleaned[column] = cleaned[column].fillna(value)

    elif method == "mode":

        for column in cleaned.columns:

            if cleaned[column].isnull().any():

                mode_values = cleaned[column].mode()

                if not mode_values.empty:
                    cleaned[column] = cleaned[column].fillna(
                        mode_values.iloc[0]
                    )

    elif method == "zero":

        cleaned = cleaned.fillna(0)

    else:
        raise ValueError("Invalid missing value handling method.")

    return cleaned


# =========================================================
# 03. REMOVE DUPLICATES
# =========================================================

def remove_duplicates(df):

    cleaned = df.copy()

    return cleaned.drop_duplicates().reset_index(drop=True)


# =========================================================
# 04. CONVERT DATA TYPES
# =========================================================

def convert_column_type(df, column, target_type):

    cleaned = df.copy()

    if column not in cleaned.columns:
        raise ValueError("Selected column does not exist.")

    if target_type == "numeric":

        cleaned[column] = pd.to_numeric(
            cleaned[column],
            errors="coerce"
        )

    elif target_type == "integer":

        converted = pd.to_numeric(
            cleaned[column],
            errors="coerce"
        )

        non_integer = converted.dropna() % 1 != 0

        if non_integer.any():
            raise ValueError(
                "Some values contain decimal numbers. "
                "Use Numeric instead of Integer."
            )

        cleaned[column] = converted.astype("Int64")

    elif target_type == "text":

        cleaned[column] = cleaned[column].astype("string")

    elif target_type == "datetime":

        cleaned[column] = pd.to_datetime(
            cleaned[column],
            errors="coerce"
        )

    else:
        raise ValueError("Invalid target data type.")

    return cleaned


# =========================================================
# 05. REMOVE COMPLETELY EMPTY ROWS
# =========================================================

def remove_empty_rows(df):

    cleaned = df.copy()

    return cleaned.dropna(how="all").reset_index(drop=True)


# =========================================================
# 06. REMOVE COLUMN
# =========================================================

def remove_column(df, column):

    cleaned = df.copy()

    if column not in cleaned.columns:
        raise ValueError("Selected column does not exist.")

    if len(cleaned.columns) <= 1:
        raise ValueError("At least one column must remain.")

    return cleaned.drop(columns=[column])


# =========================================================
# 07. RENAME COLUMN
# =========================================================

def rename_column(df, old_name, new_name):

    cleaned = df.copy()

    new_name = str(new_name).strip()

    if old_name not in cleaned.columns:
        raise ValueError("Selected column does not exist.")

    if not new_name:
        raise ValueError("New column name cannot be empty.")

    if new_name != old_name and new_name in cleaned.columns:
        raise ValueError("A column with this name already exists.")

    cleaned = cleaned.rename(
        columns={old_name: new_name}
    )

    return cleaned


# =========================================================
# 08. BACKWARD COMPATIBILITY
# =========================================================

def clean_dataset(df, fill_missing=True, remove_duplicates=True):

    cleaned = df.copy()

    if fill_missing:
        cleaned = handle_missing_values(cleaned, "median")
        cleaned = handle_missing_values(cleaned, "mode")

    if remove_duplicates:
        cleaned = remove_duplicates_operation(cleaned)

    return cleaned


def remove_duplicates_operation(df):

    return remove_duplicates(df)