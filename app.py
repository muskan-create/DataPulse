import os
import uuid
from io import BytesIO
from datetime import datetime

import numpy as np
import pandas as pd

from flask import (
    Flask, render_template, request,
    redirect, url_for, flash, session, send_file
)

from werkzeug.utils import secure_filename

from config import (
    UPLOAD_FOLDER,
    ALLOWED_EXTENSIONS,
    MAX_CONTENT_LENGTH,
    SECRET_KEY,
    SESSION_COOKIE_HTTPONLY,
    SESSION_COOKIE_SAMESITE,
    SESSION_COOKIE_SECURE
)

from utils import load_dataset

from database import (
    initialize_database,
    save_dataset,
    get_dataset_history,
    delete_dataset,
    get_dataset_by_id
)

from analysis.analyzer import analyze_dataset

from analysis.cleaner import (
    get_cleaning_report,
    handle_missing_values,
    remove_duplicates,
    convert_column_type,
    remove_empty_rows,
    remove_column,
    rename_column
)

from analysis.insights import (
    generate_insights,
    generate_recommendations
)

from analysis.query_engine import process_query
from analysis.comparator import compare_datasets

from visualization.charts import generate_chart
from reports.generator import generate_pdf_report


# =========================================================
# 01. APPLICATION CONFIGURATION
# =========================================================

app = Flask(__name__)

