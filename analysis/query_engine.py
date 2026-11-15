import re
import pandas as pd
import numpy as np


# =========================================================
# DATAPULSE — INTELLIGENT NATURAL LANGUAGE QUERY ENGINE
# =========================================================


# ---------------------------------------------------------
# 1. TEXT NORMALIZATION
# ---------------------------------------------------------

def normalize_text(text):
    text = str(text).lower().strip()
    text = text.replace("_", " ")
    text = re.sub(r"[^a-z0-9\s-]", " ", text)
    return re.sub(r"\s+", " ", text)


# ---------------------------------------------------------
# 2. COLUMN DETECTION
# ---------------------------------------------------------

def find_column(df, possible_names):

    columns = {
        normalize_text(column): column
        for column in df.columns
    }

    for name in possible_names:
        normalized = normalize_text(name)

        if normalized in columns:
            return columns[normalized]

    for column in df.columns:
        normalized_column = normalize_text(column)

        for name in possible_names:
            normalized_name = normalize_text(name)

            if (
                normalized_name in normalized_column
                or normalized_column in normalized_name
            ):
                return column

    return None


def detect_columns(df):

    return {
        "revenue": find_column(
            df,
            [
                "revenue", "total revenue", "sales",
                "total sales", "amount", "total amount"
            ]
        ),

        "profit": find_column(
            df,
            [
                "profit", "net profit",
                "total profit", "earnings"
            ]
        ),

        "quantity": find_column(
            df,
            [
                "quantity", "qty", "units",
                "units sold", "total quantity"
            ]
        ),

        "unit_price": find_column(
            df,
            [
                "unit price", "price",
                "selling price", "product price", "rate"
            ]
        ),

        "product": find_column(
            df,
            [
                "product", "product name",
                "item", "item name"
            ]
        ),

        "region": find_column(
            df,
            [
                "region", "area", "location",
                "zone", "territory"
            ]
        ),

        "category": find_column(
            df,
            [
                "category", "product category",
                "type", "segment"
            ]
        ),

        "date": find_column(
            df,
            [
                "date", "order date", "sales date",
                "transaction date", "purchase date",
                "created date"
            ]
        )
    }


# ---------------------------------------------------------
# 3. NUMERIC HELPERS
# ---------------------------------------------------------

def numeric_series(df, column):

    if column is None or column not in df.columns:
        return None

    values = (
        df[column]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("₹", "", regex=False)
        .str.replace("$", "", regex=False)
        .str.strip()
    )

    return pd.to_numeric(values, errors="coerce")


def get_numeric_column(df, possible_names):

    column = find_column(df, possible_names)

    if column is None:
        return None, None

    return column, numeric_series(df, column)


def format_number(value):

    try:
        return f"{float(value):,.2f}"
    except (ValueError, TypeError):
        return str(value)


# ---------------------------------------------------------
# 4. QUESTION HELPERS
# ---------------------------------------------------------

def contains_any(text, keywords):

    return any(keyword in text for keyword in keywords)


def is_average(question):

    return contains_any(
        question,
        ["average", "avg", "mean"]
    )


def is_maximum(question):

    return contains_any(
        question,
        ["highest", "maximum", "max", "top", "best", "most"]
    )


def is_minimum(question):

    return contains_any(
        question,
        ["lowest", "minimum", "min", "least", "worst"]
    )


# ---------------------------------------------------------
# 5. RESULT FORMAT
# ---------------------------------------------------------

def make_result(
    question,
    answer,
    details="",
    result_type="success"
):

    return {
        "question": question,
        "answer": answer,
        "details": details,
        "type": result_type
    }


# ---------------------------------------------------------
# 6. REVENUE CALCULATION
# ---------------------------------------------------------

def get_revenue_series(df, columns):

    revenue_column = columns["revenue"]

    if revenue_column:

        return numeric_series(
            df,
            revenue_column
        )

    quantity_column = columns["quantity"]
    price_column = columns["unit_price"]

    if quantity_column and price_column:

        quantity = numeric_series(
            df,
            quantity_column
        )

        price = numeric_series(
            df,
            price_column
        )

        return quantity * price

    return None


# ---------------------------------------------------------
# 7. GROUPED ANALYSIS
# ---------------------------------------------------------

