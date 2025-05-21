import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional
from utils.opcoes_coluna.deliberacao import mapa_cores_deliberacao, opcoes_deliberacao
from utils.opcoes_coluna.situacao import mapa_cores_situacao, opcoes_situacao

from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, DataReturnMode, GridUpdateMode

# Adicione este código com as constantes (perto de CELL_STYLE_PADRAO)
BUTTON_RENDERER = JsCode('''
class BtnCellRenderer {
    init(params) {
        this.params = params;
        this.eGui = document.createElement('div');
        this.eGui.innerHTML = `
        <span>
            <style>
            .streamlit-button {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 4px 8px;
                text-align: center;
                font-size: 12px;
                margin: 2px;
                cursor: pointer;
                border-radius: 4px;
                font-family: inherit;
            }
            .streamlit-button:hover {
                opacity: 0.8;
            }
            </style>
            <button 
                class="streamlit-button"
                onclick="window.parent.postMessage({
                    type: 'streamlit:buttonClick',
                    key: 'botao_' + params.data['Nº do Processo']
                }, '*')"
                >Ação</button>
        </span>
        `;
    }
    getGui() { return this.eGui; }
}
''')

# Estilos e JS reutilizáveis
CELL_STYLE_PADRAO = JsCode(
    "function(params) {"
    "  return {"
    "    'textAlign': 'center',"
    "    'display': 'flex',"
    "    'alignItems': 'center',"
    "    'justifyContent': 'center'"
    "  };"
    "}"
)

CSS_CUSTOMIZADO = {
    ".ag-header": {"background-color": "#3064ad !important"}, # Cor do cabeçalho
    ".ag-header-cell-label": {
        "color": "#ffffff !important", # Cor do texto do cabeçalho
        "font-weight": "650", 
        "font-size": "12px",
        "justify-content": "center",
    },
    ".ag-cell": {
        "font-size": "12px", 
        "line-height": "1.4",
        "border-color": "#e6e6e6", # Cor da borda das células
    },
    ".ag-row-hover": {"background-color": "#e8f0fe !important"}, # Cor do hover
    ".ag-row-selected": {"background-color": "#d0e8ff !important"}, # Cor da linha selecionada
    ".ag-root-wrapper": {"border": "1px solid #e0e0e0", "border-radius": "8px"},
}

