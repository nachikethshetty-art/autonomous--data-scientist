"""
Data Ingestion & Validation Module
Module 1: Async CSV upload with schema detection and metadata storage
"""

import os
import sqlite3
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
import pandas as pd
import numpy as np
from io import StringIO


def _convert_to_python_types(obj: Any) -> Any:
    """Recursively convert numpy types to native Python types."""
    if isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: _convert_to_python_types(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_convert_to_python_types(item) for item in obj]
    else:
        return obj


class DataValidator:
    """Validates and ingests CSV data with schema detection."""

    # SQLite for job tracking
    DB_PATH = "data/jobs.db"

    def __init__(self):
        """Initialize database if it doesn't exist."""
        Path(self.DB_PATH).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database schema."""
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    upload_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    file_path TEXT NOT NULL,
                    schema TEXT NOT NULL,
                    shape TEXT NOT NULL,
                    rows INTEGER NOT NULL,
                    cols INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    metadata TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS validations (
                    validation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT NOT NULL,
                    check_name TEXT NOT NULL,
                    passed BOOLEAN NOT NULL,
                    message TEXT,
                    FOREIGN KEY (job_id) REFERENCES jobs(job_id)
                )
                """
            )
            conn.commit()

    def upload_csv(self, file_content: str, filename: str) -> Dict[str, Any]:
        """
        Upload and validate CSV file.

        Args:
            file_content: CSV content as string
            filename: Original filename for reference

        Returns:
            Dict with job_id, schema, validation results
        """
        # Parse CSV
        try:
            df = pd.read_csv(StringIO(file_content))
        except Exception as e:
            return {"success": False, "error": f"Failed to parse CSV: {str(e)}"}

        # Generate job ID and store
        job_id = str(uuid.uuid4())[:8]
        file_path = f"data/processed/{job_id}_{filename}"
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        # Save processed file
        df.to_csv(file_path, index=False)

        # Detect schema
        schema = self._detect_schema(df)
        metadata = self._extract_metadata(df, schema)

        # Store in database
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.execute(
                """
                INSERT INTO jobs (job_id, filename, file_path, schema, shape, rows, cols, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    filename,
                    file_path,
                    json.dumps(schema),
                    f"{df.shape[0]}x{df.shape[1]}",
                    df.shape[0],
                    df.shape[1],
                    json.dumps(metadata),
                ),
            )
            conn.commit()

        # Run validation checks
        validation_results = self._validate(job_id, df, schema)

        result = {
            "success": True,
            "job_id": job_id,
            "filename": filename,
            "rows": int(df.shape[0]),
            "cols": int(df.shape[1]),
            "columns": list(df.columns),
            "schema": schema,
            "metadata": metadata,
            "validation_results": validation_results,
        }
        
        # Convert all numpy types to Python-native types
        return _convert_to_python_types(result)

    def _detect_schema(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Detect data types and schema.

        Returns:
            Schema dict with column types and statistics
        """
        schema = {}
        for col in df.columns:
            dtype = str(df[col].dtype)
            null_count = df[col].isnull().sum()
            null_pct = (null_count / len(df)) * 100

            if dtype == "object":
                # Check if it's actually numeric or date
                detected_type = self._infer_column_type(df[col])
            else:
                detected_type = dtype

            schema[col] = {
                "detected_type": detected_type,
                "pandas_dtype": dtype,
                "null_count": int(null_count),
                "null_percentage": round(null_pct, 2),
                "unique_values": int(df[col].nunique()),
                "sample_values": df[col].dropna().head(3).tolist()[:3],  # Limit to 3 samples
            }

        return schema

    def _infer_column_type(self, series: pd.Series) -> str:
        """Infer actual type from object column."""
        try:
            pd.to_numeric(series, errors="raise")
            return "numeric"
        except:
            pass

        try:
            pd.to_datetime(series, errors="raise")
            return "datetime"
        except:
            pass

        return "categorical"

    def _extract_metadata(self, df: pd.DataFrame, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Extract summary statistics."""
        metadata = {
            "total_rows": int(len(df)),
            "total_columns": int(len(df.columns)),
            "memory_usage_mb": float(round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)),
            "duplicate_rows": int(df.duplicated().sum()),
            "numeric_columns": [],
            "categorical_columns": [],
            "datetime_columns": [],
            "sparse_columns": [],  # >50% nulls
        }

        for col, col_schema in schema.items():
            col_type = col_schema["detected_type"]
            null_pct = col_schema["null_percentage"]

            if col_type == "numeric":
                metadata["numeric_columns"].append(col)
            elif col_type == "categorical":
                metadata["categorical_columns"].append(col)
            elif col_type == "datetime":
                metadata["datetime_columns"].append(col)

            if null_pct > 50:
                metadata["sparse_columns"].append((col, float(null_pct)))

        return metadata

    def _validate(self, job_id: str, df: pd.DataFrame, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run validation checks."""
        results = []

        # Check 1: Not empty
        check = {
            "name": "Non-empty dataset",
            "passed": bool(len(df) > 0),
            "message": f"Dataset has {len(df)} rows",
        }
        results.append(check)
        self._store_validation(job_id, check)

        # Check 2: No completely empty columns
        check = {
            "name": "No completely empty columns",
            "passed": bool(not any(df[col].isnull().all() for col in df.columns)),
            "message": f"All {len(df.columns)} columns have at least one value",
        }
        results.append(check)
        self._store_validation(job_id, check)

        # Check 3: Reasonable number of rows/cols
        check = {
            "name": "Reasonable dimensions",
            "passed": bool(10 <= len(df) <= 1000000 and 2 <= len(df.columns) <= 1000),
            "message": f"Shape {len(df)} x {len(df.columns)} is valid",
        }
        results.append(check)
        self._store_validation(job_id, check)

        # Check 4: Check for duplicates
        dup_count = int(df.duplicated().sum())
        check = {
            "name": "Duplicate rows",
            "passed": bool(dup_count / len(df) < 0.5),  # Less than 50% duplicates
            "message": f"{dup_count} duplicate rows ({round(dup_count/len(df)*100, 1)}%)",
        }
        results.append(check)
        self._store_validation(job_id, check)

        # Check 5: Column naming
        has_bad_names = any(col.strip() != col or col == "" for col in df.columns)
        check = {
            "name": "Valid column names",
            "passed": bool(not has_bad_names),
            "message": "All columns have valid names",
        }
        results.append(check)
        self._store_validation(job_id, check)

        # Convert all results to JSON-serializable format
        clean_results = []
        for r in results:
            clean_results.append({
                "name": str(r["name"]),
                "passed": bool(r["passed"]),
                "message": str(r["message"])
            })

        return clean_results

    def _store_validation(self, job_id: str, check: Dict[str, Any]):
        """Store validation result in database."""
        with sqlite3.connect(self.DB_PATH) as conn:
            conn.execute(
                """
                INSERT INTO validations (job_id, check_name, passed, message)
                VALUES (?, ?, ?, ?)
                """,
                (job_id, check["name"], check["passed"], check.get("message", "")),
            )
            conn.commit()

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get job status and metadata."""
        with sqlite3.connect(self.DB_PATH) as conn:
            row = conn.execute(
                "SELECT * FROM jobs WHERE job_id = ?", (job_id,)
            ).fetchone()

            if not row:
                return {"error": "Job not found"}

            job = {
                "job_id": row[0],
                "filename": row[1],
                "timestamp": row[2],
                "file_path": row[3],
                "schema": json.loads(row[4]),
                "shape": row[5],
                "rows": row[6],
                "cols": row[7],
                "status": row[8],
                "metadata": json.loads(row[9]),
            }

            # Get validations
            validations = conn.execute(
                "SELECT check_name, passed, message FROM validations WHERE job_id = ?",
                (job_id,),
            ).fetchall()
            job["validations"] = [
                {"name": v[0], "passed": v[1], "message": v[2]} for v in validations
            ]

            return job

    def list_jobs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent jobs."""
        with sqlite3.connect(self.DB_PATH) as conn:
            rows = conn.execute(
                """
                SELECT job_id, filename, upload_timestamp, rows, cols, status
                FROM jobs
                ORDER BY upload_timestamp DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

            return [
                {
                    "job_id": row[0],
                    "filename": row[1],
                    "timestamp": row[2],
                    "rows": row[3],
                    "cols": row[4],
                    "status": row[5],
                }
                for row in rows
            ]

    def load_dataframe(self, job_id: str) -> Optional[pd.DataFrame]:
        """Load processed dataframe for a job."""
        with sqlite3.connect(self.DB_PATH) as conn:
            row = conn.execute(
                "SELECT file_path FROM jobs WHERE job_id = ?", (job_id,)
            ).fetchone()

            if not row:
                return None

            return pd.read_csv(row[0])


# Module exports
__all__ = ["DataValidator"]
