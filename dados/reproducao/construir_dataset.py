"""Recria os CSV a partir das fontes guardadas. Requer Python, pandas e numpy."""
from pathlib import Path
import json
import platform
import re
import zipfile

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
RAW = ROOT / 'fontes_originais'
COUNTRIES = {
    'PRT': ('Portugal', 'Portugal', 'Elevado'),
    'ESP': ('Espanha', 'Spain', 'Elevado'),
    'JPN': ('Japão', 'Japan', 'Elevado'),
    'BRA': ('Brasil', 'Brazil', 'Médio-alto'),
    'MEX': ('México', 'Mexico', 'Médio-alto'),
    'ZAF': ('África do Sul', 'South Africa', 'Médio-alto'),
    'THA': ('Tailândia', 'Thailand', 'Médio-alto'),
    'BEN': ('Benim', 'Benin', 'Médio-baixo'),
    'HND': ('Honduras', 'Honduras', 'Médio-baixo'),
    'NGA': ('Nigéria', 'Nigeria', 'Médio-baixo'),
    'SEN': ('Senegal', 'Senegal', 'Médio-baixo'),
    'BDI': ('Burundi', 'Burundi', 'Baixo'),
    'BFA': ('Burkina Faso', 'Burkina Faso', 'Baixo'),
    'MLI': ('Mali', 'Mali', 'Baixo'),
    'NER': ('Níger', 'Niger', 'Baixo'),
}


def save_csv(frame, name):
    frame.to_csv(ROOT / name, index=False, encoding='utf-8-sig', date_format='%Y-%m-%d')


def read_climate():
    rows = []
    for country in COUNTRIES:
        for var in ['tmp', 'pre', 'pet']:
            path = RAW / 'CRU' / f'{country}_{var}.per'
            for line in path.read_text().splitlines():
                fields = line.split()
                if len(fields) >= 13 and re.fullmatch(r'\d{4}', fields[0]):
                    for month, value in enumerate(fields[1:13], 1):
                        rows.append((country, pd.Timestamp(int(fields[0]), month, 1), var, float(value)))
    data = pd.DataFrame(rows, columns=['pais_iso3', 'data', 'variavel', 'valor'])
    assert data.valor.gt(-999).all(), 'Código de valor omisso no clima'
    assert not data.duplicated(['pais_iso3', 'data', 'variavel']).any()
    data = data.pivot(index=['pais_iso3', 'data'], columns='variavel', values='valor').reset_index()
    data.columns.name = None
    data = data.rename(columns={'tmp': 'temperatura_media_c', 'pre': 'precipitacao_mm', 'pet': 'pet_mm_dia'})
    data = data.sort_values(['pais_iso3', 'data']).reset_index(drop=True)
    assert len(data) == 15 * 125 * 12
    assert data.notna().all().all()
    data['pais'] = data.pais_iso3.map(lambda c: COUNTRIES[c][0])
    return data


def read_food():
    with zipfile.ZipFile(RAW / 'FAOSTAT_CP.zip') as z:
        path = next(n for n in z.namelist() if n.endswith('(Normalized).csv'))
        food = pd.read_csv(z.open(path), encoding='utf-8-sig', low_memory=False)
    mapping = {v[1]: k for k, v in COUNTRIES.items()}
    food = food[food['Item Code'].eq(23013) & food.Area.isin(mapping) & food.Year.between(2000, 2025)].copy()
    food['pais_iso3'] = food.Area.map(mapping)
    food['data'] = pd.to_datetime(dict(year=food.Year, month=food['Months Code'] - 7000, day=1))
    food = food.rename(columns={'Value': 'ipc_alimentar_2015_100', 'Flag': 'flag_ipc_faostat'})
    food = food[['pais_iso3', 'data', 'ipc_alimentar_2015_100', 'flag_ipc_faostat']]
    assert not food.duplicated(['pais_iso3', 'data']).any()
    assert len(food) == 4680
    assert food.ipc_alimentar_2015_100.gt(0).all()
    assert food.flag_ipc_faostat.isin(['A', 'X']).all()
    return food


def read_wdi():
    rows = []
    paths = ['gdp_ppp.json', 'agricultura_inicial.json', 'agricultura_alternativos.json']
    for name in paths:
        metadata, records = json.loads((RAW / 'WDI' / name).read_bytes())
        assert metadata['pages'] == 1
        for r in records:
            country, year = r['countryiso3code'], int(r['date'])
            if country in COUNTRIES and 1999 <= year <= 2024:
                rows.append((country, year, r['indicator']['id'], r['value']))
    data = pd.DataFrame(rows, columns=['pais_iso3', 'ano', 'variavel', 'valor'])
    assert not data.duplicated(['pais_iso3', 'ano', 'variavel']).any()
    data = data.pivot(index=['pais_iso3', 'ano'], columns='variavel', values='valor').reset_index()
    data.columns.name = None
    data = data.rename(columns={'NY.GDP.PCAP.PP.KD': 'pib_pc_ppc_2021', 'NV.AGR.TOTL.ZS': 'peso_agricola_pct_pib'})
    assert len(data) == 390 and data.notna().all().all()
    assert data.pib_pc_ppc_2021.gt(0).all()
    data['pais'] = data.pais_iso3.map(lambda c: COUNTRIES[c][0])
    return data.sort_values(['pais_iso3', 'ano']).reset_index(drop=True)


