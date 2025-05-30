import streamlit as st
import plotly.graph_objects as go
from src.google_drive_utils import read_parquet_file_from_drive
from utils.confeccoes.formatar import formatar_valor2
from utils.ui.display import titulos_pagina

def render_rgf_dashboard():

    with st.container(): # DESPESA COM PESSOAL / RCL AJUSTADA
        st.write('---')
        titulos_pagina("Despesa com Pessoal sobre Receita Corrente Líquida Ajustada", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-chart-line"></i>' )
        with st.container(): 

            @st.cache_data
            def load_data():
                df = read_parquet_file_from_drive('RGF-DESPESA-PESSOAL-RECEITA-CORRENTE-LIQUIDA.parquet')
                return df
            df = load_data()

        with st.container(): # Metricas

            ano_max = df["DATA"].max()
            ano_max_index = df[df["DATA"] == ano_max].index[0]
            ano_anterior = df.iloc[ano_max_index - 1]["DATA"]
            ano_reanterior = df.iloc[ano_max_index - 2]["DATA"]

            col1, col2, col3 = st.columns(3)
            col1.metric(label='Despesa com Pessoal / RCL Ajustada', value=formatar_valor2(df[df['DATA'] == ano_max]['valor'].sum()), delta=ano_max, delta_color='off',border=True)
            col2.metric(label='Despesa com Pessoal / RCL Ajustada', value=formatar_valor2(df[df['DATA'] == ano_anterior]['valor'].sum()), delta=ano_anterior, delta_color='off',border=True)
            col3.metric(label='Despesa com Pessoal / RCL Ajustada', value=formatar_valor2(df[df['DATA'] == ano_reanterior]['valor'].sum()), delta=ano_reanterior, delta_color='off',border=True)

            fig = go.Figure()
            fig.add_trace(go.Bar(x=df['DATA'], y=df['valor'], marker_color ='#095aa2', text=df['valor'].apply(formatar_valor2), textposition='inside', name=f'Despesa com Pessaoal / RCL Ajustada'))
            fig.add_trace(go.Scatter(x=df['DATA'], y=df['valor'], mode='lines+markers', name=''))
            fig.update_layout(title=f' - Despesa com Pessoal / RCL Ajustada - Série histórica',
                                legend=dict(font=dict(size=15), orientation='h', x=0.5, xanchor='center', y=-0.2),
                                xaxis=dict(tickfont=dict(size=15)), yaxis=dict(tickfont=dict(size=15)))
            fig.update_xaxes(dtick='M1', tickformat='%b %Y')
            st.plotly_chart(fig, use_container_width=True)

            st.expander(f':blue[Tabela] - Despesa com Pessoal / RCL Ajustada', expanded=False).data_editor(df, use_container_width=True, hide_index=True)

    with st.container(): # Dívida Consolidada Líquida / RCL Ajustada
        st.write('---')
        st.write('---')
        titulos_pagina("Dívida Consolidada Líquida sobre RCL Ajustada", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-chart-line"></i>' )
        with st.container(): # Carregamento dos Dados
            @st.cache_data
            def load_data():
                df = read_parquet_file_from_drive('RGF-DIVIDA-CONSOLIDADA-LIQUIDA-RECEITA-CORRENTE-LIQUIDA.parquet')
                return df
            df = load_data()
            

        with st.container(): # Metricas e Gráfo

            df = df[df['coluna'].isin(['Até o 3º Quadrimestre'])]
            df['DATA'] = df['DATA'].str.replace('-3 Q', '')
            ano_max = df["DATA"].max()

            col1, col2, col3 = st.columns(3)
            col1.metric(label='Dívida Consolidada Líquida / RCL Ajustada', value=formatar_valor2(df[df['DATA'] == ano_max]['valor'].sum()), delta=ano_max, delta_color='off',border=True)
            col2.metric(label='Dívida Consolidada Líquida / RCL Ajustada', value=formatar_valor2(df['valor'].iloc[-2].sum()), delta=df['DATA'].iloc[-2], delta_color='off',border=True)
            col3.metric(label='Dívida Consolidada Líquida / RCL Ajustada', value=formatar_valor2(df['valor'].iloc[-3].sum()), delta=df['DATA'].iloc[-3], delta_color='off',border=True)

            fig = go.Figure()
            fig.add_trace(go.Bar(x=df['DATA'], y=df['valor'], marker_color ='#095aa2', text=df['valor'].apply(formatar_valor2), textposition='inside', name=f'Dívida Consolidada Líquida / RCL Ajustada'))
            fig.add_trace(go.Scatter(x=df['DATA'], y=df['valor'], mode='lines+markers', name=''))
            fig.update_layout(title=f' - Dívida Consolidada Líquida / RCL Ajustada - Série histórica',
                                legend=dict(font=dict(size=15), orientation='h', x=0.5, xanchor='center', y=-0.2),
                                xaxis=dict(tickfont=dict(size=15)), yaxis=dict(tickfont=dict(size=15)))
            fig.update_xaxes(dtick='M1', tickformat='%b %Y')
            st.plotly_chart(fig, use_container_width=True)

            st.expander(f':blue[Tabela] - Dívida Consolidada Líquida / RCL Ajustada', expanded=False).data_editor(df, use_container_width=True, hide_index=True)
    

    with st.container(): # DESPESA COM PESSOAL / RCL AJUSTADA
        st.write('---')
        st.write('---')
        titulos_pagina("Dívida Consolidada sobre RCL Ajustada", font_size="1.9em", text_color="#3064AD", icon='<i class="fas fa-chart-line"></i>' )
        with st.container():
            @st.cache_data
            def load_data():
                df = read_parquet_file_from_drive('RGF-DIVIDA-CONSOLIDADA-RECEITA-CORRENTE-LIQUIDA.parquet')
                return df
            df = load_data()

        with st.container(): # Metricas e Gráfo

            df = df[df['coluna'].isin(['Até o 3º Quadrimestre'])]
            df['DATA'] = df['DATA'].str.replace('-3 Q', '')
            ano_max = df["DATA"].max()

            col1, col2, col3 = st.columns(3)
            col1.metric(label='Dívida Consolidada / RCL Ajustada', value=formatar_valor2(df[df['DATA'] == ano_max]['valor'].sum()), delta=ano_max, delta_color='off',border=True)
            col2.metric(label='Dívida Consolidada / RCL Ajustada', value=formatar_valor2(df['valor'].iloc[-2].sum()), delta=df['DATA'].iloc[-2], delta_color='off',border=True)
            col3.metric(label='Dívida Consolidada / RCL Ajustada', value=formatar_valor2(df['valor'].iloc[-3].sum()), delta=df['DATA'].iloc[-3], delta_color='off',border=True)

            fig = go.Figure()
            fig.add_trace(go.Bar(x=df['DATA'], y=df['valor'], marker_color ='#095aa2', text=df['valor'].apply(formatar_valor2), textposition='inside', name=f'Dívida Consolidada / RCL Ajustada'))
            fig.add_trace(go.Scatter(x=df['DATA'], y=df['valor'], mode='lines+markers', name=''))
            fig.update_layout(title=f' - Dívida Consolidada / RCL Ajustada - Série histórica',
                                legend=dict(font=dict(size=15), orientation='h', x=0.5, xanchor='center', y=-0.2),
                                xaxis=dict(tickfont=dict(size=15)), yaxis=dict(tickfont=dict(size=15)))
            fig.update_xaxes(dtick='M1', tickformat='%b %Y')
            st.plotly_chart(fig, use_container_width=True)

            st.expander(f':blue[Tabela] - Dívida Consolidada / RCL Ajustada', expanded=False).data_editor(df, use_container_width=True, hide_index=True)