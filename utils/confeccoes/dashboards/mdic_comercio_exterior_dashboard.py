import json
import unidecode
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import pydeck as pdk
from utils.ui.display import titulos_pagina
from utils.confeccoes.formatar import formatar_valor_usd
from src.google_drive_utils import read_parquet_file_from_drive
from utils.confeccoes.dashboards.mdic_bandeiras import get_flag_mapping as _get_flag_mapping


def azul_gradient(valor):
    limites = [
        (0, [230, 244, 255, 180]),
        (100_000, [220, 240, 255, 185]),
        (250_000, [210, 235, 255, 190]),
        (500_000, [200, 230, 255, 195]),
        (1_000_000, [190, 225, 255, 200]),
        (2_000_000, [170, 215, 255, 210]),
        (5_000_000, [150, 205, 255, 220]),
        (10_000_000, [120, 180, 255, 230]),
        (20_000_000, [90, 150, 240, 235]),
        (30_000_000, [60, 120, 220, 240]),
        (50_000_000, [30, 100, 200, 245]),
        (75_000_000, [15, 90, 180, 250]),
        (100_000_000, [0, 80, 170, 255]),
        (200_000_000, [0, 60, 140, 255]),
        (300_000_000, [0, 40, 110, 255]),
    ]
    for lim, cor in limites:
        if valor < lim:
            return cor
    return [0, 20, 80, 255]

def get_flag_mapping():
    
    return _get_flag_mapping()

def add_flag_column(df, pais_col):
    flag_map = get_flag_mapping()
    df = df.copy()
    df['Bandeira'] = df[pais_col].map(flag_map).fillna('')
    return df

def get_municipios_filtrados(df, anos):
    if not anos:
        return []
    df_filtrado = df[df['DATA'].dt.year.isin(anos)]
    municipios = sorted(df_filtrado['NO_MUN'].unique())
    return ["Alagoas"] + municipios

def get_anos_filtrados(df, mun):
    if mun == "Alagoas":
        anos = sorted(df['DATA'].dt.year.unique(), reverse=True)
    else:
        anos = sorted(df[df['NO_MUN'] == mun]['DATA'].dt.year.unique(), reverse=True)
    return anos

