# Industrial Sheet AI

MVP em Python para analisar planilhas industriais e transformar dados operacionais em
KPIs, anomalias e recomendações explicáveis.

## O que já funciona

- Upload de arquivos CSV, XLSX e XLS.
- Detecção automática de separador e suporte a CSV UTF-8/Windows.
- Dados de demonstração para começar sem uma planilha real.
- Detecção de colunas numéricas e datas.
- KPIs de produção, perdas, refugo e paradas quando essas colunas existem.
- Detecção de anomalias com Isolation Forest.
- Gráfico exploratório e tabela de linhas sinalizadas.

## Executar

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Para validar:

```powershell
pytest
```

## Próximos incrementos

1. Padronizar um dicionário de dados industrial (produção, OEE, perdas, paradas e qualidade).
2. Adicionar filtros por linha, turno, produto e período.
3. Conectar um modelo de linguagem por meio de um provedor configurável, sem colocar
   credenciais no código.
4. Evoluir para API FastAPI e persistência de histórico.

## Formato recomendado da planilha

Use uma linha por evento, lote, hora ou turno. Colunas recomendadas:

`data_hora`, `linha`, `produto`, `turno`, `producao_unidades`,
`perdas_unidades`, `parada_minutos` e `temperatura_c`.

Os nomes não precisam ser idênticos: o sistema reconhece palavras-chave como
`produc`, `perda`, `refugo` e `parad` para calcular os totais.