def grouped_analysis(
    df,
    group_column,
    values,
    question,
    label="Value"
):

    if group_column is None or values is None:
        return None

    working = pd.DataFrame({
        "group": df[group_column],
        "value": values
    })

    working = working.dropna(
        subset=["group", "value"]
    )

    if working.empty:
        return None

    grouped = (
        working
        .groupby("group")["value"]
        .sum()
        .sort_values(ascending=False)
    )

    if grouped.empty:
        return None

    if is_minimum(question):

        best_name = grouped.idxmin()
        best_value = grouped.min()
        title = "Lowest Performing"

    else:

        best_name = grouped.idxmax()
        best_value = grouped.max()
        title = "Highest Performing"

    details = "\n".join(
        f"{name}: {label}: {format_number(value)}"
        for name, value in grouped.items()
    )

    return make_result(
        question,
        f"{title}: {best_name}",
        f"{label}: {format_number(best_value)}\n\n{details}"
    )


# ---------------------------------------------------------
# 8. PRODUCT COMPARISON
# ---------------------------------------------------------

def product_comparison(
    df,
    product_column,
    values,
    question,
    label="Revenue"
):

    if product_column is None or values is None:
        return None

    working = pd.DataFrame({
        "product": df[product_column].astype(str),
        "value": values
    })

    working = working.dropna(
        subset=["value"]
    )

    grouped = (
        working
        .groupby("product")["value"]
        .sum()
        .sort_values(ascending=False)
    )

    if grouped.empty:
        return None

    # Identify product names mentioned in the question
    matched_products = []

    normalized_question = normalize_text(question)

    for product in grouped.index:

        normalized_product = normalize_text(product)

        if (
            normalized_product
            and normalized_product in normalized_question
        ):
            matched_products.append(product)

    # Compare specifically mentioned products
    if len(matched_products) >= 2:

        comparison = grouped.loc[
            matched_products
        ].sort_values(ascending=False)

        winner = comparison.index[0]

        details = "\n".join(
            f"{name}: {label}: {format_number(value)}"
            for name, value in comparison.items()
        )

        return make_result(
            question,
            f"Better Performing Product: {winner}",
            details
        )

    # Otherwise show complete product ranking
    details = "\n".join(
        f"{index + 1}. {name}: {label}: {format_number(value)}"
        for index, (name, value) in enumerate(grouped.items())
    )

    return make_result(
        question,
        f"Top Performing Product: {grouped.idxmax()}",
        details
    )


# ---------------------------------------------------------
# 9. MONTHLY REVENUE ANALYSIS
# ---------------------------------------------------------

def monthly_revenue_analysis(
    df,
    date_column,
    revenue_values,
    question
):

    if date_column is None or revenue_values is None:
        return None

    dates = pd.to_datetime(
        df[date_column],
        errors="coerce"
    )

    working = pd.DataFrame({
        "date": dates,
        "revenue": revenue_values
    })

    working = working.dropna(
        subset=["date", "revenue"]
    )

    if working.empty:
        return None

    working["month"] = (
        working["date"].dt.to_period("M")
    )

    monthly = (
        working
        .groupby("month")["revenue"]
        .sum()
        .sort_index()
    )

    if monthly.empty:
        return None

    if (
        "best month" in question
        or "highest month" in question
        or (
            is_maximum(question)
            and "month" in question
        )
    ):

        best_month = monthly.idxmax()

        return make_result(
            question,
            f"Best Performing Month: {best_month.strftime('%B %Y')}",
            f"Total Revenue: ₹{format_number(monthly.max())}"
        )

    if (
        "worst month" in question
        or "lowest month" in question
        or (
            is_minimum(question)
            and "month" in question
        )
    ):

        worst_month = monthly.idxmin()

        return make_result(
            question,
            f"Lowest Performing Month: {worst_month.strftime('%B %Y')}",
            f"Total Revenue: ₹{format_number(monthly.min())}"
        )

    if is_average(question):

        return make_result(
            question,
            f"Average Monthly Revenue: ₹{format_number(monthly.mean())}",
            f"Months Analyzed: {len(monthly)}"
        )

    details = "\n".join(
        f"{month.strftime('%B %Y')}: ₹{format_number(value)}"
        for month, value in monthly.items()
    )

    return make_result(
        question,
        "Monthly Revenue Analysis Complete",
        details
    )


# ---------------------------------------------------------
# 10. DATE-WISE ANALYSIS
# ---------------------------------------------------------