def build_grid_options(
    columns: tuple,
    altura_max_linhas: int,
    enable_click: bool,
    set_filter_cols: list[str] = None,
    unique_vals: dict[str,list] = None,
    editable_columns: list[str] = None,
    editable_columns_deliberacao: list[str] = None,
    button_column: str = None,
    parecer_options: list[str] = None,
    # Os argumentos flexíveis agora são opcionais e definidos automaticamente
    mapa_cores_coluna: dict = None,
    opcoes_coluna: list = None,
    nome_coluna_status: str = None,
    editable_colunas_especiais: bool = False  # NOVO
) -> Dict[str, Any]:
    """
    Gera e retorna o dict de gridOptions para AgGrid com base nas colunas,
    quantidade de linhas por página e se permite clique.
    Permite customizar qual coluna terá cor e opções (ex: Deliberação ou Situação).
    """
    # Criamos um DataFrame vazio apenas para inicializar o builder
    empty_df = pd.DataFrame({col: [] for col in columns})
    gb = GridOptionsBuilder.from_dataframe(empty_df)

    # Configurações padrão de coluna
    gb.configure_default_column(
        resizable=True,
        autoHeight=False,
        wrapText=True,
        maxWidth=600,
        minWidth=100,
        sortable=True,
        filter=False,
        floatingFilter=False,
        cellStyle=CELL_STYLE_PADRAO,
        enableRowGroup=True,    # permite agrupar linhas
        enablePivot=True,       # permite usar como coluna de pivot
        enableValue=True, 
    )

    # Paginação ao invés de scroll manual
    gb.configure_pagination(
        paginationAutoPageSize=False,
        paginationPageSize=20, # Máx pages
    )

    gb.configure_side_bar()

    # dentro da função build_grid_options, antes do gb.build()
    if "Valor" in columns:
        gb.configure_column(
            "Valor",
            type=["numericColumn"],      # habilita tratamento numérico
            aggFunc="sum",               # usa soma como agregação padrão
            valueFormatter=JsCode("""
                function(params) {
                    if (params.value == null) return '';
                    // toLocaleString no pt-BR com 2 dígitos
                    return 'R$ ' + params.value.toLocaleString('pt-BR', {
                        minimumFractionDigits: 2,
                        maximumFractionDigits: 2
                    });
                }
            """)
        )

    # Seleção de linha e callback de duplo clique
    if enable_click:
        gb.configure_selection(selection_mode="single", use_checkbox=False)
        gb.configure_grid_options(
            onRowDoubleClicked=JsCode(
                "function(event) {"
                "  window.parent.postMessage({"
                "    type: 'row_double_click',"
                "    data: event.data"
                "  }, '*');"
                "}"
            )
        )

    # --- DETECÇÃO AUTOMÁTICA DE SITUAÇÃO OU DELIBERAÇÃO ---
    # Se não foi passado explicitamente, detecta automaticamente
    if not nome_coluna_status:
        if "Situação" in columns:
            nome_coluna_status = "Situação"
            mapa_cores_coluna = mapa_cores_situacao
            opcoes_coluna = opcoes_situacao
        elif "Deliberação" in columns:
            nome_coluna_status = "Deliberação"
            mapa_cores_coluna = mapa_cores_deliberacao
            opcoes_coluna = opcoes_deliberacao

    # Estilo condicional da coluna de status (deliberacao/situacao), se existir
    if nome_coluna_status and nome_coluna_status in columns and mapa_cores_coluna:
        mapa_js = ", ".join(f"'{sit}': '{cor}'" for sit, cor in mapa_cores_coluna.items())
        cell_style_status = JsCode(
            "function(params) {\n"
            f"  let cor = {{{mapa_js}}};\n"
            "  return {\n"
            "    backgroundColor: cor[params.value] || '#ffffff',\n"
            "    color: 'black',\n"
            "    fontWeight: '500',\n"
            "    textAlign: 'center',\n"
            "    display: 'flex',\n"
            "    alignItems: 'center',\n"
            "    justifyContent: 'center'\n"
            "  };\n"
            "}"
        )
        gb.configure_column(nome_coluna_status, cellStyle=cell_style_status)

    # Se foi passada alguma coluna para Set Filter, configura cada uma
    if set_filter_cols:
        for col in set_filter_cols:
            # entrega a lista de valores únicos para popular o checkbox
            # (pode também passar um filterParams fixo se quiser)
            gb.configure_column(
                col,
                filter="agSetColumnFilter",
                filterParams={
                    "values": sorted(empty_df[col].dropna().unique().tolist()),
                    "suppressSelectAll": False,
                    "suppressMiniFilter": False
                }
            )

    # se houver colunas para Set Filter, use unique_vals
    if set_filter_cols and unique_vals:
        for col in set_filter_cols:
            gb.configure_column(
                col,
                filter="agSetColumnFilter",
                filterParams={
                    "values": unique_vals[col],
                    "suppressSelectAll": False,
                    "suppressMiniFilter": False
                }
            )


    # Habilitar edição nas colunas especificadas
    if editable_columns:
        destaque_style = JsCode("""
            function(params) {
                return {
                    backgroundColor: '#e3f0ff',
                    fontWeight: 'bold',
                    textAlign: 'center',
                    color: params.value ? '#222' : '#888',
                    fontStyle: params.value ? 'normal' : 'italic',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    borderBottom: '2px dashed #7da6d9',
                    cursor: 'pointer'
                };
            }
        """)
        # Suporte a opções por linha (dict: idx -> lista de opções)
        for col in editable_columns:
            if isinstance(parecer_options, dict):
                # Use cellEditorParams como função para opções dinâmicas por linha
                gb.configure_column(
                    col,
                    editable=True,
                    cellEditorSelector=JsCode("""
                        function(params) {
                            var opcoes = %s[params.node.rowIndex] || ["", "Digitar Manualmente", "Aprovado", "Indeferimento", "Diligênciar", "Verificar"];
                            if (params.value === "Digitar Manualmente") {
                                return { component: 'agTextCellEditor' };
                            }
                            return {
                                component: 'agSelectCellEditor',
                                params: {
                                    values: opcoes,
                                    cellEditorPopup: true,
                                    useFormatter: true
                                }
                            };
                        }
                    """ % str(parecer_options)),
                    # cellStyle=destaque_style,
                    pinned="right",
                    valueFormatter=JsCode("""
                        function(params) {
                            if (!params.value) {
                                return "Insira seu parecer";
                            }
                            return params.value;
                        }
                    """)
                )
            else:
                opcoes = parecer_options or ["Aprovado", "Indeferimento", "Diligênciar", "Verificar"]
                opcoes_com_extra = ["", "Digitar Manualmente"] + opcoes
                gb.configure_column(
                    col,
                    editable=True,
                    cellEditorSelector=JsCode("""
                        function(params) {
                            if (params.value === "Digitar Manualmente") {
                                return { component: 'agTextCellEditor' };
                            }
                            return {
                                component: 'agSelectCellEditor',
                                params: {
                                    values: %s,
                                    cellEditorPopup: true,
                                    useFormatter: true
                                }
                            };
                        }
                    """ % str(opcoes_com_extra)),
                    cellStyle=destaque_style,
                    pinned="right",
                    valueFormatter=JsCode("""
                        function(params) {
                            if (!params.value) {
                                return "Insira seu parecer";
                            }
                            return params.value;
                        }
                    """)
                )


    # EDITÁVEL PARA DELIBERAÇÃO/SITUAÇÃO (agora automático se editable_colunas_especiais)
    if editable_colunas_especiais and editable_columns_deliberacao is None:
        if nome_coluna_status and nome_coluna_status in columns:
            editable_columns_deliberacao = [nome_coluna_status]

    if editable_columns_deliberacao and opcoes_coluna:
        for col in editable_columns_deliberacao:
            gb.configure_column(
                col,
                editable=True,
                cellEditorSelector=JsCode(f"""
                    function(params) {{
                    return {{
                        component: 'agSelectCellEditor',
                        params: {{
                        values: {opcoes_coluna},
                        cellEditorPopup: true,
                        useFormatter: true
                        }}
                    }};
                    }}
                """),
                valueFormatter=JsCode("""
                    function(params) {
                    if (!params.value) {
                        return "Selecione uma opção";
                    }
                    return params.value;
                    }
                """)
            )


    if button_column:
        gb.configure_column(
            field=button_column,
            header_name="Ação",
            cellRenderer=BUTTON_RENDERER,
            lockPosition="right",
            pinned="right",
            width=100,
            filter=False,
            sortable=False,
            editable=False
        )


    opts = gb.build()
    opts["autoHeaderHeight"] = True
    opts["enableRangeSelection"]        = True   # permite selecionar células individualmente
    opts["suppressCopyRowsToClipboard"] = True   # impede copiar a linha inteira
    opts["suppressRowClickSelection"] = False

      # <<< Duplo‑clique copia a célula >>>
    opts["onCellDoubleClicked"] = JsCode("""
    +   function(event) {
    +       // limpa seleção anterior
    +       event.api.clearRangeSelection();
    +       // seleciona só esta célula
    +       event.api.addCellRange({
    +           rowStartIndex: event.rowIndex,
    +           rowEndIndex: event.rowIndex,
    +           columns: [event.column.getId()]
    +       });
    +       // copia o conteúdo do range (esta célula) para o clipboard
    +       event.api.copySelectedRangeToClipboard();
    +   }
    +   """)

    return opts

