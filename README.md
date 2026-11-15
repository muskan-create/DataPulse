# DataPulse – Intelligent Data Analytics Platform

DataPulse is a Python-based data analytics platform that helps users upload, clean, analyze, visualize, and understand their datasets through an interactive web interface.

## Features

- **Dataset Upload:** Upload CSV and Excel files.
- **Analytics Dashboard:** View important dataset statistics and key performance indicators.
- **Data Cleaning:** Identify missing values, duplicate records, and improve data quality.
- **Data Visualization:** Generate interactive-style charts including bar, line, pie, histogram, and scatter plots.
- **InsightAI:** Generate data-driven insights and business recommendations.
- **VisualQuery:** Ask questions about datasets using simple English.
- **Dataset Comparison:** Compare two datasets and understand differences.
- **Report Generation:** Export analytical reports in PDF and CSV formats.
- **Dataset History:** View, reload, and delete previously uploaded datasets.

## Technology Stack

**Backend:** Python, Flask  
**Data Analysis:** Pandas, NumPy  
**Visualization:** Matplotlib, Seaborn  
**Frontend:** HTML, CSS, JavaScript  
**Database:** SQLite  
**Testing:** Pytest

## Project Structure

```text
DataPulse/
│
├── analysis/
├── data/
├── reports/
├── static/
│   ├── css/
│   └── js/
├── templates/
├── tests/
├── uploads/
├── visualization/
│
├── app.py
├── config.py
├── database.py
├── utils.py
├── requirements.txt
└── README.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd DataPulse
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Application

```bash
python app.py
```

Open your browser:

```text
http://127.0.0.1:5000/
```

## Run Automated Tests

Run the following command:

```bash
python -m pytest -v
```

Current test status: **9 tests passed.**

## Purpose

The goal of DataPulse is to simplify data analysis by bringing data cleaning, analytics, visualization, and business insights together in one platform.

## Author

Muskan Prajapati  
B.Tech – Computer Science (Data Science)