# Histórico Processual

Esta página oferece uma interface centralizada para consulta e visualização do histórico de modificações de processos em diferentes bases do sistema. O módulo permite rastreamento completo das alterações realizadas em cada processo, proporcionando transparência e auditoria das operações realizadas pelos usuários autorizados.

## Lógica Central

O sistema opera com base em três componentes principais: controle de acesso baseado em permissões, seleção dinâmica de bases e processos, e exibição detalhada do histórico de modificações.

### 1. Controle de Acesso e Permissões

- **Autenticação por Usuário:**  
  O sistema verifica o usuário logado através de `st.session_state.get("username")` e consulta suas permissões no arquivo de configuração `st.secrets["base_access"]`.
- **Bases Disponíveis:**  
  Apenas as bases para as quais o usuário possui permissão são exibidas como opções:
  - `"Histórico CPOF"`: Histórico de processos do Comitê de Programação Orçamentária e Financeira
  - `"Histórico Crédito SOP/GEO"`: Histórico de processos de crédito das Secretarias de Orçamento, Planejamento e Gestão
- **Controle de Acesso:**  
  Usuários sem permissão para nenhuma base recebem uma mensagem de aviso e o sistema é interrompido.

### 2. Seleção de Base e Processo

- **Seleção Automática:**  
  Se o usuário possui acesso a apenas uma base, ela é automaticamente selecionada. Caso contrário, é exibido um selectbox para escolha.
- **Mapeamento de Bases:**  
  O sistema utiliza um dicionário `historico_map` para mapear nomes de bases para seus respectivos históricos, garantindo flexibilidade na nomenclatura.
- **Carregamento Dinâmico:**  
  Com base na seleção, o sistema carrega a base correspondente:
  - `func_load_base_cpof()`: Para histórico CPOF
  - `func_load_base_credito_sop_geo()`: Para histórico de crédito SOP/GEO

### 3. Seleção e Visualização de Processos

- **Lista de Processos:**  
  O sistema identifica automaticamente a coluna de identificação do processo (`"Nº do Processo"` ou `"Processo ID"`) e extrai a lista de processos disponíveis.
- **Filtros Aplicados:**  
  Se existem filtros ativos na sessão (`st.session_state.processos_filtrados`), apenas os processos filtrados são exibidos como opções.
- **Remoção de Duplicatas:**  
  A lista de processos é processada para remover duplicatas, mantendo a ordem original através de `dict.fromkeys()`.

### 4. Exibição do Histórico

- **Interface Condicional:**  
  Quando nenhum processo está selecionado, é exibida uma mensagem informativa orientando o usuário.
- **Histórico Detalhado:**  
  Ao selecionar um processo, a função `exibir_historico()` é chamada para renderizar o histórico completo de modificações, incluindo:
  - Data e hora das alterações
  - Usuário responsável pela modificação
  - Campos alterados
  - Valores anteriores e novos

## Estrutura do Código

- `streamlit_app.py` (ou arquivo correspondente): Página principal do histórico processual.
- `src/base.py`: Funções para carregamento das bases de dados (`func_load_base_cpof`, `func_load_base_credito_sop_geo`).
- `utils/ui/display.py`: Funções utilitárias para padronização visual.
- `src/salvar_historico.py`: Função `exibir_historico()` para renderização do histórico de modificações.

## Fluxo de Utilização

1. **Acesso:** O usuário acessa a página e o sistema verifica suas permissões.
2. **Seleção de Base:** O usuário seleciona (ou o sistema seleciona automaticamente) a base de histórico desejada.
3. **Carregamento:** A base correspondente é carregada e os processos disponíveis são listados.
4. **Seleção de Processo:** O usuário escolhe um processo específico da lista disponível.
5. **Visualização:** O histórico completo de modificações do processo selecionado é exibido de forma detalhada.

## Características Técnicas

- **Segurança:** Controle rigoroso de acesso baseado em permissões configuradas em `st.secrets`.
- **Flexibilidade:** Suporte a múltiplas bases com diferentes estruturas de dados.
- **Performance:** Carregamento sob demanda das bases, evitando processamento desnecessário.
- **Usabilidade:** Interface intuitiva com seleção automática quando aplicável.
- **Auditoria:** Rastreamento completo de todas as modificações realizadas nos processos.

## Considerações de Segurança

- **Autenticação:** Verificação obrigatória de usuário logado antes do acesso.
- **Autorização:** Controle granular de acesso por base de dados.
- **Auditoria:** Registro completo de todas as consultas ao histórico.
- **Integridade:** Proteção contra acesso não autorizado a dados sensíveis.

---

**Créditos:** Este projeto foi desenvolvido por [Lucas Falcão](https://www.linkedin.com/in/falkzera/).