app.config.update(
    SECRET_KEY=SECRET_KEY,
    UPLOAD_FOLDER=UPLOAD_FOLDER,
    MAX_CONTENT_LENGTH=MAX_CONTENT_LENGTH,
    SESSION_COOKIE_HTTPONLY=SESSION_COOKIE_HTTPONLY,
    SESSION_COOKIE_SAMESITE=SESSION_COOKIE_SAMESITE,
    SESSION_COOKIE_SECURE=SESSION_COOKIE_SECURE
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

initialize_database()


# =========================================================
# 02. GENERAL HELPER FUNCTIONS
# =========================================================

def allowed_file(filename):

    if not filename or "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()

    return extension in ALLOWED_EXTENSIONS


def get_current_dataset():

    filename = session.get("dataset_filename")

    if not filename:
        return None

    filename = os.path.basename(filename)

    file_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    if not os.path.isfile(file_path):
        return None

    return load_dataset(file_path)


def find_column(dataset, possible_names):

    columns = list(dataset.columns)

    normalized = {
        str(column).strip().lower().replace("_", " "): column
        for column in columns
    }

    for name in possible_names:

        key = name.strip().lower().replace("_", " ")

        if key in normalized:
            return normalized[key]

    for name in possible_names:

        key = name.strip().lower().replace("_", " ")

        for normalized_name, original_name in normalized.items():

            if key in normalized_name:
                return original_name

    return None


def numeric_series(dataset, column):

    if not column:
        return None

    return pd.to_numeric(
        dataset[column],
        errors="coerce"
    )


def grouped_chart_data(
    dataset,
    group_column,
    value_column=None,
    limit=12
):

    if not group_column or group_column not in dataset.columns:
        return {
            "labels": [],
            "values": []
        }

    frame = dataset.copy()

    frame["_group"] = (
        frame[group_column]
        .fillna("Unknown")
        .astype(str)
    )

    if value_column and value_column in dataset.columns:

        frame["_value"] = numeric_series(
            frame,
            value_column
        )

        frame = frame.dropna(
            subset=["_value"]
        )

        grouped = (
            frame.groupby("_group")["_value"]
            .sum()
            .sort_values(ascending=False)
            .head(limit)
        )

    else:

        grouped = (
            frame["_group"]
            .value_counts()
            .head(limit)
        )

    return {
        "labels": grouped.index.astype(str).tolist(),
        "values": [
            float(value)
            for value in grouped.values
        ]
    }


# =========================================================
# 03. DASHBOARD DATA GENERATOR
# =========================================================

def generate_dashboard_data(dataset):

    numeric_columns = dataset.select_dtypes(
        include=np.number
    ).columns.tolist()

    categorical_columns = dataset.select_dtypes(
        include=["object", "category", "string"]
    ).columns.tolist()

    revenue_column = find_column(
        dataset,
        ["revenue", "sales", "total_sales", "amount", "total_amount"]
    )

    profit_column = find_column(
        dataset,
        ["profit", "net_profit", "earnings", "income"]
    )

    quantity_column = find_column(
        dataset,
        ["quantity", "units_sold", "units", "qty"]
    )

    product_column = find_column(
        dataset,
        ["product", "product_name", "item", "item_name"]
    )

    region_column = find_column(
        dataset,
        ["region", "location", "area", "branch", "city", "state"]
    )

    category_column = find_column(
        dataset,
        ["category", "product_category", "segment", "department"]
    )

    payment_column = find_column(
        dataset,
        ["payment_method", "payment", "payment_type", "method"]
    )

    date_column = find_column(
        dataset,
        [
            "date",
            "order_date",
            "transaction_date",
            "created_at",
            "timestamp"
        ]
    )

    revenue = numeric_series(
        dataset,
        revenue_column
    )

    profit = numeric_series(
        dataset,
        profit_column
    )

    quantity = numeric_series(
        dataset,
        quantity_column
    )

    rows = len(dataset)
    columns = len(dataset.columns)

    missing = int(
        dataset.isnull().sum().sum()
    )

    duplicates = int(
        dataset.duplicated().sum()
    )

    total_cells = max(rows * columns, 1)

    quality = round(
        max(
            0,
            100 - (
                (missing + duplicates) / total_cells * 100
            )
        ),
        1
    )

    stats = {
        "rows": rows,
        "columns": columns,
        "missing": missing,
        "duplicates": duplicates,
        "quality": quality,

        "revenue": float(revenue.sum()) if revenue is not None else 0,

        "profit": float(profit.sum()) if profit is not None else 0,

        "units": float(quantity.sum()) if quantity is not None else 0,

        "average_revenue": (
            float(revenue.mean())
            if revenue is not None and revenue.notna().any()
            else 0
        ),

        "average_profit": (
            float(profit.mean())
            if profit is not None and profit.notna().any()
            else 0
        ),

        "average_order_value": (
            float(revenue.sum() / rows)
            if revenue is not None and rows
            else 0
        )
    }

    charts = {
        "product": grouped_chart_data(
            dataset,
            product_column,
            revenue_column
        ),

        "region": grouped_chart_data(
            dataset,
            region_column,
            revenue_column
        ),

        "category": grouped_chart_data(
            dataset,
            category_column,
            revenue_column
        ),

        "payment": grouped_chart_data(
            dataset,
            payment_column
        ),

        "category_count": grouped_chart_data(
            dataset,
            category_column
        ),

        "region_count": grouped_chart_data(
            dataset,
            region_column
        ),

        "histogram": {
            "labels": [],
            "values": []
        },

        "trend": {
            "labels": [],
            "values": []
        },

        "profit_trend": {
            "labels": [],
            "values": []
        },

        "orders_trend": {
            "labels": [],
            "values": []
        },

        "scatter": {
            "x_label": "",
            "y_label": "",
            "points": []
        },

        "correlation": {
            "labels": [],
            "values": []
        }
    }

    # Date-based charts

    if date_column:

        date_frame = dataset.copy()

        date_frame["_date"] = pd.to_datetime(
            date_frame[date_column],
            errors="coerce"
        )

        date_frame = date_frame.dropna(
            subset=["_date"]
        )

        if not date_frame.empty:

            date_frame["_period"] = (
                date_frame["_date"]
                .dt.to_period("M")
                .astype(str)
            )

            if revenue_column:

                date_frame["_revenue"] = numeric_series(
                    date_frame,
                    revenue_column
                )

                trend = (
                    date_frame.groupby("_period")["_revenue"]
                    .sum()
                    .sort_index()
                )

                charts["trend"] = {
                    "labels": trend.index.tolist(),
                    "values": trend.astype(float).tolist()
                }

            if profit_column:

                date_frame["_profit"] = numeric_series(
                    date_frame,
                    profit_column
                )

                trend = (
                    date_frame.groupby("_period")["_profit"]
                    .sum()
                    .sort_index()
                )

                charts["profit_trend"] = {
                    "labels": trend.index.tolist(),
                    "values": trend.astype(float).tolist()
                }

            order_counts = (
                date_frame.groupby("_period")
                .size()
                .sort_index()
            )

            charts["orders_trend"] = {
                "labels": order_counts.index.tolist(),
                "values": order_counts.astype(int).tolist()
            }

    # Histogram

    if numeric_columns:

        histogram_column = (
            revenue_column or numeric_columns[0]
        )

        values = numeric_series(
            dataset,
            histogram_column
        ).dropna()

        if not values.empty:

            counts, edges = np.histogram(
                values,
                bins=min(10, max(3, values.nunique()))
            )

            charts["histogram"] = {
                "labels": [
                    (
                        f"{edges[index]:,.1f} - "
                        f"{edges[index + 1]:,.1f}"
                    )
                    for index in range(len(counts))
                ],

                "values": counts.astype(int).tolist()
            }

    # Scatter chart

    if len(numeric_columns) >= 2:

        x_column = numeric_columns[0]
        y_column = numeric_columns[1]

        scatter_frame = dataset[
            [x_column, y_column]
        ].apply(
            pd.to_numeric,
            errors="coerce"
        ).dropna().head(500)

        charts["scatter"] = {
            "x_label": str(x_column),
            "y_label": str(y_column),

            "points": [
                {
                    "x": float(x),
                    "y": float(y)
                }
                for x, y in zip(
                    scatter_frame[x_column],
                    scatter_frame[y_column]
                )
            ]
        }

    # Correlation

    if len(numeric_columns) >= 2:

        correlation = dataset[numeric_columns].corr().round(2)

        charts["correlation"] = {
            "labels": correlation.columns.astype(str).tolist(),
            "values": correlation.fillna(0).values.tolist()
        }

    product_data = [
        {
            "label": label,
            "value": value
        }
        for label, value in zip(
            charts["product"]["labels"],
            charts["product"]["values"]
        )
    ]

    region_data = [
        {
            "label": label,
            "value": value
        }
        for label, value in zip(
            charts["region"]["labels"],
            charts["region"]["values"]
        )
    ]

    category_data = [
        {
            "label": label,
            "value": value
        }
        for label, value in zip(
            charts["category_count"]["labels"],
            charts["category_count"]["values"]
        )
    ]

    return {
        "stats": stats,
        "charts": charts,
        "product_data": product_data,
        "region_data": region_data,
        "category_data": category_data,
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns
    }


# =========================================================
# 04. ERROR HANDLER
# =========================================================

@app.errorhandler(413)
def file_too_large(error):

    flash(
        "File is too large. Maximum upload size is 20 MB."
    )

    return redirect(
        url_for("dashboard")
    )


# =========================================================
# 05. HOME
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================================
# 06. DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    stats = None
    columns = []
    preview = []
    missing_values = {}

    product_data = []
    region_data = []
    category_data = []
    charts = {}

    filename = session.get("dataset_filename")

    try:

        dataset = get_current_dataset()

        if dataset is not None and not dataset.empty:

            dashboard_data = generate_dashboard_data(
                dataset
            )

            stats = dashboard_data["stats"]
            charts = dashboard_data["charts"]

            product_data = dashboard_data["product_data"]
            region_data = dashboard_data["region_data"]
            category_data = dashboard_data["category_data"]

            columns = dataset.columns.tolist()

            preview = (
                dataset.head(10)
                .fillna("")
                .astype(str)
                .to_dict(orient="records")
            )

            missing_values = {
                str(column): int(count)
                for column, count in dataset.isnull().sum().items()
            }

    except Exception:

        app.logger.exception(
            "Dashboard data calculation failed"
        )

        flash(
            "Unable to calculate dashboard statistics."
        )

    return render_template(
        "dashboard.html",
        stats=stats,
        columns=columns,
        preview=preview,
        missing_values=missing_values,
        filename=filename,
        product_data=product_data,
        region_data=region_data,
        category_data=category_data,
        charts=charts
    )


# =========================================================
# 07. DATASET UPLOAD
# =========================================================

@app.route("/upload", methods=["POST"])
def upload():

    if "dataset" not in request.files:

        flash("No file selected.")

        return redirect(
            url_for("dashboard")
        )

    file = request.files["dataset"]

    if not file.filename:

        flash("Please select a file.")

        return redirect(
            url_for("dashboard")
        )

    if not allowed_file(file.filename):

        flash("Please upload a CSV or Excel file.")

        return redirect(
            url_for("dashboard")
        )

    original_name = secure_filename(
        file.filename
    )

    if not original_name:

        flash("Invalid filename.")

        return redirect(
            url_for("dashboard")
        )

    extension = original_name.rsplit(".", 1)[1].lower()

    unique_name = f"{uuid.uuid4().hex}.{extension}"

    file_path = os.path.join(
        UPLOAD_FOLDER,
        unique_name
    )

    try:

        file.save(file_path)

        dataset = load_dataset(file_path)

        if (
            dataset is None
            or dataset.empty
            or len(dataset.columns) == 0
        ):
            raise ValueError(
                "The uploaded dataset is empty."
            )

        save_dataset(
            original_name,
            unique_name,
            len(dataset),
            len(dataset.columns)
        )

        session["dataset_filename"] = unique_name
        session["original_filename"] = original_name
        session["original_dataset_filename"] = unique_name

        session.pop("cleaning_working_filename", None)
        session.pop("cleaning_history", None)

        session.modified = True

        flash(
            "New dataset uploaded successfully. Dashboard updated!"
        )

    except Exception:

        if os.path.exists(file_path):
            os.remove(file_path)

        app.logger.exception(
            "Dataset upload failed"
        )

        flash(
            "Upload failed. Please check your file and try again."
        )

    return redirect(
        url_for("dashboard")
    )


# =========================================================
# 08. ANALYTICS
# =========================================================

@app.route("/analytics")
def analytics():

    dataset = get_current_dataset()

    analysis = None

    try:

        if dataset is not None:
            analysis = analyze_dataset(dataset)

        else:
            flash(
                "Please upload a dataset first."
            )

    except Exception as error:

        app.logger.exception(
            "Analytics failed"
        )

        flash(
            f"Analytics error: {error}"
        )

    return render_template(
        "analytics.html",
        analysis=analysis
    )


# =========================================================
# 09. DATA CLEANING STUDIO HELPERS
# =========================================================

def get_cleaning_files():

    original_filename = session.get(
        "original_dataset_filename"
    )

    if not original_filename:

        original_filename = session.get(
            "dataset_filename"
        )

        if not original_filename:
            raise ValueError(
                "Please upload a dataset first."
            )

        session["original_dataset_filename"] = original_filename

    original_path = os.path.join(
        UPLOAD_FOLDER,
        os.path.basename(original_filename)
    )

    if not os.path.isfile(original_path):
        raise FileNotFoundError(
            "Original dataset file not found."
        )

    original_df = load_dataset(original_path)

    working_filename = session.get(
        "cleaning_working_filename"
    )

    working_path = None

    if working_filename:

        working_path = os.path.join(
            UPLOAD_FOLDER,
            os.path.basename(working_filename)
        )

    if (
        not working_path
        or not os.path.isfile(working_path)
    ):

        working_filename = (
            f"working_{uuid.uuid4().hex}.csv"
        )

        working_path = os.path.join(
            UPLOAD_FOLDER,
            working_filename
        )

        original_df.to_csv(
            working_path,
            index=False
        )

        session["cleaning_working_filename"] = working_filename

    cleaned_df = load_dataset(
        working_path
    )

    session["dataset_filename"] = working_filename

    session.modified = True

    return original_df, cleaned_df


def save_cleaning_result(
    dataset,
    operation,
    details
):

    filename = f"working_{uuid.uuid4().hex}.csv"

    file_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    dataset.to_csv(
        file_path,
        index=False
    )

    old_filename = session.get(
        "cleaning_working_filename"
    )

    session["cleaning_working_filename"] = filename
    session["dataset_filename"] = filename

    history = session.get(
        "cleaning_history",
        []
    )

    history.insert(
        0,
        {
            "operation": operation,
            "details": details,
            "time": datetime.now().strftime(
                "%d %b %Y, %I:%M %p"
            )
        }
    )

    session["cleaning_history"] = history[:30]

    session.modified = True

    if old_filename and old_filename != filename:

        old_path = os.path.join(
            UPLOAD_FOLDER,
            os.path.basename(old_filename)
        )

        original_filename = session.get(
            "original_dataset_filename"
        )

        if (
            os.path.isfile(old_path)
            and old_filename != original_filename
        ):

            try:
                os.remove(old_path)

            except OSError:

                app.logger.exception(
                    "Could not remove previous working file"
                )


def cleaning_preview(dataset, limit=8):

    preview = dataset.head(limit).copy()

    preview = preview.astype("string").fillna("")

    return preview.values.tolist()


# =========================================================
# 10. CLEANING MAIN PAGE
# =========================================================

@app.route("/cleaning")
def cleaning():

    try:

        original_df, cleaned_df = get_cleaning_files()

        report = get_cleaning_report(
            cleaned_df
        )

        return render_template(
            "cleaning.html",

            total_rows=report["rows"],
            total_columns=report["columns"],
            missing_values=report["total_missing"],
            duplicate_rows=report["duplicates"],
            quality_score=report["quality_score"],

            columns=cleaned_df.columns.tolist(),

            original_preview=cleaning_preview(
                original_df
            ),

            cleaned_columns=cleaned_df.columns.tolist(),

            cleaned_preview=cleaning_preview(
                cleaned_df
            ),

            cleaning_history=session.get(
                "cleaning_history",
                []
            )
        )

    except Exception as error:

        app.logger.exception(
            "Cleaning page failed"
        )

        flash(
            f"Unable to open Cleaning Studio: {error}"
        )

        return redirect(
            url_for("dashboard")
        )


# =========================================================
# 11. HANDLE MISSING VALUES
# =========================================================

@app.route(
    "/cleaning/handle-missing",
    methods=["POST"]
)
def handle_missing_route():

    try:

        _, dataset = get_cleaning_files()

        method = request.form.get(
            "method",
            ""
        ).strip()

        cleaned = handle_missing_values(
            dataset,
            method
        )

        save_cleaning_result(
            cleaned,
            "Missing Values",
            f"Applied {method} method"
        )

        flash(
            "Missing values handled successfully!"
        )

    except Exception as error:

        app.logger.exception(
            "Missing value handling failed"
        )

        flash(
            f"Cleaning failed: {error}"
        )

    return redirect(
        url_for("cleaning")
    )


# =========================================================
# 12. REMOVE DUPLICATES
# =========================================================

@app.route(
    "/cleaning/remove-duplicates",
    methods=["POST"]
)
def cleaning_remove_duplicates():

    try:

        _, dataset = get_cleaning_files()

        cleaned = remove_duplicates(
            dataset
        )

        removed = len(dataset) - len(cleaned)

        save_cleaning_result(
            cleaned,
            "Remove Duplicates",
            f"{removed} duplicate rows removed"
        )

        flash(
            f"{removed} duplicate rows removed."
        )

    except Exception as error:

        app.logger.exception(
            "Duplicate removal failed"
        )

        flash(
            f"Operation failed: {error}"
        )

    return redirect(
        url_for("cleaning")
    )


# =========================================================
# 13. CONVERT DATA TYPE
# =========================================================

@app.route(
    "/cleaning/convert-type",
    methods=["POST"]
)
def cleaning_convert_type():

    try:

        _, dataset = get_cleaning_files()

        column = request.form.get("column")
        target_type = request.form.get("target_type")

        cleaned = convert_column_type(
            dataset,
            column,
            target_type
        )

        save_cleaning_result(
            cleaned,
            "Data Type Conversion",
            f"{column} converted to {target_type}"
        )

        flash(
            f"{column} converted successfully!"
        )

    except Exception as error:

        app.logger.exception(
            "Data type conversion failed"
        )

        flash(
            f"Conversion failed: {error}"
        )

    return redirect(
        url_for("cleaning")
    )


# =========================================================
# 14. REMOVE EMPTY ROWS
# =========================================================

@app.route(
    "/cleaning/remove-empty-rows",
    methods=["POST"]
)
def cleaning_remove_empty_rows():

    try:

        _, dataset = get_cleaning_files()

        cleaned = remove_empty_rows(
            dataset
        )

        removed = len(dataset) - len(cleaned)

        save_cleaning_result(
            cleaned,
            "Remove Empty Rows",
            f"{removed} empty rows removed"
        )

        flash(
            f"{removed} empty rows removed."
        )

    except Exception as error:

        app.logger.exception(
            "Empty row removal failed"
        )

        flash(
            f"Operation failed: {error}"
        )

    return redirect(
        url_for("cleaning")
    )


# =========================================================
# 15. REMOVE COLUMN
# =========================================================

@app.route(
    "/cleaning/remove-column",
    methods=["POST"]
)
def cleaning_remove_column():

    try:

        _, dataset = get_cleaning_files()

        column = request.form.get(
            "column"
        )

        cleaned = remove_column(
            dataset,
            column
        )

        save_cleaning_result(
            cleaned,
            "Remove Column",
            f"Removed column: {column}"
        )

        flash(
            f"{column} removed successfully!"
        )

    except Exception as error:

        app.logger.exception(
            "Column removal failed"
        )

        flash(
            f"Operation failed: {error}"
        )

    return redirect(
        url_for("cleaning")
    )


# =========================================================
# 16. RENAME COLUMN
# =========================================================

@app.route(
    "/cleaning/rename-column",
    methods=["POST"]
)
def cleaning_rename_column():

    try:

        _, dataset = get_cleaning_files()

        old_name = request.form.get(
            "old_name"
        )

        new_name = request.form.get(
            "new_name"
        )

        cleaned = rename_column(
            dataset,
            old_name,
            new_name
        )

        save_cleaning_result(
            cleaned,
            "Rename Column",
            f"{old_name} renamed to {new_name}"
        )

        flash(
            "Column renamed successfully!"
        )

    except Exception as error:

        app.logger.exception(
            "Column rename failed"
        )

        flash(
            f"Rename failed: {error}"
        )

    return redirect(
        url_for("cleaning")
    )


# =========================================================
# 17. DOWNLOAD CLEANED CSV
# =========================================================

@app.route(
    "/cleaning/download/csv"
)
def download_cleaning_csv():

    try:

        _, dataset = get_cleaning_files()

        buffer = BytesIO()

        dataset.to_csv(
            buffer,
            index=False,
            encoding="utf-8-sig"
        )

        buffer.seek(0)

        return send_file(
            buffer,
            mimetype="text/csv",
            as_attachment=True,
            download_name="DataPulse_Cleaned_Dataset.csv"
        )

    except Exception as error:

        app.logger.exception(
            "CSV download failed"
        )

        flash(
            f"CSV download failed: {error}"
        )

        return redirect(
            url_for("cleaning")
        )


# =========================================================
# 18. DOWNLOAD CLEANED EXCEL
# =========================================================

@app.route(
    "/cleaning/download/excel"
)
def download_cleaning_excel():

    try:

        _, dataset = get_cleaning_files()

        buffer = BytesIO()

        dataset.to_excel(
            buffer,
            index=False,
            engine="openpyxl"
        )

        buffer.seek(0)

        return send_file(
            buffer,
            mimetype=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            as_attachment=True,
            download_name="DataPulse_Cleaned_Dataset.xlsx"
        )

    except Exception as error:

        app.logger.exception(
            "Excel download failed"
        )

        flash(
            f"Excel download failed: {error}"
        )

        return redirect(
            url_for("cleaning")
        )


# =========================================================
# 19. RESET TO ORIGINAL DATASET
# =========================================================

@app.route(
    "/cleaning/reset",
    methods=["POST"]
)
def reset_cleaning():

    try:

        original_filename = session.get(
            "original_dataset_filename"
        )

        if not original_filename:

            raise ValueError(
                "Original dataset not found."
            )

        original_path = os.path.join(
            UPLOAD_FOLDER,
            os.path.basename(original_filename)
        )

        if not os.path.isfile(original_path):

            raise FileNotFoundError(
                "Original file not found."
            )

        working_filename = session.get(
            "cleaning_working_filename"
        )

        if working_filename:

            working_path = os.path.join(
                UPLOAD_FOLDER,
                os.path.basename(working_filename)
            )

            if (
                os.path.isfile(working_path)
                and working_filename != original_filename
            ):

                os.remove(working_path)

        session["dataset_filename"] = original_filename

        session.pop(
            "cleaning_working_filename",
            None
        )

        session.pop(
            "cleaning_history",
            None
        )

        session.modified = True

        flash(
            "Original dataset restored successfully!"
        )

    except Exception as error:

        app.logger.exception(
            "Dataset reset failed"
        )

        flash(
            f"Reset failed: {error}"
        )

    return redirect(
        url_for("cleaning")
    )


# =========================================================
# 20. BACKWARD-COMPATIBLE CLEANED DOWNLOAD
# =========================================================

@app.route("/download-cleaned")
def download_cleaned():

    return redirect(
        url_for("download_cleaning_csv")
    )


# =========================================================
# 21. VISUALIZATION
# =========================================================

@app.route(
    "/visualization",
    methods=["GET", "POST"]
)
def visualization():

    dataset = get_current_dataset()

    if dataset is None:

        flash(
            "Please upload a dataset first."
        )

        return redirect(
            url_for("dashboard")
        )

    numerical_columns = dataset.select_dtypes(
        include=np.number
    ).columns.tolist()

    categorical_columns = dataset.select_dtypes(
        include=["object", "category"]
    ).columns.tolist()

    chart_filename = None

    if request.method == "POST":

        chart_type = request.form.get(
            "chart_type"
        )

        x_column = request.form.get(
            "x_column"
        )

        y_column = request.form.get(
            "y_column"
        )

        try:

            if x_column not in dataset.columns:

                raise ValueError(
                    "Invalid X-axis column."
                )

            if chart_type in [
                "bar",
                "line",
                "scatter"
            ]:

                if y_column not in numerical_columns:

                    raise ValueError(
                        "Please select a valid numerical Y-axis column."
                    )

            if chart_type == "histogram":

                if x_column not in numerical_columns:

                    raise ValueError(
                        "Histogram requires a numerical column."
                    )

            chart_filename = generate_chart(
                dataset,
                chart_type,
                x_column,
                y_column
            )

        except Exception as error:

            flash(
                f"Chart generation failed: {error}"
            )

    return render_template(
        "visualization.html",
        numerical_columns=numerical_columns,
        categorical_columns=categorical_columns,
        all_columns=dataset.columns.tolist(),
        chart_filename=chart_filename
    )


# =========================================================
# 22. INSIGHT AI
# =========================================================

@app.route("/insights")
def insights():

    dataset = get_current_dataset()

    if dataset is None:

        flash(
            "Please upload a dataset first."
        )

        return redirect(
            url_for("dashboard")
        )

    try:

        insight_data = generate_insights(
            dataset
        )

        recommendations = generate_recommendations(
            dataset
        )

        return render_template(
            "insights.html",
            insights=insight_data,
            recommendations=recommendations
        )

    except Exception as error:

        app.logger.exception(
            "InsightAI failed"
        )

        flash(
            f"InsightAI error: {error}"
        )

        return redirect(
            url_for("dashboard")
        )


# =========================================================
# 23. VISUAL QUERY
# =========================================================

@app.route(
    "/visualquery",
    methods=["GET", "POST"]
)
def visualquery():

    dataset = get_current_dataset()

    result = None

    if dataset is None:

        flash(
            "Please upload a dataset first."
        )

        return render_template(
            "visualquery.html",
            result=None
        )

    if request.method == "POST":

        question = request.form.get(
            "question",
            ""
        ).strip()

        if question:

            result = process_query(
                dataset,
                question
            )

    return render_template(
        "visualquery.html",
        result=result
    )
# =========================================================
# DATAPULSE — DATASET COMPARISON ENGINE
# =========================================================

def compare_datasets(df1, df2):

    if df1 is None or df2 is None:
        raise ValueError("Both datasets are required.")

    if df1.empty or df2.empty:
        raise ValueError("Both datasets must contain data.")

    # Dataset statistics
    dataset1_rows = len(df1)
    dataset2_rows = len(df2)

    dataset1_columns = len(df1.columns)
    dataset2_columns = len(df2.columns)

    dataset1_missing = int(df1.isna().sum().sum())
    dataset2_missing = int(df2.isna().sum().sum())

    # Column comparison
    columns1 = set(df1.columns)
    columns2 = set(df2.columns)

    common_columns = sorted(
        columns1.intersection(columns2)
    )

    only_dataset1 = sorted(
        columns1 - columns2
    )

    only_dataset2 = sorted(
        columns2 - columns1
    )

    # Numerical comparison
    numerical_comparison = {}

    for column in common_columns:

        values1 = pd.to_numeric(
            df1[column]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("₹", "", regex=False)
            .str.replace("$", "", regex=False),
            errors="coerce"
        )

        values2 = pd.to_numeric(
            df2[column]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("₹", "", regex=False)
            .str.replace("$", "", regex=False),
            errors="coerce"
        )

        if (
            values1.notna().sum() == 0
            or values2.notna().sum() == 0
        ):
            continue

        mean1 = float(values1.mean())
        mean2 = float(values2.mean())

        difference = mean2 - mean1

        percentage_change = (
            (difference / abs(mean1)) * 100
            if mean1 != 0
            else None
        )

        numerical_comparison[column] = {

            "dataset1_mean": round(mean1, 2),

            "dataset2_mean": round(mean2, 2),

            "difference": round(difference, 2),

            "percentage_change": (
                round(percentage_change, 2)
                if percentage_change is not None
                else None
            )
        }

    return {

        "dataset1_rows": dataset1_rows,
        "dataset2_rows": dataset2_rows,

        "dataset1_columns": dataset1_columns,
        "dataset2_columns": dataset2_columns,

        "dataset1_missing": dataset1_missing,
        "dataset2_missing": dataset2_missing,

        "common_columns": common_columns,

        "only_dataset1": only_dataset1,
        "only_dataset2": only_dataset2,

        "numerical_comparison": numerical_comparison
    }


# =========================================================
# 24. DATASET COMPARISON
# =========================================================

@app.route(
    "/comparison",
    methods=["GET", "POST"]
)
def comparison():

    comparison_result = None

    if request.method == "POST":

        file1 = request.files.get(
            "dataset1"
        )

        file2 = request.files.get(
            "dataset2"
        )

        if (
            not file1
            or not file2
            or not file1.filename
            or not file2.filename
        ):

            flash(
                "Please select both datasets."
            )

        elif (
            not allowed_file(file1.filename)
            or not allowed_file(file2.filename)
        ):

            flash(
                "Only CSV and Excel files are supported."
            )

        else:

            try:

                df1 = load_dataset(file1)
                df2 = load_dataset(file2)

                if df1.empty or df2.empty:

                    raise ValueError(
                        "Both datasets must contain data."
                    )

                comparison_result = compare_datasets(
                    df1,
                    df2
                )

            except Exception as error:

                app.logger.exception(
                    "Dataset comparison failed"
                )

                flash(
                    f"Comparison failed: {error}"
                )

    return render_template(
        "comparison.html",
        comparison=comparison_result
    )


# =========================================================
# 25. REPORTS
# =========================================================

@app.route("/reports")
def reports_page():

    dataset = get_current_dataset()

    if dataset is None:

        return render_template(
            "reports.html",
            has_dataset=False
        )

    return render_template(
        "reports.html",
        has_dataset=True,
        rows=len(dataset),
        columns=len(dataset.columns),
        missing=int(
            dataset.isnull().sum().sum()
        ),
        duplicates=int(
            dataset.duplicated().sum()
        )
    )


# =========================================================
# 26. EXPORT CSV
# =========================================================

@app.route("/export-csv")
def export_csv():

    dataset = get_current_dataset()

    if dataset is None:

        flash(
            "Please upload a dataset first."
        )

        return redirect(
            url_for("reports_page")
        )

    csv_buffer = dataset.to_csv(
        index=False
    ).encode("utf-8-sig")

    return send_file(
        BytesIO(csv_buffer),
        mimetype="text/csv",
        as_attachment=True,
        download_name="DataPulse_Export.csv"
    )


# =========================================================
# 27. EXPORT PDF
# =========================================================

@app.route("/export-pdf")
def export_pdf():

    dataset = get_current_dataset()

    if dataset is None:

        flash(
            "Please upload a dataset first."
        )

        return redirect(
            url_for("reports_page")
        )

    try:

        pdf_buffer = generate_pdf_report(
            dataset
        )

        return send_file(
            pdf_buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name="DataPulse_Analytics_Report.pdf"
        )

    except Exception as error:

        app.logger.exception(
            "PDF generation failed"
        )

        flash(
            f"PDF generation failed: {error}"
        )

        return redirect(
            url_for("reports_page")
        )


# =========================================================
# 28. DATASET HISTORY
# =========================================================

@app.route("/history")
def history():

    datasets = get_dataset_history()

    return render_template(
        "history.html",
        datasets=datasets
    )


# =========================================================
# 29. LOAD OLD DATASET
# =========================================================

@app.route("/load-dataset/<int:dataset_id>")
def load_old_dataset(dataset_id):

    selected = get_dataset_by_id(
        dataset_id
    )

    if selected is None:

        flash(
            "Dataset not found.",
            "error"
        )

        return redirect(
            url_for("history")
        )

    filename = os.path.basename(
        selected["file_path"]
    )

    file_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    if not os.path.isfile(file_path):

        flash(
            "Dataset file is missing.",
            "error"
        )

        return redirect(
            url_for("history")
        )

    session["dataset_filename"] = filename

    session["original_filename"] = selected["dataset_name"]

    session["original_dataset_filename"] = filename

    session.pop(
        "cleaning_working_filename",
        None
    )

    session.pop(
        "cleaning_history",
        None
    )

    session.modified = True

    flash(
        "Dataset loaded successfully!",
        "success"
    )

    return redirect(
        url_for("dashboard")
    )


# =========================================================
# 30. DELETE DATASET
# =========================================================

@app.route(
    "/delete-dataset/<int:dataset_id>",
    methods=["POST"]
)
def remove_dataset(dataset_id):

    deleted_path = delete_dataset(
        dataset_id
    )

    if deleted_path is None:

        flash(
            "Dataset record not found.",
            "error"
        )

        return redirect(
            url_for("history")
        )

    filename = os.path.basename(
        deleted_path
    )

    file_path = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    if (
        session.get("dataset_filename") == filename
        or session.get("original_dataset_filename") == filename
    ):

        session.pop(
            "dataset_filename",
            None
        )

        session.pop(
            "original_filename",
            None
        )

        session.pop(
            "original_dataset_filename",
            None
        )

        session.pop(
            "cleaning_working_filename",
            None
        )

        session.pop(
            "cleaning_history",
            None
        )

        session.modified = True

    if os.path.isfile(file_path):

        try:

            os.remove(file_path)

        except OSError:

            app.logger.exception(
                "Could not delete dataset file"
            )

    flash(
        "Dataset deleted successfully.",
        "success"
    )

    return redirect(
        url_for("history")
    )


# =========================================================
# 31. RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(debug=True)