def render_mdic_comercio_exterior_dashboard():

    @st.cache_data
    def load_geojson():
        from src.google_drive_utils import read_geojson_file_from_drive
        geojson_path = read_geojson_file_from_drive('mapa_alagoas.geojson')
        with open(geojson_path) as f:
            geojson = json.load(f)
        for feature in geojson['features']:
            nome = unidecode.unidecode(feature['properties']['NM_MUN']).upper()
            feature['properties']['NM_MUN'] = nome
        return geojson

    @st.cache_data
    def load_data():
        
        df = read_parquet_file_from_drive('mdic_comercio_exterior.parquet')
        return df

    # --- CARREGAMENTO DE DADOS ---
    geojson = load_geojson()
    df = load_data()
    df['NO_MUN'] = df['NO_MUN'].apply(lambda x: unidecode.unidecode(x).upper())
    df['DATA'] = pd.to_datetime(df['DATA'])

    # --- FILTROS ---
    ano_atual = pd.Timestamp.now().year
    anos_disponiveis = sorted(df['DATA'].dt.year.unique(), reverse=True)

    if 'anos_selecionados' not in st.session_state:
        st.session_state['anos_selecionados'] = [ano_atual, ano_atual - 1] if (ano_atual - 1) in anos_disponiveis else [ano_atual]
    if 'mun_selecionado' not in st.session_state:
        st.session_state['mun_selecionado'] = "Alagoas"

    col_filtro_ano, col_filtro_mun = st.columns([1, 2])

    with col_filtro_ano:
        anos_filtrados = get_anos_filtrados(df, st.session_state['mun_selecionado'])
        anos_selecionados = st.multiselect(
            "Ano(s)", anos_filtrados,
            default=st.session_state['anos_selecionados'],
            key="anos_selecionados"
        )

    with col_filtro_mun:
        municipios_filtrados = get_municipios_filtrados(df, st.session_state['anos_selecionados'])
        mun_selecionado = st.selectbox(
            "Selecione um município para ver detalhes:",
            options=municipios_filtrados,
            index=municipios_filtrados.index(st.session_state['mun_selecionado']) if st.session_state['mun_selecionado'] in municipios_filtrados else 0,
            key="mun_selecionado"
        )

    df_ano = df[df['DATA'].dt.year.isin(st.session_state['anos_selecionados'])]

    # --- AGREGAÇÃO PARA MAPA ---
    df_periodo = df[df['DATA'].dt.year.isin(st.session_state['anos_selecionados'])]

    df_exp = df_periodo[df_periodo['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum()
    df_imp = df_periodo[df_periodo['CATEGORIA'] == 'IMPORTACAO'].groupby('NO_MUN')['VL_FOB'].sum()

    df_mapa = pd.DataFrame({'VL_EXP': df_exp, 'VL_IMP': df_imp}).fillna(0)
    df_mapa['VL_SALDO'] = df_mapa['VL_EXP'] - df_mapa['VL_IMP']
    df_mapa = df_mapa.reset_index()

    # --- ATUALIZA GEOJSON ---
    mun_to_exp = dict(zip(df_mapa['NO_MUN'], df_mapa['VL_EXP']))
    mun_to_imp = dict(zip(df_mapa['NO_MUN'], df_mapa['VL_IMP']))
    mun_to_saldo = dict(zip(df_mapa['NO_MUN'], df_mapa['VL_SALDO']))
    for feature in geojson['features']:
        mun = feature['properties']['NM_MUN']
        exp = float(mun_to_exp.get(mun, 0))
        imp = float(mun_to_imp.get(mun, 0))
        saldo = float(mun_to_saldo.get(mun, 0))
        feature['properties']['VL_EXP'] = exp
        feature['properties']['VL_IMP'] = imp
        feature['properties']['VL_SALDO'] = saldo
        feature['properties']['VL_EXP_FORMATADO'] = f"{exp:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        feature['properties']['VL_IMP_FORMATADO'] = f"{imp:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        feature['properties']['VL_SALDO_FORMATADO'] = f"{saldo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        feature['properties']['VL_FOB'] = exp + imp
        feature['properties']['VL_FOB_FORMATADO'] = f"{(exp + imp):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        feature['properties']['fill_color'] = azul_gradient(exp + imp)

    estados_geojson = geojson

    geojson_layer = pdk.Layer(
        "GeoJsonLayer",
        geojson,
        pickable=True,
        stroked=True,
        filled=True,
        extruded=False,
        wireframe=True,
        get_fill_color="properties.fill_color",
        get_line_color=[80, 80, 80, 180],
        auto_highlight=True,
    )
    estados_layer = None
    if estados_geojson is not None:
        estados_layer = pdk.Layer(
            "GeoJsonLayer",
            estados_geojson,
            pickable=False,
            stroked=True,
            filled=False,
            get_line_color=[0, 0, 0, 200],
            line_width_min_pixels=1,
        )

    view_state = pdk.ViewState(
        latitude=-9.5713,
        longitude=-36.7820,
        zoom=7,
        pitch=0,
        bearing=0
    )

    tooltip = {
        "html": (
            "<b>{NM_MUN}</b><br/>"
            "Exportação: <b>US$ {VL_EXP_FORMATADO}</b><br/>"
            "Importação: <b>US$ {VL_IMP_FORMATADO}</b><br/>"
            "Saldo: <b>US$ {VL_SALDO_FORMATADO}</b>"
        ),
        "style": {
            "backgroundColor": "rgba(30, 30, 30, 0.9)",
            "color": "white",
            "fontSize": "16px"
        }
    }

    col1, col2 = st.columns([2, 1])

    with col1:
        titulos_pagina(" Mapa Interativo - Alagoas ", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-map"></i>' )
        layers = [geojson_layer]
        if estados_layer is not None:
            layers.append(estados_layer)
        st.pydeck_chart(
            pdk.Deck(
                layers=layers,
                initial_view_state=view_state,
                tooltip=tooltip,
                map_style="mapbox://styles/mapbox/light-v10"
            ),
            use_container_width=True
        )
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 18px; margin-top: 18px;">
            <span style="font-size: 18px; font-weight: bold;">Menor valor</span>
            <div style="background: linear-gradient(90deg, #e6f4ff, #d2ebff, #b4d8ff, #78b4ff, #3c8cff, #0050c8); width: 320px; height: 28px; border-radius: 12px;"></div>
            <span style="font-size: 18px; font-weight: bold;">Maior valor</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if st.session_state['mun_selecionado']:
            if st.session_state['mun_selecionado'] == "Alagoas":
                df_mun = df_ano
            else:
                df_mun = df_ano[df_ano['NO_MUN'] == st.session_state['mun_selecionado']]

            valor_exportado = df_mun[df_mun['CATEGORIA'] == 'EXPORTACAO']['VL_FOB'].sum()
            valor_importado = df_mun[df_mun['CATEGORIA'] == 'IMPORTACAO']['VL_FOB'].sum()
            saldo_geral = valor_exportado - valor_importado
            top_produtos = df_mun[df_mun['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_SH2_POR')['VL_FOB'].sum().nlargest(3)
            top_paises = df_mun[df_mun['CATEGORIA'] == 'EXPORTACAO'].groupby('NO_PAIS')['VL_FOB'].sum().nlargest(3)
            top_produtos_importados = df_mun[df_mun['CATEGORIA'] == 'IMPORTACAO'].groupby('NO_SH2_POR')['VL_FOB'].sum().nlargest(3)
            top_paises_import = df_mun[df_mun['CATEGORIA'] == 'IMPORTACAO'].groupby('NO_PAIS')['VL_FOB'].sum().nlargest(3)

            saldo_font_color = "#00b894" if saldo_geral >= 0 else "#e17055"
            titulos_pagina("Indicadores", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-chart-bar"></i>')
            st.markdown(f"""
            <div style="display: flex; flex-direction: column; gap: 16px; margin-bottom: 16px;">
                <div style="background: #3064AD; border-radius: 12px; padding: 18px 26px; min-width: 200px; text-align: center;">
                    <div style="font-size: 1.15em; color: #fff; font-weight: 500;">Valor Exportado</div>
                    <div style="font-size: 2em; color: #fff; font-weight: bold;">{formatar_valor_usd(valor_exportado)}</div>
                </div>
                <div style="background: #3064AD; border-radius: 12px; padding: 18px 26px; min-width: 200px; text-align: center;">
                    <div style="font-size: 1.15em; color: #fff; font-weight: 500;">Valor Importado</div>
                    <div style="font-size: 2em; color: #fff; font-weight: bold;">{formatar_valor_usd(valor_importado)}</div>
                </div>
                <div style="background: #3064AD; border-radius: 12px; padding: 18px 26px; min-width: 200px; text-align: center;">
                    <div style="font-size: 1.15em; color: #fff; font-weight: 500;">Saldo</div>
                    <div style="font-size: 2em; color: {saldo_font_color}; font-weight: bold;">{formatar_valor_usd(saldo_geral)}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.write("##")
    st.write("##")
    with st.expander("Principais Parceiros Comerciais (Exportação e Importação)", expanded=True):
        
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown(f"""
            <div style="background: #e3ecfa; border-radius: 10px; padding: 18px 24px; margin-bottom: 12px;">
                <span style="font-size: 1.1em; font-weight: bold; color: #0050c8;">
                    🌎 <u>Exportação: O que {st.session_state['mun_selecionado'].title()} leva ao mundo?</u>
                </span>
                <div style="margin-top: 10px; font-size: 1.05em; color: #111;">
                    <b>Top 3 Produtos Exportados:</b><br>
                    <span>{", ".join(top_produtos.index)}</span>
                </div>
                <div style="margin-top: 8px; font-size: 1.05em; color: #111;">
                    <b>Principais Destinos:</b><br>
                    <span>{", ".join(top_paises.index)}</span>
                </div>
                <div style="margin-top: 10px; font-size: 0.98em; color: #444;">
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div style="background: #e3ecfa; border-radius: 10px; padding: 18px 24px; margin-bottom: 12px;">
                <span style="font-size: 1.1em; font-weight: bold; color: #3064AD;">
                    🚢 <u>Importação: O que chega para {st.session_state['mun_selecionado'].title()}?</u>
                </span>
                <div style="margin-top: 10px; font-size: 1.05em; color: #111;">
                    <b>Top 3 Produtos Importados:</b><br>
                    <span>{", ".join(top_produtos_importados.index)}</span>
                </div>
                <div style="margin-top: 8px; font-size: 1.05em; color: #111;">
                    <b>Principais Origens:</b><br>
                    <span>{", ".join(top_paises_import.index)}</span>
                </div>
                <div style="margin-top: 10px, font-size: 0.98em; color: #444;">
                </div>
            </div>
            """, unsafe_allow_html=True)

    # --- TABELAS (APÓS AS COLUNAS) ---
    
        if st.session_state['mun_selecionado']:
            df_mun = df_ano if st.session_state['mun_selecionado'] == "Alagoas" else df_ano[df_ano['NO_MUN'] == st.session_state['mun_selecionado']]
        
            col1, col2 = st.columns([1, 1])
            # Exportação
            with col1:
                df_parceiros_export = (
                    df_mun[df_mun['CATEGORIA'] == 'EXPORTACAO']
                    .groupby('NO_PAIS')
                    .agg(Valor_Exportado=('VL_FOB', 'sum'))
                    .sort_values('Valor_Exportado', ascending=False)
                    .reset_index()
                )
                if not df_parceiros_export.empty:
                    df_parceiros_export['Valor_Exportado'] = df_parceiros_export['Valor_Exportado'].apply(formatar_valor_usd)
                    df_parceiros_export = add_flag_column(df_parceiros_export, 'NO_PAIS')
                    df_parceiros_export = df_parceiros_export.rename(columns={
                        "Bandeira": "BANDEIRA",
                        "NO_PAIS": "PAÍS",
                        "Valor_Exportado": "VALOR EXPORTADO"
                    })
                    st.markdown("""
                    <style>
                    .stDataFrame thead tr th div {
                        font-weight: bold !important;
                        text-transform: uppercase !important;
                        text-align: center !important;
                        font-size: 1.05em !important;
                    }
                    .stDataFrame tbody td {
                        text-align: center !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    st.data_editor(
                        df_parceiros_export[["BANDEIRA", "PAÍS", "VALOR EXPORTADO"]],
                        hide_index=True,
                        column_config={
                            "BANDEIRA": st.column_config.ImageColumn(
                                label="BANDEIRA", width="small", help="Bandeira do país"
                            ),
                            "PAÍS": st.column_config.Column(
                                label="PAÍS", width="medium", disabled=True
                            ),
                            "VALOR EXPORTADO": st.column_config.Column(
                                label="VALOR EXPORTADO", width="max"
                            ),
                        },
                        use_container_width=True,
                        disabled=True
                    )
                else:
                    st.info("Não há dados de exportação para parceiros comerciais.")

            # Importação
            with col2:
                df_parceiros_import = (
                    df_mun[df_mun['CATEGORIA'] == 'IMPORTACAO']
                    .groupby('NO_PAIS')
                    .agg(Valor_Importado=('VL_FOB', 'sum'))
                    .sort_values('Valor_Importado', ascending=False)
                    .reset_index()
                )
                if not df_parceiros_import.empty:
                    df_parceiros_import['Valor_Importado'] = df_parceiros_import['Valor_Importado'].apply(formatar_valor_usd)
                    df_parceiros_import = add_flag_column(df_parceiros_import, 'NO_PAIS')
                    df_parceiros_import = df_parceiros_import.rename(columns={
                        "Bandeira": "BANDEIRA",
                        "NO_PAIS": "PAÍS",
                        "Valor_Importado": "VALOR IMPORTADO"
                    })
                    st.markdown("""
                    <style>
                    .stDataFrame thead tr th div {
                        font-weight: bold !important;
                        text-transform: uppercase !important;
                        text-align: center !important;
                        font-size: 1.05em !important;
                    }
                    .stDataFrame tbody td {
                        text-align: center !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    st.data_editor(
                        df_parceiros_import[["BANDEIRA", "PAÍS", "VALOR IMPORTADO"]],
                        hide_index=True,
                        column_config={
                            "BANDEIRA": st.column_config.ImageColumn(
                                label="BANDEIRA", width="small", help="Bandeira do país"
                            ),
                            "PAÍS": st.column_config.Column(
                                label="PAÍS", width="medium", disabled=True
                            ),
                            "VALOR IMPORTADO": st.column_config.Column(
                                label="VALOR IMPORTADO", width="max"
                            ),
                        },
                        use_container_width=True,
                        disabled=True
                    )
                else:
                    st.info("Não há dados de importação para parceiros comerciais.")

    # --- TABELA DE EXPORTAÇÃO E IMPORTAÇÃO ---
    # --- GRÁFICO DE SÉRIE TEMPORAL ---
    if st.session_state['mun_selecionado'] == "Alagoas":
        df_mun_hist = df.copy()
    else:
        df_mun_hist = df[df['NO_MUN'] == st.session_state['mun_selecionado']]
    df_exp = df_mun_hist[df_mun_hist['CATEGORIA'] == 'EXPORTACAO'].groupby(df_mun_hist['DATA'].dt.year)['VL_FOB'].sum().reset_index()
    df_imp = df_mun_hist[df_mun_hist['CATEGORIA'] == 'IMPORTACAO'].groupby(df_mun_hist['DATA'].dt.year)['VL_FOB'].sum().reset_index()
    df_saldo = pd.merge(df_exp, df_imp, on='DATA', how='outer', suffixes=('_EXP', '_IMP')).fillna(0)
    df_saldo['SALDO'] = df_saldo['VL_FOB_EXP'] - df_saldo['VL_FOB_IMP']
    superavit_anos = df_saldo[df_saldo['SALDO'] > 0]['DATA'].tolist()
    deficit_anos = df_saldo[df_saldo['SALDO'] < 0]['DATA'].tolist()

    titulos_pagina(f"Série Histórica da Balança Comercial de {st.session_state['mun_selecionado']}", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-chart-line"></i>')
    
    # Reduzir a distância do título ao topo usando CSS
    st.markdown(
        """
        <style>
        .element-container:has(.fa-chart-line) {
            margin-top: -22px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    with st.container():
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_exp['DATA'], y=df_exp['VL_FOB'],
            mode='lines+markers', name='Exportação',
            line=dict(color='#0050c8', width=3)
        ))
        fig.add_trace(go.Scatter(
            x=df_imp['DATA'], y=df_imp['VL_FOB'],
            mode='lines+markers', name='Importação',
            line=dict(color='#7bbcff', width=3, dash='dash')
        ))
        fig.add_trace(go.Scatter(
            x=df_saldo['DATA'], y=df_saldo['SALDO'],
            mode='lines+markers', name='Saldo',
            line=dict(color='#00b894', width=2, dash='dot')
        ))

        for ano in superavit_anos:
            fig.add_vrect(
                x0=ano-0.5, x1=ano+0.5,
                fillcolor="rgba(0,184,148,0.08)",
                layer="below", line_width=0
            )
        for ano in deficit_anos:
            fig.add_vrect(
                x0=ano-0.5, x1=ano+0.5,
                fillcolor="rgba(225,112,85,0.08)",
                layer="below", line_width=0
            )
        for ano in superavit_anos:
            fig.add_vline(
                x=ano, line_width=1, line_dash="dot", line_color="#00b894", opacity=0.5
            )
        for ano in deficit_anos:
            fig.add_vline(
                x=ano, line_width=1, line_dash="dot", line_color="#e17055", opacity=0.5
            )

        fig.update_layout(
            xaxis_title="",  # Remover label do eixo x
            yaxis_title="",
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.18,  # Coloca a legenda abaixo do gráfico
                xanchor="center",
                x=0.5
            ),
            plot_bgcolor="#F0F2F9",
            paper_bgcolor="#F0F2F9",
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False),
            margin=dict(l=20, r=20, t=60, b=20)
        )

        st.markdown(
            """
            <style>
            .element-container:has(.js-plotly-plot) {
            margin-top: -72px !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.plotly_chart(fig, use_container_width=True)