"""
dashboard/db_queries.py

SQLAlchemy helper functions that query the AutoClaw SQLite database
for the Streamlit dashboard.
"""

import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text

# Locate the database relative to this file's location
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(BASE_DIR, 'autoclaw.sqlite3')
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=False)


def get_all_jobs() -> pd.DataFrame:
    """Returns all rows from discovered_jobs as a DataFrame."""
    query = """
        SELECT
            id,
            company_name    AS "Company",
            job_title       AS "Title",
            status          AS "Status",
            created_at      AS "Discovered At"
        FROM discovered_jobs
        ORDER BY created_at DESC
    """
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn)


def get_applied_jobs() -> pd.DataFrame:
    """Returns jobs that have application log entries (applied jobs)."""
    query = """
        SELECT
            dj.company_name     AS "Company",
            dj.job_title        AS "Title",
            al.application_date AS "Applied At",
            al.success          AS "Success",
            al.notes            AS "Notes / LLM Score"
        FROM application_logs al
        JOIN discovered_jobs dj ON al.job_id = dj.id
        ORDER BY al.application_date DESC
    """
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn)


def get_stats() -> dict:
    """Returns summary stats for the sidebar."""
    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM discovered_jobs")).scalar()
        applied = conn.execute(
            text("SELECT COUNT(*) FROM discovered_jobs WHERE status='applied'")
        ).scalar()
        skipped = conn.execute(
            text("SELECT COUNT(*) FROM discovered_jobs WHERE status='skipped'")
        ).scalar()

    return {
        "total": total or 0,
        "applied": applied or 0,
        "skipped": skipped or 0,
        "pending": (total or 0) - (applied or 0) - (skipped or 0),
    }