def date_wise_analysis(
    df,
    date_column,
    values,
    question,
    label="Revenue"
):

    if date_column is None or values is None:
        return None

    dates = pd.to_datetime(
        df[date_column],
        errors="coerce"
    )

    working = pd.DataFrame({
        "date": dates,
        "value": values
    })

    working = working.dropna(
        subset=["date", "value"]
    )

    if working.empty:
        return None

    # Aggregate records date-wise
    working["date"] = working["date"].dt.date

    daily = (
        working
        .groupby("date")["value"]
        .sum()
        .sort_index()
    )

    if daily.empty:
        return None

    if is_maximum(question):

        best_date = daily.idxmax()

        return make_result(
            question,
            f"Highest {label} Date: {best_date}",
            f"{label}: {format_number(daily.max())}"
        )

    if is_minimum(question):

        worst_date = daily.idxmin()

        return make_result(
            question,
            f"Lowest {label} Date: {worst_date}",
            f"{label}: {format_number(daily.min())}"
        )

    details = "\n".join(
        f"{date}: {label}: {format_number(value)}"
        for date, value in daily.items()
    )

    return make_result(
        question,
        f"Date-wise {label} Analysis Complete",
        details
    )


# ---------------------------------------------------------
# 11. MAIN QUERY ENGINE
# ---------------------------------------------------------

