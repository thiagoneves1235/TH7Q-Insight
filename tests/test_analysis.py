from io import StringIO

import pandas as pd

from industrial_ai.analysis import analyze_dataframe, load_spreadsheet
from industrial_ai.sample_data import create_sample_data


class NamedStringIO(StringIO):
    pass


def test_sample_data_has_expected_industrial_columns():
    result = analyze_dataframe(create_sample_data())

    assert len(result.data) == 120
    assert "producao_unidades" in result.numeric_columns
    assert result.kpis["Producao total"] > 0
    assert result.insights


def test_analysis_reports_missing_values():
    frame = pd.DataFrame({"producao": [10, None, 12], "linha": ["A", "A", "B"]})

    result = analyze_dataframe(frame)

    assert result.kpis["Valores ausentes"] == 1
    assert any("ausentes" in insight for insight in result.insights)


def test_load_spreadsheet_rejects_unknown_extension():
    try:
        load_spreadsheet("dados.json")
    except ValueError as error:
        assert "nao suportado" in str(error)
    else:
        raise AssertionError("Esperava ValueError para extensao desconhecida")


def test_load_csv_detects_semicolon_and_windows_encoding():
    file = NamedStringIO("linha;producao\nA;10\nB;12\n")
    file.name = "dados.csv"

    result = load_spreadsheet(file)

    assert result["producao"].tolist() == [10, 12]


def test_load_spreadsheet_rejects_duplicate_columns():
    file = NamedStringIO("linha,linha\nA,B\n")
    file.name = "dados.csv"

    try:
        load_spreadsheet(file)
    except ValueError as error:
        assert "duplicados" in str(error)
    else:
        raise AssertionError("Esperava ValueError para colunas duplicadas")
