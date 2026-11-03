from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


@dataclass(frozen=True)
class AnalysisResult:
    data: pd.DataFrame
    numeric_columns: list[str]
    datetime_columns: list[str]
    kpis: dict[str, float]
    anomalies: pd.DataFrame
    insights: list[str]


def load_spreadsheet(file: Any) -> pd.DataFrame:
    """Load CSV or Excel input and reject empty or unsupported files."""
    name = str(getattr(file, "name", "")).lower()
    if name.endswith(".csv"):
        try:
            frame = pd.read_csv(file, sep=None, engine="python", encoding="utf-8-sig")
        except UnicodeDecodeError:
            file.seek(0)
            frame = pd.read_csv(file, sep=None, engine="python", encoding="cp1252")
    elif name.endswith(".xlsx"):
        frame = pd.read_excel(file, engine="openpyxl")
    elif name.endswith(".xls"):
        frame = pd.read_excel(file, engine="xlrd")
    else:
        raise ValueError("Formato nao suportado. Envie um arquivo CSV, XLSX ou XLS.")

    if frame.empty:
        raise ValueError("A planilha nao possui linhas.")
    frame.columns = [str(column).strip() for column in frame.columns]
    if any(not column for column in frame.columns):
        raise ValueError("A planilha possui uma coluna sem nome.")
    if frame.columns.duplicated().any():
        raise ValueError("A planilha possui nomes de colunas duplicados.")
    return frame


def _detect_datetime_columns(frame: pd.DataFrame) -> list[str]:
    result: list[str] = []
    for column in frame.columns:
        if pd.api.types.is_datetime64_any_dtype(frame[column]):
            result.append(column)
            continue
        if frame[column].dtype == "object":
            parsed = pd.to_datetime(frame[column], errors="coerce")
            if parsed.notna().mean() >= 0.8:
                result.append(column)
    return result


def _calculate_kpis(frame: pd.DataFrame, numeric_columns: list[str]) -> dict[str, float]:
    kpis: dict[str, float] = {
        "Linhas analisadas": float(len(frame)),
        "Colunas numericas": float(len(numeric_columns)),
        "Valores ausentes": float(frame.isna().sum().sum()),
    }
    normalized = {column.lower(): column for column in numeric_columns}
    for keyword, label in (
        ("produc", "Producao total"),
        ("quant", "Quantidade total"),
        ("perda", "Perdas totais"),
        ("refugo", "Refugo total"),
        ("parad", "Paradas totais"),
    ):
        matches = [column for name, column in normalized.items() if keyword in name]
        if matches:
            kpis[label] = float(frame[matches[0]].sum(skipna=True))
    return kpis


def _find_anomalies(frame: pd.DataFrame, numeric_columns: list[str]) -> pd.DataFrame:
    if len(numeric_columns) == 0 or len(frame) < 10:
        return frame.iloc[0:0].copy()

    values = frame[numeric_columns].apply(pd.to_numeric, errors="coerce")
    values = values.replace([np.inf, -np.inf], np.nan).fillna(values.median())
    if values.isna().all().all():
        return frame.iloc[0:0].copy()

    detector = IsolationForest(
        contamination="auto",
        random_state=42,
        n_estimators=100,
    )
    labels = detector.fit_predict(values)
    anomalies = frame.loc[labels == -1].copy()
    anomalies.insert(0, "indice_original", anomalies.index)
    return anomalies


def _build_insights(
    frame: pd.DataFrame,
    numeric_columns: list[str],
    anomalies: pd.DataFrame,
    kpis: dict[str, float],
) -> list[str]:
    insights: list[str] = []
    missing = int(frame.isna().sum().sum())
    if missing:
        insights.append(f"Existem {missing} valores ausentes; valide a origem antes de comparar periodos.")
    if len(anomalies):
        ratio = len(anomalies) / len(frame) * 100
        insights.append(f"{len(anomalies)} linhas ({ratio:.1f}%) foram sinalizadas como possiveis anomalias.")
    else:
        insights.append("Nenhuma anomalia estatistica foi identificada com os dados disponiveis.")

    loss_columns = [
        column for column in numeric_columns
        if any(word in column.lower() for word in ("perda", "refugo", "rejeit"))
    ]
    production = kpis.get("Producao total") or kpis.get("Quantidade total")
    if loss_columns and production and production > 0:
        loss = float(frame[loss_columns[0]].sum(skipna=True))
        insights.append(f"A taxa estimada de perdas e {loss / production * 100:.2f}% sobre a producao.")
    if not numeric_columns:
        insights.append("Nao foram encontradas colunas numericas; revise os tipos da planilha.")
    return insights


def analyze_dataframe(frame: pd.DataFrame) -> AnalysisResult:
    """Analyze a normalized industrial dataframe with explainable methods."""
    data = frame.copy()
    numeric_columns = data.select_dtypes(include="number").columns.tolist()
    datetime_columns = _detect_datetime_columns(data)
    kpis = _calculate_kpis(data, numeric_columns)
    anomalies = _find_anomalies(data, numeric_columns)
    insights = _build_insights(data, numeric_columns, anomalies, kpis)
    return AnalysisResult(data, numeric_columns, datetime_columns, kpis, anomalies, insights)
