# Canal de Manifestação Técnica

Esta página é um sistema especializado para gerenciar manifestações técnicas dos membros do CPOF (Comitê de Programação Orçamentária e Financeira). A interface permite que cada membro visualize, filtre e responda aos processos que aguardam sua análise, mantendo um controle rigoroso do fluxo de trabalho e das responsabilidades individuais.

## Lógica Central

O sistema opera com base em três componentes principais: autenticação e identificação do membro, filtragem dinâmica de processos por status de resposta, e interface de edição para manifestações técnicas.

### 1. Autenticação e Identificação do Membro

- **Membros Autorizados:**  
  O sistema reconhece cinco membros oficiais do CPOF.
- **Identificação Automática:**  
  Se o usuário logado corresponder a um dos membros oficiais, o sistema automaticamente o identifica e exibe seus processos específicos.
- **Seleção Manual:**  
  Para usuários que não são membros oficiais (ex: administradores), é disponibilizado um selectbox para escolher qual membro visualizar.

### 2. Carregamento e Filtragem da Base de Dados

- **Base Principal:**  
  A função `func_load_base_cpof()` carrega a base de dados completa do CPOF, forçando o recarregamento para garantir dados atualizados.
- **Critério de Exibição:**  
  Apenas processos com status `"Disponível aos Membros CPOF"` na coluna `Deliberação` são exibidos. Este critério pode ser facilmente alterado para outros status como `"Em Análise"` ou `"Em Revisão"`.  
  Isso pode ser modificado.

- **Separação por Status de Resposta:**  
  Os processos são automaticamente separados em duas categorias:
    - **Aguardando Resposta:** Processos onde a coluna do membro está vazia (null, vazio ou espaço).
    - **Respondidos:** Processos onde a coluna do membro já possui alguma manifestação.

### 3. Interface de Navegação e Edição

- **Indicadores Visuais:**  
  Dois botões principais exibem a quantidade de processos em cada categoria, permitindo navegação rápida entre eles.
- **Tabela Interativa:**  
  Utiliza a função `mostrar_tabela()` para exibir os processos de forma interativa, com a coluna do membro atual editável.
- **Sistema de Modificações:**  
  O sistema `inicializar_e_gerenciar_modificacoes()` monitora alterações feitas pelo usuário e habilita o botão de salvamento apenas quando há modificações pendentes.

### 4. Persistência de Dados

- **Salvamento Seguro:**  
  As modificações são salvas através da função `salvar_modificacoes_selectbox_mae()`, que atualiza tanto a base principal quanto o histórico.
- **Recarregamento Automático:**  
  Após salvar, a página é automaticamente recarregada para refletir as alterações mais recentes.

## Estrutura do Código

- `streamlit_app.py` (ou arquivo correspondente): Página principal do canal de manifestação técnica.
- `src/base.py`: Função `func_load_base_cpof()` para carregamento da base de dados do CPOF.
- `utils/ui/display.py`: Funções utilitárias para padronização visual.
- `utils/ui/dataframe.py`: Função `mostrar_tabela()` para exibição interativa de dados.
- `src/salvar_alteracoes.py`: Funções para gerenciamento e persistência de modificações.

## Fluxo de Trabalho

1. **Acesso:** O usuário acessa a página e é automaticamente identificado como membro do CPOF ou seleciona manualmente o membro.
2. **Visualização:** São exibidos dois botões com contadores de processos aguardando resposta e já respondidos.
3. **Seleção:** O usuário clica em um dos botões para visualizar a categoria desejada.
4. **Análise:** Uma tabela interativa exibe os processos, permitindo que o usuário clique em uma linha para editá-la.
5. **Manifestação:** O usuário pode inserir ou editar sua manifestação técnica na coluna correspondente.
6. **Salvamento:** Quando há modificações, o botão "Salvar" é habilitado para persistir as alterações.
7. **Atualização:** Após salvar, a página é recarregada com os dados atualizados.

## Considerações Técnicas

- **Performance:** A base é recarregada a cada acesso para garantir dados sempre atualizados.
- **Segurança:** Apenas membros autorizados podem fazer modificações, com controle de acesso baseado no usuário logado.
- **Auditoria:** Todas as modificações são registradas no histórico para fins de auditoria.
- **Flexibilidade:** O critério de exibição pode ser facilmente alterado modificando a variável `base_mostrar`.

---

**Créditos:** Este projeto foi desenvolvido por [Lucas Falcão](https://www.linkedin.com/in/falkzera/).