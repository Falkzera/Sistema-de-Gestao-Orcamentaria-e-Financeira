# Sistema de Gerenciamento de Processos (`base.py`)

## Visão Geral

O arquivo `base.py` dentro da pasta `src` é responsável pelo carregamento e gerenciamento dos dados de processos a partir de planilhas do Google Sheets. O sistema trabalha com dois tipos principais de dados:

- **Processos CPOF**: Processos da Comissão de Programação Orçamentária e Financeira.
- **Processos de Crédito SOP/GEO**: Processos relacionados a créditos da Superintendência de Orçamento e Planejamento/Gerência de Execução Orçamentária.

## Funcionalidades

O módulo implementa quatro funções principais:

- `func_load_base_cpof`: Carrega a base de dados principal dos processos CPOF.
- `func_load_historico_cpof`: Carrega o histórico de modificações dos processos CPOF.
- `func_load_base_credito_sop_geo`: Carrega a base de dados principal dos processos de crédito SOP/GEO.
- `func_load_historico_credito_sop_geo`: Carrega o histórico de modificações dos processos de crédito SOP/GEO.

## Detalhes Técnicos

### Conexão com Google Sheets

O sistema utiliza a biblioteca `streamlit_gsheets` para estabelecer conexão com planilhas do Google Sheets, permitindo leitura e escrita de dados em tempo real.

### Tratamento de Dados

Ao carregar os dados, o sistema realiza as seguintes operações:

- Conversão de tipos de dados para garantir consistência.
- Padronização de campos como "Fonte de Recursos" e "Grupo de Despesas" para string.
- Remoção de espaços em branco nos números de processo.
- Armazenamento dos dados no estado da sessão do Streamlit (`st.session_state`) para acesso rápido.

### Cache e Atualização

- Os dados são armazenados no `st.session_state` para evitar carregamentos desnecessários.
- O parâmetro `forcar_recarregar` permite atualizar os dados quando necessário.
- O parâmetro `ttl=0` garante que os dados sejam sempre atualizados a partir da fonte.

## Uso

Este módulo é utilizado como base para outras funcionalidades do sistema, como:

- Visualização e filtragem de processos.
- Edição de informações de processos.
- Acompanhamento de histórico de modificações.
- Geração de relatórios e análises.

## Dependências

- `pandas`: Para manipulação de dados tabulares.
- `streamlit`: Para interface do usuário.
- `streamlit_gsheets`: Para conexão com Google Sheets.

---

*Este sistema foi desenvolvido para otimizar o fluxo de trabalho no gerenciamento de processos, permitindo maior transparência, rastreabilidade e eficiência na gestão orçamentária.*