def mostrar_tabela(
    df: pd.DataFrame,
    altura_max_linhas: int = None,
    nome_tabela: str = "",
    mostrar_na_tela: bool = False,
    enable_click: bool = False,
    editable_columns: list[str] = None,
    editable_columns_deliberacao: list[str] = None,
    button_column: str = None,
    parecer_options: list[str] = None,
    editable_colunas_especiais: bool = False  # NOVO
) -> tuple[pd.DataFrame, dict | None]:
    """
    Exibe um DataFrame no Streamlit com AgGrid e retorna:
     - df_filtrado: DataFrame já aplicado com os filtros do usuário
     - selected_row: dict da linha selecionada (se enable_click=True e houver duplo clique)
    """
    if not mostrar_na_tela:
        return df, None

    # Inicializa session_state para this tabela, se necessário
    for key in ("grid_options", "filtros", "ordenacao"):
        estado = f"{key}_{nome_tabela}"
        if estado not in st.session_state:
            st.session_state[estado] = None

    # Definição das opções de filtros
    UNIQUE_THRESHOLD = 100
    # encontra colunas de texto com poucos valores únicos
    set_filter_cols = [
        col for col in df.select_dtypes(include=['object', 'category']).columns
        if df[col].nunique() <= UNIQUE_THRESHOLD and col not in ["Última Edição", "Cadastrado Por"]
    ]

    # Aqui vem a diferença: pegue os valores do df de verdade
    unique_vals = {
        col: (df[col].dropna().unique().tolist())
        for col in set_filter_cols
    }

    # Configuração dos botões (nova implementação)
    if button_column and mostrar_na_tela:
        if 'Nº do Processo' not in df.columns:
            df['Nº do Processo'] = range(len(df))  # Cria um Nº do Processo temporário se não existir
        
        # Adiciona o listener JavaScript para os botões
        st.markdown("""
        <script>
        window.addEventListener('message', (event) => {
            if (event.data.type === 'streamlit:buttonClick') {
                const key = event.data.key;
                Streamlit.setComponentValue(key);
            }
        });
        </script>
        """, unsafe_allow_html=True)
        
        # Cria um componente para capturar os cliques
        button_clicked = st.empty()

    # Constrói grid_options (cacheado)
    grid_options = build_grid_options(
        columns=tuple(df.columns),
        altura_max_linhas=altura_max_linhas,
        enable_click=enable_click,
        set_filter_cols=set_filter_cols,
        unique_vals=unique_vals,
        editable_columns=editable_columns,
        editable_columns_deliberacao=editable_columns_deliberacao,
        button_column=button_column,
        parecer_options=parecer_options,
        editable_colunas_especiais=editable_colunas_especiais  # NOVO
    )

    # Restaura filtros e ordenação do último estado
    filtros_key = f"filtros_{nome_tabela}"
    ordenacao_key = f"ordenacao_{nome_tabela}"
    if st.session_state[filtros_key]:
        grid_options["initialFilterModel"] = st.session_state[filtros_key]
    if st.session_state[ordenacao_key]:
        grid_options["initialSortModel"] = st.session_state[ordenacao_key]

    # Título
    st.markdown(f"##### {nome_tabela}")

    num_linhas = len(df)  # Número de linhas no DataFrame
    altura_dinamica = num_linhas * 160  # 40px por linha, ajustável conforme necessário
    altura_max = 500  # Altura máxima (ajuste conforme necessário)
    height = min(altura_dinamica, altura_max)
    
    # Renderiza a AgGrid
    response = AgGrid(
        df,
        gridOptions=grid_options,
        theme="alpine",
        allow_unsafe_jscode=True,
        custom_css=CSS_CUSTOMIZADO,
        height=height,
        width='2%',
        reload_data=True,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        enable_enterprise_modules=enable_click,
        return_mode="AS_INPUT" if enable_click else "NONE",
    )

    # Armazena filtros e ordenação atuais
    st.session_state[filtros_key] = response.get("filter_model")
    st.session_state[ordenacao_key] = response.get("sort_model")

    df_filtrado_pelo_grid = pd.DataFrame(response["data"])

    # Se click estiver habilitado, captura a linha selecionada
    selected_row = None
    if enable_click:
        try:
            sel = response.get("selected_rows")
            if isinstance(sel, list) and sel:
                selected_row = sel[0]
            elif hasattr(sel, "iloc") and len(sel) > 0:
                selected_row = sel.iloc[0].to_dict()
        except Exception:
            st.error("Não foi possível obter a linha selecionada.")

    clicked_row = None
    if button_column and mostrar_na_tela:
        clicked_key = button_clicked.text_input("", key=f"button_click_{nome_tabela}", label_visibility="collapsed")
        if clicked_key:
            clicked_id = clicked_key.replace("botao_", "")
            clicked_row = df[df['Nº do Processo'] == clicked_id].iloc[0].to_dict()
            st.toast(f"Ação acionada para processo: {clicked_id}")
            # Limpa o estado após uso
            button_clicked.text_input("", value="", key=f"button_reset_{nome_tabela}", label_visibility="collapsed")

    return df_filtrado_pelo_grid, selected_row