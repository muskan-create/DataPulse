import os
import pandas as pd


def load_dataset(file_path):

    extension = os.path.splitext(file_path.filename if hasattr(file_path, "filename") else file_path)[1].lower()

    if extension == ".csv":
        try:
            return pd.read_csv(file_path, encoding="utf-8-sig")
        except UnicodeDecodeError:
            if hasattr(file_path, "seek"):
                file_path.seek(0)
            return pd.read_csv(file_path, encoding="latin-1")

    elif extension in [".xlsx", ".xls"]:
        return pd.read_excel(file_path)

    raise ValueError("Unsupported file format")