def build():
    climate = read_climate()
    food = read_food()
    annual = read_wdi()
    climate['mes'] = climate.data.dt.month
    climate['pet_mm_mes'] = climate.pet_mm_dia * climate.data.dt.days_in_month
    climate['balanco_hidrico_mm'] = climate.precipitacao_mm - climate.pet_mm_mes
    climate['balanco_hidrico_3m_mm'] = climate.groupby('pais_iso3').balanco_hidrico_mm.transform(lambda x: x.rolling(3, min_periods=3).sum())
    baseline = climate[climate.data.dt.year.between(1991, 2020)]
    normals = baseline.groupby(['pais_iso3', 'mes']).agg(
        temperatura_normal_c=('temperatura_media_c', 'mean'),
        balanco_3m_normal_mm=('balanco_hidrico_3m_mm', 'mean'),
        balanco_3m_desvio_padrao_mm=('balanco_hidrico_3m_mm', lambda x: x.std(ddof=1)),
        n_anos_temperatura=('temperatura_media_c', 'count'),
        n_anos_balanco=('balanco_hidrico_3m_mm', 'count'),
    ).reset_index()
    assert len(normals) == 180
    assert normals.n_anos_temperatura.eq(30).all() and normals.n_anos_balanco.eq(30).all()
    assert normals.balanco_3m_desvio_padrao_mm.gt(0).all()
    climate = climate.merge(normals, on=['pais_iso3', 'mes'], validate='many_to_one')
    climate['anomalia_temperatura_c'] = climate.temperatura_media_c - climate.temperatura_normal_c
    climate['defice_hidrico_3m_z'] = (climate.balanco_3m_normal_mm - climate.balanco_hidrico_3m_mm) / climate.balanco_3m_desvio_padrao_mm

    current = climate[climate.data.between('2000-01-01', '2025-12-01')].copy()
    joined = current.merge(food, on=['pais_iso3', 'data'], how='left', validate='one_to_one')
    joined = joined.sort_values(['pais_iso3', 'data']).reset_index(drop=True)
    monthly_raw = joined[['pais_iso3', 'pais', 'data', 'ipc_alimentar_2015_100', 'flag_ipc_faostat', 'temperatura_media_c', 'precipitacao_mm', 'pet_mm_dia']].copy()
    joined['ano_dados_economicos'] = joined.data.dt.year - 1
    joined = joined.merge(annual.drop(columns='pais').rename(columns={'ano': 'ano_dados_economicos'}), on=['pais_iso3', 'ano_dados_economicos'], how='left', validate='many_to_one')
    joined['inflacao_alimentar_log_pct'] = joined.groupby('pais_iso3').ipc_alimentar_2015_100.transform(lambda x: 100 * np.log(x).diff())
    joined['ln_pib_pc_ppc_ano_anterior'] = np.log(joined.pib_pc_ppc_2021)
    joined['peso_agricola_pct_ano_anterior'] = joined.peso_agricola_pct_pib
    joined['calor_x_ln_pib'] = joined.anomalia_temperatura_c * joined.ln_pib_pc_ppc_ano_anterior
    joined['calor_x_peso_agricola'] = joined.anomalia_temperatura_c * joined.peso_agricola_pct_ano_anterior
    joined['grupo_rendimento_2027'] = joined.pais_iso3.map(lambda c: COUNTRIES[c][2])
    joined['ano'] = joined.data.dt.year
    joined['amostra_temporal'] = np.where(joined.ano.eq(2025), 'teste_2025', 'treino_ate_2024')
    columns = ['pais_iso3', 'pais', 'data', 'ano', 'mes', 'inflacao_alimentar_log_pct', 'anomalia_temperatura_c', 'defice_hidrico_3m_z', 'ln_pib_pc_ppc_ano_anterior', 'peso_agricola_pct_ano_anterior', 'calor_x_ln_pib', 'calor_x_peso_agricola', 'ano_dados_economicos', 'grupo_rendimento_2027', 'flag_ipc_faostat', 'amostra_temporal']
    panel = joined.loc[joined.data.ge('2000-02-01'), columns].sort_values(['pais_iso3', 'data']).reset_index(drop=True)
    assert len(panel) == 4665 and panel.notna().all().all()
    assert not panel.duplicated(['pais_iso3', 'data']).any()
    assert panel.groupby('pais_iso3').size().eq(311).all()
    expected = pd.date_range('2000-02-01', '2025-12-01', freq='MS')
    for country, sample in panel.groupby('pais_iso3'):
        assert sample.data.tolist() == expected.tolist(), country
    numeric = panel.select_dtypes('number')
    assert np.isfinite(numeric).all().all()
    assert panel.ano_dados_economicos.eq(panel.ano - 1).all()

    # Conferências independentes em países, anos bissextos e limites da amostra.
    spot_checks = []
    for country, stamp in [('PRT', '2000-02-01'), ('THA', '2020-02-01'), ('NER', '2024-02-01'), ('BRA', '2025-12-01')]:
        date = pd.Timestamp(stamp)
        obs = panel[(panel.pais_iso3 == country) & (panel.data == date)].iloc[0]
        source = monthly_raw[monthly_raw.pais_iso3.eq(country)].set_index('data')
        independent_rate = 100 * np.log(source.at[date, 'ipc_alimentar_2015_100'] / source.at[date - pd.DateOffset(months=1), 'ipc_alimentar_2015_100'])
        assert abs(obs.inflacao_alimentar_log_pct - independent_rate) < 1e-10
        hist = climate[climate.pais_iso3.eq(country)].set_index('data')
        monthly_balance = lambda dt: hist.at[dt, 'precipitacao_mm'] - hist.at[dt, 'pet_mm_dia'] * dt.days_in_month
        water = sum(monthly_balance(date - pd.DateOffset(months=k)) for k in range(3))
        historical_water = np.array([sum(monthly_balance(pd.Timestamp(y, date.month, 1) - pd.DateOffset(months=k)) for k in range(3)) for y in range(1991, 2021)])
        independent_deficit = (historical_water.mean() - water) / historical_water.std(ddof=1)
        assert abs(obs.defice_hidrico_3m_z - independent_deficit) < 1e-10
        independent_temp = hist.at[date, 'temperatura_media_c'] - np.mean([hist.at[pd.Timestamp(y, date.month, 1), 'temperatura_media_c'] for y in range(1991, 2021)])
        assert abs(obs.anomalia_temperatura_c - independent_temp) < 1e-10
        spot_checks.append({'pais_iso3': country, 'data': stamp, 'inflacao_log_pct': independent_rate, 'defice_hidrico_3m_z': independent_deficit})

    save_csv(panel, 'painel_indicadores.csv')
    save_csv(monthly_raw, 'dados_brutos_mensais.csv')
    save_csv(annual[['pais_iso3', 'pais', 'ano', 'pib_pc_ppc_2021', 'peso_agricola_pct_pib']], 'dados_brutos_anuais.csv')
    save_csv(climate[['pais_iso3', 'pais', 'data', 'temperatura_media_c', 'precipitacao_mm', 'pet_mm_dia']].sort_values(['pais_iso3', 'data']), 'clima_historico_mensal.csv')
    save_csv(normals.sort_values(['pais_iso3', 'mes']), 'normais_climaticas_1991_2020.csv')
    save_csv(pd.DataFrame([{'pais_iso3': c, 'pais': v[0], 'nome_fao': v[1], 'grupo_rendimento_2027': v[2]} for c, v in COUNTRIES.items()]), 'paises.csv')
    pt = panel[panel.pais_iso3.eq('PRT')][['data', 'inflacao_alimentar_log_pct', 'amostra_temporal']]
    save_csv(pt, 'portugal_sarima.csv')
    report = {
        'periodo_dados_brutos': ['2000-01', '2025-12'],
        'periodo_painel': ['2000-02', '2025-12'],
        'n_paises': 15, 'n_meses_por_pais': 311, 'n_linhas_painel': len(panel),
        'n_linhas_dados_brutos_mensais': len(monthly_raw), 'n_linhas_anuais': len(annual),
        'n_linhas_clima_historico': len(climate), 'n_normais': len(normals),
        'pares_duplicados_painel': int(panel.duplicated(['pais_iso3', 'data']).sum()),
        'omissos_painel': panel.isna().sum().to_dict(),
        'flags_faostat_mensais': monthly_raw.flag_ipc_faostat.value_counts().to_dict(),
        'portugal_treino': int(pt.amostra_temporal.eq('treino_ate_2024').sum()),
        'portugal_teste': int(pt.amostra_temporal.eq('teste_2025').sum()),
        'conferencias_independentes': spot_checks,
        'ambiente': {'python': platform.python_version(), 'pandas': pd.__version__, 'numpy': np.__version__},
    }
    (ROOT / 'verificacao_dataset.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'painel': len(panel), 'paises': 15, 'meses': 311, 'omissos': int(panel.isna().sum().sum()), 'portugal_treino': report['portugal_treino'], 'portugal_teste': report['portugal_teste']}, ensure_ascii=False))


if __name__ == '__main__':
    build()
