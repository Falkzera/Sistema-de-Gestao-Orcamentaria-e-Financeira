# Relatórios

Esta página centraliza a geração e download de relatórios especializados do sistema, oferecendo uma interface unificada para criação de documentos analíticos em formato PDF. O módulo combina funcionalidades de atualização de dados, seleção de relatórios e geração automatizada de conteúdo, proporcionando uma solução completa para produção de relatórios governamentais.

## Lógica Central

O sistema opera em três camadas principais: controle de acesso para atualização de dados, seleção e configuração de relatórios, e geração automatizada de documentos PDF com conteúdo dinâmico.

### 1. Sistema de Atualização de Dados (Usuários Privilegiados)

- **Controle de Acesso:**  
  Apenas usuários com permissões elevadas (7 ou mais acessos configurados em `st.secrets["page_access"]`) podem visualizar e utilizar os botões de atualização de dados.
- **Categorias de Atualização:**  
  O sistema oferece quatro grupos de atualização organizados por domínio:
  - **Dados do Boletim:** IBGE (abate de animais, leite industrializado), MDIC (comércio exterior), ANP (preços e produção de combustíveis)
  - **Relatório de Despesas:** Dados completos de despesas da SEFAZ
  - **Dados SEFAZ:** Despesas do ano corrente (dotação comentada para manutenção)
  - **Dados RGF:** Relatório de Gestão Fiscal
- **Feedback Visual:**  
  Cada atualização exibe um spinner com mensagem específica e confirmação de sucesso ao final do processo.

### 2. Seleção e Configuração de Relatórios

#### Relatório CPOF
- **Fonte de Dados:** Base de crédito SOP/GEO carregada via `func_load_base_credito_sop_geo()`
- **Filtros Disponíveis:** Ano e mês através da função `filtro_ano_mes()`
- **Processamento:** Gera dados filtrados para o mês atual e anterior para análises comparativas
- **Descrição:** Panorama detalhado das movimentações orçamentárias do Poder Executivo de Alagoas

#### Boletim Conjuntural Alagoano
- **Composição:** Relatório composto que integra múltiplas análises:
  - IBGE: Abate de animais e leite industrializado
  - MDIC: Comércio exterior
  - ANP: Preços de combustíveis, petróleo, etanol, gás natural e GLP
- **Função Composta:** `montar_relatorio_composto()` executa sequencialmente todas as funções de montagem
- **Descrição:** Análise abrangente dos indicadores econômicos e produtivos de Alagoas

#### Relatório de Despesas dos Órgãos
- **Fonte:** Dados de despesas dos órgãos governamentais
- **Função:** `montar_relatorio_sefaz_despesa()`
- **Descrição:** Análise detalhada das despesas realizadas pelos órgãos do governo

### 3. Sistema de Geração de Relatórios

- **Função Unificada:**  
  `botao_gerar_e_baixar_arquivo()` centraliza a lógica de geração, oferecendo interface consistente para todos os relatórios.
- **Parâmetros Dinâmicos:**  
  Cada relatório pode receber parâmetros específicos (ano, mês, DataFrames filtrados) através do dicionário `parametros_funcao`.
- **Nomenclatura Automática:**  
  Nomes de arquivos são gerados automaticamente com base no tipo de relatório e parâmetros (ex: `Relatorio_CPOF_Janeiro_2024.pdf`).
- **Buffer de Download:**  
  Sistema utiliza `st.session_state["buffer_download"]` para gerenciar downloads em andamento.

## Estrutura do Código

- `streamlit_app.py` (ou arquivo correspondente): Página principal de relatórios.
- `src/base.py`: Função `func_load_base_credito_sop_geo()` para carregamento de dados.
- `src/coleta_de_dados/`: Módulos de atualização de dados por fonte (IBGE, MDIC, ANP, SEFAZ, RGF).
- `utils/confeccoes/`: Diretório de funções de confecção de relatórios:
  - `gerar_baixar_confeccao.py`: Função unificada de geração e download
  - `relatorio/`: Funções específicas de montagem de cada tipo de relatório
  - `formatar.py`: Utilitários de formatação (ex: `mes_por_extenso()`)

## Fluxo de Utilização

1. **Acesso:** O usuário acessa a página de relatórios.
2. **Atualização (Opcional):** Usuários privilegiados podem atualizar dados específicos antes da geração.
3. **Seleção:** O usuário escolhe o tipo de relatório desejado no selectbox.
4. **Configuração:** Dependendo do relatório, são exibidos filtros e opções específicas (ano/mês para CPOF).
5. **Visualização:** Uma descrição detalhada do relatório é exibida em expander.
6. **Geração:** O usuário clica no botão de geração e o sistema processa o relatório.
7. **Download:** O arquivo PDF é automaticamente disponibilizado para download.

## Características Técnicas

- **Modularidade:** Cada relatório possui função de montagem independente, facilitando manutenção.
- **Escalabilidade:** Novos relatórios podem ser facilmente adicionados seguindo o padrão estabelecido.
- **Performance:** Carregamento sob demanda de dados e cache de sessão para otimização.
- **Segurança:** Controle granular de acesso às funcionalidades de atualização.
- **Usabilidade:** Interface intuitiva com descrições detalhadas e feedback visual.

## Considerações de Manutenção

- **Adição de Novos Relatórios:** Criar função de montagem, adicionar à lista de opções e implementar lógica condicional.
- **Atualização de Fontes:** Novas fontes de dados podem ser adicionadas aos grupos de atualização existentes.
- **Personalização:** Parâmetros e filtros podem ser facilmente modificados para cada tipo de relatório.

---

**Créditos:** Este projeto foi desenvolvido por [Lucas Falcão](https://www.linkedin.com/in/falkzera/).