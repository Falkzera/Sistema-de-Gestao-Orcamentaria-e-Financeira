# Visualizador de Processos

Esta página oferece uma interface robusta para consulta, edição e análise de processos, permitindo ao usuário visualizar, filtrar, editar e resumir informações de acordo com suas permissões. O sistema foi projetado para ser flexível, seguro e eficiente, centralizando todas as operações relacionadas à gestão de processos em um único ambiente.

## Lógica Central

A página é estruturada em quatro grandes blocos: carregamento e filtragem da base, exibição e edição da tabela, edição detalhada de processos e apresentação de resumos analíticos.

### 1. Carregamento e Filtragem da Base

- **Carregamento Dinâmico:**  
  A função `carregar_base_por_usuario(apenas_base=True)` carrega a base de dados específica para o usuário logado, respeitando suas permissões de acesso.
- **Filtros de Busca:**  
  A função `filtros_de_busca(df)` permite ao usuário aplicar múltiplos filtros sobre a base, facilitando a localização de processos específicos e otimizando a navegação em grandes volumes de dados.

### 2. Exibição e Edição da Tabela

- **Tabela Interativa:**  
  A função `mostrar_tabela()` exibe os dados em formato de tabela, permitindo edição direta de colunas especiais, seleção de linhas e interação dinâmica.
- **Indicadores Dinâmicos:**  
  Se a coluna "Valor" estiver presente, o sistema exibe automaticamente o valor total somado e a quantidade de processos listados.
- **Gerenciamento de Modificações:**  
  O sistema monitora alterações feitas pelo usuário através de `inicializar_e_gerenciar_modificacoes(selected_row)`. Quando há modificações pendentes, o botão "Salvar" é habilitado.
- **Persistência Segura:**  
  Ao salvar, as alterações são registradas tanto na base principal quanto na base histórica, garantindo rastreabilidade e integridade dos dados. A página é recarregada automaticamente após o salvamento.

### 3. Edição Detalhada de Processos

- **Expansor de Edição:**  
  Quando uma linha é selecionada e não há modificações pendentes, um expansor é exibido permitindo a edição detalhada do processo selecionado via `editar_unico_processo()`.
- **Contexto Completo:**  
  O expansor exibe o número do processo e oferece uma interface dedicada para ajustes finos, sem comprometer a visualização geral da tabela.

### 4. Resumos Analíticos

- **Resumos por Permissão:**  
  A função `mostrar_resumos_por_permissao(df, nome_base)` apresenta resumos e análises customizadas de acordo com o perfil do usuário e a base acessada, facilitando a tomada de decisão e o acompanhamento gerencial.

## Estrutura do Código

- `streamlit_app.py` (ou arquivo correspondente): Página principal do visualizador de processos.
- `utils/ui/display.py`: Funções utilitárias para padronização visual.
- `utils/ui/dataframe.py`: Função `mostrar_tabela()` para exibição e edição de dados.
- `utils/auth/auth.py`: Função `carregar_base_por_usuario()` para controle de acesso.
- `utils/filtros/filtro.py`: Função `filtros_de_busca()` para aplicação de filtros dinâmicos.
- `src/salvar_alteracoes.py`: Funções para gerenciamento e persistência de modificações.
- `src/editar_processo_geral.py`: Função `editar_unico_processo()` para edição detalhada.
- `utils/confeccoes/resumos.py`: Função `mostrar_resumos_por_permissao()` para exibição de resumos analíticos.

## Fluxo de Utilização

1. **Acesso:** O usuário acessa a página e a base de dados correspondente ao seu perfil é carregada.
2. **Filtragem:** O usuário aplica filtros para refinar a visualização dos processos.
3. **Visualização e Edição:** A tabela interativa permite seleção e edição de processos. Modificações podem ser salvas diretamente.
4. **Edição Detalhada:** O usuário pode expandir um processo selecionado para edição detalhada.
5. **Resumos:** São exibidos resumos e análises customizadas ao final da página.

## Características Técnicas

- **Performance:** Carregamento e filtragem otimizados para grandes volumes de dados.
- **Segurança:** Controle rigoroso de acesso e rastreabilidade de modificações.
- **Usabilidade:** Interface intuitiva, com feedback visual e navegação fluida.
- **Modularidade:** Cada funcionalidade é implementada em módulo separado, facilitando manutenção e expansão.

## Considerações de Manutenção

- **Otimização:** O carregamento da base pode ser otimizado para evitar recarregamentos desnecessários.
- **Expansibilidade:** Novos filtros, colunas editáveis e resumos podem ser facilmente adicionados seguindo o padrão atual.
- **Auditoria:** Todas as alterações são registradas na base histórica para fins de auditoria e rastreamento.

---

**Créditos:** Este projeto foi desenvolvido por [Lucas Falcão](https://www.linkedin.com/in/falkzera/).