def process_query(df, question):

    if df is None or df.empty:

        return make_result(
            question,
            "No dataset available.",
            "Please upload a dataset first.",
            "error"
        )

    original_question = str(question).strip()
    question = normalize_text(question)

    columns = detect_columns(df)

    revenue_values = get_revenue_series(
        df,
        columns
    )

    profit_column = columns["profit"]
    quantity_column = columns["quantity"]

    product_column = columns["product"]
    region_column = columns["region"]
    category_column = columns["category"]
    date_column = columns["date"]

    profit_values = (
        numeric_series(df, profit_column)
        if profit_column else None
    )

    quantity_values = (
        numeric_series(df, quantity_column)
        if quantity_column else None
    )

    # -----------------------------------------------------
    # 1. ROW COUNT
    # -----------------------------------------------------

    if contains_any(
        question,
        [
            "how many rows",
            "number of rows",
            "total records",
            "total rows",
            "record count",
            "how many records"
        ]
    ):

        return make_result(
            original_question,
            f"Total Records: {len(df):,}"
        )

    # -----------------------------------------------------
    # 2. COLUMN COUNT
    # -----------------------------------------------------

    if contains_any(
        question,
        [
            "how many columns",
            "number of columns",
            "total columns"
        ]
    ):

        return make_result(
            original_question,
            f"Total Columns: {len(df.columns)}",
            f"Columns: {', '.join(map(str, df.columns))}"
        )

    # -----------------------------------------------------
    # 3. COLUMN NAMES
    # -----------------------------------------------------

    if contains_any(
        question,
        [
            "show columns",
            "list columns",
            "column names",
            "dataset columns"
        ]
    ):

        return make_result(
            original_question,
            "Dataset Columns",
            ", ".join(map(str, df.columns))
        )

    # -----------------------------------------------------
    # 4. MONTHLY REVENUE
    # -----------------------------------------------------

    if (
        date_column
        and revenue_values is not None
        and contains_any(
            question,
            ["monthly", "month", "months"]
        )
    ):

        result = monthly_revenue_analysis(
            df,
            date_column,
            revenue_values,
            question
        )

        if result:
            return result

    # -----------------------------------------------------
    # 5. PRODUCT-WISE PROFIT
    # -----------------------------------------------------

    if (
        product_column
        and profit_values is not None
        and "profit" in question
        and contains_any(
            question,
            ["product", "item", "compare"]
        )
    ):

        result = product_comparison(
            df,
            product_column,
            profit_values,
            question,
            "Profit"
        )

        if result:
            return result

    # -----------------------------------------------------
    # 6. PRODUCT COMPARISON / PRODUCT REVENUE
    # -----------------------------------------------------

    if (
        product_column
        and revenue_values is not None
        and contains_any(
            question,
            [
                "compare",
                "product",
                "item",
                "best seller",
                "top selling"
            ]
        )
    ):

        result = product_comparison(
            df,
            product_column,
            revenue_values,
            question,
            "Revenue"
        )

        if result:
            return result

    # -----------------------------------------------------
    # 7. DATE-WISE ANALYSIS
    # -----------------------------------------------------

    if (
        date_column
        and revenue_values is not None
        and contains_any(
            question,
            [
                "date wise",
                "date-wise",
                "daily",
                "day wise",
                "day-wise",
                "by date"
            ]
        )
    ):

        result = date_wise_analysis(
            df,
            date_column,
            revenue_values,
            question,
            "Revenue"
        )

        if result:
            return result

    # -----------------------------------------------------
    # 8. PROFIT ANALYSIS
    # -----------------------------------------------------

    if (
        "profit" in question
        or "earning" in question
    ):

        if profit_values is None:

            return make_result(
                original_question,
                "Profit column not found.",
                "Your dataset does not contain a recognized profit column.",
                "error"
            )

        profits = profit_values.dropna()

        if profits.empty:

            return make_result(
                original_question,
                "No valid profit data found.",
                "",
                "error"
            )

        if is_average(question):

            return make_result(
                original_question,
                f"Average Profit: ₹{format_number(profits.mean())}",
                f"Total Profit: ₹{format_number(profits.sum())}"
            )

        if is_maximum(question):

            return make_result(
                original_question,
                f"Highest Profit: ₹{format_number(profits.max())}",
                f"Lowest Profit: ₹{format_number(profits.min())}"
            )

        if is_minimum(question):

            return make_result(
                original_question,
                f"Lowest Profit: ₹{format_number(profits.min())}",
                f"Highest Profit: ₹{format_number(profits.max())}"
            )

        return make_result(
            original_question,
            f"Total Profit: ₹{format_number(profits.sum())}",
            f"Average Profit: ₹{format_number(profits.mean())}"
        )

    # -----------------------------------------------------
    # 9. REGION ANALYSIS
    # -----------------------------------------------------

    if (
        region_column
        and contains_any(
            question,
            ["region", "area", "location", "zone"]
        )
    ):

        values = (
            profit_values
            if "profit" in question
            else revenue_values
            if revenue_values is not None
            else quantity_values
        )

        result = grouped_analysis(
            df,
            region_column,
            values,
            question,
            "Profit" if "profit" in question else "Revenue"
        )

        if result:
            return result

    # -----------------------------------------------------
    # 10. CATEGORY ANALYSIS
    # -----------------------------------------------------

    if (
        category_column
        and contains_any(
            question,
            ["category", "categories", "segment"]
        )
    ):

        values = (
            profit_values
            if "profit" in question
            else revenue_values
            if revenue_values is not None
            else quantity_values
        )

        result = grouped_analysis(
            df,
            category_column,
            values,
            question,
            "Profit" if "profit" in question else "Revenue"
        )

        if result:
            return result

    # -----------------------------------------------------
    # 11. REVENUE ANALYSIS
    # -----------------------------------------------------

    if (
        revenue_values is not None
        and contains_any(
            question,
            ["revenue", "sales", "selling", "turnover"]
        )
    ):

        revenue = revenue_values.dropna()

        if revenue.empty:

            return make_result(
                original_question,
                "No valid revenue data found.",
                "Please check your sales and price columns.",
                "error"
            )

        if is_average(question):

            return make_result(
                original_question,
                f"Average Revenue: ₹{format_number(revenue.mean())}",
                f"Total Revenue: ₹{format_number(revenue.sum())}"
            )

        if is_maximum(question):

            return make_result(
                original_question,
                f"Highest Revenue: ₹{format_number(revenue.max())}",
                f"Average Revenue: ₹{format_number(revenue.mean())}"
            )

        if is_minimum(question):

            return make_result(
                original_question,
                f"Lowest Revenue: ₹{format_number(revenue.min())}",
                f"Average Revenue: ₹{format_number(revenue.mean())}"
            )

        return make_result(
            original_question,
            f"Total Revenue: ₹{format_number(revenue.sum())}",
            f"Average Revenue: ₹{format_number(revenue.mean())}"
        )

    # -----------------------------------------------------
    # 12. QUANTITY ANALYSIS
    # -----------------------------------------------------

    if (
        quantity_values is not None
        and contains_any(
            question,
            [
                "quantity",
                "units",
                "unit sold",
                "items sold"
            ]
        )
    ):

        quantities = quantity_values.dropna()

        if quantities.empty:

            return make_result(
                original_question,
                "No valid quantity data found.",
                "",
                "error"
            )

        if is_average(question):

            return make_result(
                original_question,
                f"Average Quantity: {format_number(quantities.mean())}",
                f"Total Units Sold: {format_number(quantities.sum())}"
            )

        return make_result(
            original_question,
            f"Total Units Sold: {format_number(quantities.sum())}",
            f"Average Quantity: {format_number(quantities.mean())}"
        )

    # -----------------------------------------------------
    # 13. GENERAL FALLBACK
    # -----------------------------------------------------

    return make_result(
        original_question,
        "I couldn't understand this question.",
        (
            "Try asking:\n"
            "• What is the total revenue?\n"
            "• What is the average profit?\n"
            "• Which product has the highest sales?\n"
            "• Compare Laptop and Mouse.\n"
            "• Which product has the highest profit?\n"
            "• Which region performs best?\n"
            "• Show monthly revenue.\n"
            "• Which month had the highest revenue?\n"
            "• Show date-wise revenue.\n"
            "• How many units were sold?"
        ),
        "error"
    )