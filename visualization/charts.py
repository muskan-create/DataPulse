import os
import uuid

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def generate_chart(dataset, chart_type, x_column, y_column=None):

    if dataset is None or dataset.empty:
        raise ValueError("Dataset is empty.")

    if x_column not in dataset.columns:
        raise ValueError("Invalid X-axis column.")

    chart_type = chart_type.lower()

    supported_types = ["bar", "line", "scatter", "histogram"]

    if chart_type not in supported_types:
        raise ValueError("Unsupported chart type.")

    # Output folder
    base_dir = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )

    chart_dir = os.path.join(
        base_dir,
        "static",
        "charts"
    )

    os.makedirs(chart_dir, exist_ok=True)

    # Dashboard theme
    plt.rcParams.update({
        "figure.facecolor": "#1B2940",
        "axes.facecolor": "#1B2940",
        "axes.edgecolor": "#2B3A50",
        "axes.labelcolor": "#F1F5F9",
        "text.color": "#F1F5F9",
        "xtick.color": "#CBD5E1",
        "ytick.color": "#CBD5E1",
        "grid.color": "#34445B",
        "font.family": "DejaVu Sans"
    })

    fig, ax = plt.subplots(figsize=(11, 6))

    try:

        if chart_type == "bar":

            if y_column not in dataset.columns:
                raise ValueError("Select a valid Y-axis column.")

            if not pd.api.types.is_numeric_dtype(dataset[y_column]):
                raise ValueError("Y-axis must be numerical.")

            data = dataset[[x_column, y_column]].copy()
            data[y_column] = pd.to_numeric(
                data[y_column], errors="coerce"
            )
            data = data.dropna()

            if data.empty:
                raise ValueError("No valid data available.")

            grouped = data.groupby(
                x_column,
                observed=False
            )[y_column].sum().sort_values(ascending=False)

            grouped = grouped.head(20)

            ax.bar(
                grouped.index.astype(str),
                grouped.values,
                color="#3B82F6",
                edgecolor="#60A5FA",
                linewidth=0.8
            )

            ax.set_title(
                f"{y_column} by {x_column}",
                fontsize=17,
                fontweight="bold",
                pad=20
            )

            ax.set_xlabel(x_column)
            ax.set_ylabel(y_column)
            plt.xticks(rotation=35, ha="right")

        elif chart_type == "line":

            if y_column not in dataset.columns:
                raise ValueError("Select a valid Y-axis column.")

            if not pd.api.types.is_numeric_dtype(dataset[y_column]):
                raise ValueError("Y-axis must be numerical.")

            data = dataset[[x_column, y_column]].copy()
            data[y_column] = pd.to_numeric(
                data[y_column], errors="coerce"
            )
            data = data.dropna()

            if data.empty:
                raise ValueError("No valid data available.")

            # Aggregate repeated X-axis values
            grouped = data.groupby(
                x_column,
                observed=False
            )[y_column].mean()

            try:
                grouped = grouped.sort_index()
            except TypeError:
                pass

            grouped = grouped.head(100)

            ax.plot(
                grouped.index.astype(str),
                grouped.values,
                color="#60A5FA",
                linewidth=2.8,
                marker="o",
                markersize=6,
                markerfacecolor="#34D399"
            )

            ax.set_title(
                f"{y_column} Trend by {x_column}",
                fontsize=17,
                fontweight="bold",
                pad=20
            )

            ax.set_xlabel(x_column)
            ax.set_ylabel(y_column)
            plt.xticks(rotation=35, ha="right")

        elif chart_type == "scatter":

            if y_column not in dataset.columns:
                raise ValueError("Select a valid Y-axis column.")

            if not pd.api.types.is_numeric_dtype(dataset[x_column]):
                raise ValueError("Scatter plot requires a numerical X-axis.")

            if not pd.api.types.is_numeric_dtype(dataset[y_column]):
                raise ValueError("Y-axis must be numerical.")

            data = dataset[[x_column, y_column]].copy()

            data[x_column] = pd.to_numeric(
                data[x_column], errors="coerce"
            )

            data[y_column] = pd.to_numeric(
                data[y_column], errors="coerce"
            )

            data = data.replace(
                [np.inf, -np.inf], np.nan
            ).dropna()

            if data.empty:
                raise ValueError("No valid numerical data available.")

            ax.scatter(
                data[x_column],
                data[y_column],
                color="#60A5FA",
                edgecolors="#A78BFA",
                alpha=0.8,
                s=65
            )

            ax.set_title(
                f"{y_column} vs {x_column}",
                fontsize=17,
                fontweight="bold",
                pad=20
            )

            ax.set_xlabel(x_column)
            ax.set_ylabel(y_column)

        elif chart_type == "histogram":

            if not pd.api.types.is_numeric_dtype(dataset[x_column]):
                raise ValueError("Histogram requires a numerical column.")

            values = pd.to_numeric(
                dataset[x_column], errors="coerce"
            ).replace([np.inf, -np.inf], np.nan).dropna()

            if values.empty:
                raise ValueError("No valid numerical values available.")

            ax.hist(
                values,
                bins="auto",
                color="#3B82F6",
                edgecolor="#A78BFA",
                alpha=0.9
            )

            ax.set_title(
                f"Distribution of {x_column}",
                fontsize=17,
                fontweight="bold",
                pad=20
            )

            ax.set_xlabel(x_column)
            ax.set_ylabel("Frequency")

        # Common styling
        ax.grid(
            True,
            linestyle="--",
            alpha=0.25
        )

        ax.set_axisbelow(True)

        for spine in ax.spines.values():
            spine.set_color("#34445B")

        fig.tight_layout()

        filename = f"chart_{uuid.uuid4().hex}.png"

        file_path = os.path.join(
            chart_dir,
            filename
        )

        fig.savefig(
            file_path,
            dpi=160,
            bbox_inches="tight",
            facecolor=fig.get_facecolor()
        )

        return f"charts/{filename}"

    finally:
        plt.close(fig)