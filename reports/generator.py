from io import BytesIO
from xml.sax.saxutils import escape

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import inch

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)


# =========================================================
# DATAPULSE — PROFESSIONAL PDF REPORT GENERATOR
# =========================================================

PRIMARY = colors.HexColor("#657a63")
DARK = colors.HexColor("#26352d")
LIGHT = colors.HexColor("#eef2ec")
BORDER = colors.HexColor("#d5ddd2")
TEXT = colors.HexColor("#344239")
MUTED = colors.HexColor("#718078")


def safe_text(value, limit=100):

    if pd.isna(value):
        return "-"

    text = str(value)

    if len(text) > limit:
        text = text[:limit] + "..."

    return escape(text)


def make_table(data, widths=None, font_size=8):

    table = Table(
        data,
        colWidths=widths,
        repeatRows=1,
        hAlign="LEFT"
    )

    table.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),

        ("BACKGROUND", (0, 1), (-1, -1), LIGHT),
        ("TEXTCOLOR", (0, 1), (-1, -1), TEXT),

        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),

        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),

        ("FONTSIZE", (0, 0), (-1, -1), font_size),

        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),

    ]))

    return table


def generate_pdf_report(df):

    buffer = BytesIO()

    page_width, page_height = landscape(A4)

    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=35,
        leftMargin=35,
        topMargin=55,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=23,
        leading=28,
        textColor=DARK,
        alignment=TA_LEFT,
        spaceAfter=8
    ))

    styles.add(ParagraphStyle(
        name="ReportSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=MUTED,
        leading=15
    ))

    styles.add(ParagraphStyle(
        name="SectionHeading",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        textColor=DARK,
        spaceBefore=15,
        spaceAfter=10
    ))

    styles.add(ParagraphStyle(
        name="SmallText",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        textColor=TEXT
    ))

    content = []

    # -----------------------------------------------------
    # HEADER
    # -----------------------------------------------------

    content.append(
        Paragraph(
            "DataPulse Analytics Report",
            styles["ReportTitle"]
        )
    )

    content.append(
        Paragraph(
            "Automated Dataset Analysis and Summary",
            styles["ReportSubtitle"]
        )
    )

    content.append(Spacer(1, 20))

    # -----------------------------------------------------
    # DATASET SUMMARY
    # -----------------------------------------------------

    total_rows = len(df)
    total_columns = len(df.columns)

    missing_total = int(df.isnull().sum().sum())
    duplicate_total = int(df.duplicated().sum())

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    categorical_columns = df.select_dtypes(
        include=["object", "category", "bool"]
    ).columns

    total_cells = total_rows * total_columns

    if total_cells > 0:
        quality_score = (
            (total_cells - missing_total) / total_cells
        ) * 100
    else:
        quality_score = 0

    summary_data = [
        ["DATASET METRIC", "VALUE"],

        ["Total Records", str(total_rows)],
        ["Total Columns", str(total_columns)],
        ["Missing Values", str(missing_total)],
        ["Duplicate Rows", str(duplicate_total)],
        ["Numerical Columns", str(len(numeric_columns))],
        ["Categorical Columns", str(len(categorical_columns))],
        ["Data Completeness", f"{quality_score:.2f}%"]
    ]

    content.append(
        Paragraph("Dataset Overview", styles["SectionHeading"])
    )

    content.append(
        make_table(
            summary_data,
            widths=[250, 250]
        )
    )

    # -----------------------------------------------------
    # DATA QUALITY ANALYSIS
    # -----------------------------------------------------

    content.append(
        Paragraph("Data Quality Analysis", styles["SectionHeading"])
    )

    missing_data = [
        ["COLUMN NAME", "MISSING VALUES", "MISSING %"]
    ]

    for column in df.columns:

        missing_count = int(df[column].isnull().sum())

        missing_percentage = (
            (missing_count / total_rows) * 100
            if total_rows > 0 else 0
        )

        missing_data.append([
            safe_text(column),
            str(missing_count),
            f"{missing_percentage:.2f}%"
        ])

    if len(missing_data) > 1:

        content.append(
            make_table(
                missing_data,
                widths=[300, 150, 150]
            )
        )

    # -----------------------------------------------------
    # NUMERICAL ANALYSIS
    # -----------------------------------------------------

    content.append(
        Paragraph("Numerical Analysis", styles["SectionHeading"])
    )

    numerical_data = [
        [
            "COLUMN",
            "COUNT",
            "MEAN",
            "MEDIAN",
            "MINIMUM",
            "MAXIMUM",
            "STD DEV"
        ]
    ]

    for column in numeric_columns:

        series = pd.to_numeric(
            df[column],
            errors="coerce"
        ).dropna()

        if series.empty:
            continue

        numerical_data.append([

            safe_text(column, 30),

            str(len(series)),

            f"{series.mean():,.2f}",

            f"{series.median():,.2f}",

            f"{series.min():,.2f}",

            f"{series.max():,.2f}",

            f"{series.std():,.2f}" if len(series) > 1 else "0.00"

        ])

    if len(numerical_data) > 1:

        content.append(
            make_table(
                numerical_data,
                widths=[
                    120, 65, 90, 90, 90, 90, 90
                ]
            )
        )

    else:

        content.append(
            Paragraph(
                "No numerical columns found in this dataset.",
                styles["SmallText"]
            )
        )

    # -----------------------------------------------------
    # CATEGORICAL ANALYSIS
    # -----------------------------------------------------

    content.append(
        Paragraph("Categorical Analysis", styles["SectionHeading"])
    )

    categorical_data = [
        ["COLUMN", "UNIQUE VALUES", "MOST FREQUENT VALUE", "FREQUENCY"]
    ]

    for column in categorical_columns:

        series = df[column].dropna()

        if series.empty:
            top_value = "-"
            frequency = 0
        else:
            counts = series.astype(str).value_counts()
            top_value = counts.index[0]
            frequency = int(counts.iloc[0])

        categorical_data.append([

            safe_text(column, 30),

            str(df[column].nunique()),

            safe_text(top_value, 45),

            str(frequency)

        ])

    if len(categorical_data) > 1:

        content.append(
            make_table(
                categorical_data,
                widths=[120, 100, 300, 100]
            )
        )

    else:

        content.append(
            Paragraph(
                "No categorical columns found in this dataset.",
                styles["SmallText"]
            )
        )

    # -----------------------------------------------------
    # DATASET PREVIEW
    # -----------------------------------------------------

    content.append(
        Paragraph("Dataset Preview", styles["SectionHeading"])
    )

    preview = df.head(10).copy()

    # Keep preview readable for wide datasets.
    preview_columns = list(preview.columns[:8])

    preview = preview[preview_columns]

    preview_data = [
        [
            Paragraph(
                safe_text(column, 25),
                styles["SmallText"]
            )
            for column in preview.columns
        ]
    ]

    for _, row in preview.iterrows():

        preview_data.append([

            Paragraph(
                safe_text(value, 35),
                styles["SmallText"]
            )

            for value in row.tolist()

        ])

    if len(preview_data) > 1:

        available_width = page_width - 70

        column_width = available_width / max(
            len(preview_columns), 1
        )

        content.append(
            make_table(
                preview_data,
                widths=[
                    column_width
                ] * len(preview_columns),
                font_size=7
            )
        )

    if total_columns > 8:

        content.append(Spacer(1, 8))

        content.append(
            Paragraph(
                f"Note: Preview displays the first 8 columns "
                f"out of {total_columns} total columns.",
                styles["SmallText"]
            )
        )

    # -----------------------------------------------------
    # FOOTER
    # -----------------------------------------------------

    def add_footer(canvas, doc):

        canvas.saveState()

        canvas.setStrokeColor(BORDER)
        canvas.setLineWidth(0.6)

        canvas.line(
            35,
            30,
            page_width - 35,
            30
        )

        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)

        canvas.drawString(
            35,
            18,
            "DataPulse | Intelligent Data Analytics Platform"
        )

        canvas.drawRightString(
            page_width - 35,
            18,
            f"Page {doc.page}"
        )

        canvas.restoreState()

    # -----------------------------------------------------
    # BUILD PDF
    # -----------------------------------------------------

    document.build(
        content,
        onFirstPage=add_footer,
        onLaterPages=add_footer
    )

    buffer.seek(0)

    return buffer