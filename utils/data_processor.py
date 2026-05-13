# utils/data_processor.py
"""Data processing utilities for CSV/Excel ingestion and cleaning."""
import pandas as pd
import numpy as np
import json
import re
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from backend.core.logger import logger


def load_file(file_path: str) -> pd.DataFrame:
    """Load CSV, Excel, or JSON into DataFrame."""
    path = Path(file_path)
    ext = path.suffix.lower()

    loaders = {
        ".csv": lambda p: pd.read_csv(p, encoding="utf-8-sig", low_memory=False),
        ".xlsx": lambda p: pd.read_excel(p, engine="openpyxl"),
        ".xls": lambda p: pd.read_excel(p, engine="xlrd"),
        ".json": lambda p: pd.read_json(p),
    }

    if ext not in loaders:
        raise ValueError(f"Unsupported file type: {ext}")

    df = loaders[ext](file_path)
    logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns from {path.name}")
    return df


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize a DataFrame."""
    # Normalize column names
    df.columns = [
        re.sub(r"[^a-zA-Z0-9_]", "_", col.strip().lower().replace(" ", "_"))
        for col in df.columns
    ]
    # Remove duplicate columns
    df = df.loc[:, ~df.columns.duplicated()]

    # Drop fully empty rows/columns
    df.dropna(how="all", inplace=True)
    df.dropna(axis=1, how="all", inplace=True)

    # Parse date columns
    for col in df.columns:
        if df[col].dtype == object:
            try:
                parsed = pd.to_datetime(df[col], infer_datetime_format=True, errors="coerce")
                if parsed.notna().sum() > len(df) * 0.7:
                    df[col] = parsed
            except Exception:
                pass

    # Numeric coercion for string columns that look numeric
    for col in df.select_dtypes(include="object").columns:
        cleaned = df[col].str.replace(r"[,$%]", "", regex=True).str.strip()
        try:
            numeric = pd.to_numeric(cleaned, errors="coerce")
            if numeric.notna().sum() > len(df) * 0.8:
                df[col] = numeric
        except Exception:
            pass

    return df


def get_column_metadata(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Extract rich metadata for each column."""
    meta = []
    for col in df.columns:
        series = df[col]
        col_info = {
            "name": col,
            "dtype": str(series.dtype),
            "null_count": int(series.isna().sum()),
            "null_pct": round(series.isna().mean() * 100, 2),
            "unique_count": int(series.nunique()),
            "sample_values": series.dropna().head(5).tolist(),
        }
        if pd.api.types.is_numeric_dtype(series):
            col_info.update({
                "min": float(series.min()) if series.notna().any() else None,
                "max": float(series.max()) if series.notna().any() else None,
                "mean": float(series.mean()) if series.notna().any() else None,
                "std": float(series.std()) if series.notna().any() else None,
            })
        meta.append(col_info)
    return meta


def detect_numeric_columns(df: pd.DataFrame) -> List[str]:
    return df.select_dtypes(include=np.number).columns.tolist()


def detect_date_columns(df: pd.DataFrame) -> List[str]:
    return [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])]


def detect_categorical_columns(df: pd.DataFrame, max_unique: int = 50) -> List[str]:
    return [
        c for c in df.select_dtypes(include="object").columns
        if df[c].nunique() <= max_unique
    ]


def df_to_safe_json(df: pd.DataFrame, max_rows: int = 100) -> List[Dict]:
    """Convert DataFrame to JSON-safe list of dicts."""
    sample = df.head(max_rows).copy()
    for col in sample.select_dtypes(include=["datetime64"]).columns:
        sample[col] = sample[col].astype(str)
    return sample.where(pd.notnull(sample), None).to_dict(orient="records")


def get_dataframe_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """Get a comprehensive summary of the dataframe."""
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "numeric_columns": detect_numeric_columns(df),
        "date_columns": detect_date_columns(df),
        "categorical_columns": detect_categorical_columns(df),
        "total_nulls": int(df.isna().sum().sum()),
        "memory_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2),
        "duplicates": int(df.duplicated().sum()),
    }
