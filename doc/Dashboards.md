# Dashboards

Esta página centraliza o acesso a diferentes dashboards e painéis de visualização de dados, oferecendo uma interface unificada para análise de informações orçamentárias, comerciais e fiscais. O sistema permite navegação fluida entre diferentes tipos de visualizações, cada uma especializada em um domínio específico de dados governamentais.

## Lógica Central

A página funciona como um hub de dashboards, utilizando um sistema de navegação por abas virtuais que mantém o estado da sessão do usuário e renderiza dinamicamente o conteúdo correspondente à seleção atual.

### 1. Sistema de Navegação por Abas

- **Estado de Sessão:**  
  O sistema utiliza `st.session_state["pagina_atual"]` para manter o controle de qual dashboard está sendo visualizado, garantindo persistência durante a sessão do usuário.
- **Inicialização Padrão:**  
  Por padrão, o sistema inicializa com o "Observatório do Orçamento" como página ativa, proporcionando uma experiência consistente ao usuário.
- **Navegação Interativa:**  
  Três botões principais permitem alternar entre os dashboards disponíveis, com recarregamento automático da página para atualizar o conteúdo.

### 2. Dashboards Disponíveis

#### Observatório do Orçamento
- **Tipo:** Dashboard externo (Power BI)
- **Funcionalidade:** Análise orçamentária pública com link direto para visualização no Power BI
- **Implementação:** Utiliza a função `observatorio_orcamento()` para renderizar componentes adicionais

#### Mapa do Comércio Exterior
- **Tipo:** Dashboard interno personalizado
- **Funcionalidade:** Visualização geográfica e analítica do comércio exterior
- **Implementação:** Renderizado através da função `render_mdic_comercio_exterior_dashboard()`

#### Dashboard - RGF (Relatório de Gestão Fiscal)
- **Tipo:** Dashboard interno especializado
- **Funcionalidade:** Análise de indicadores fiscais e de gestão pública
- **Implementação:** Renderizado através da função `render_rgf_dashboard()`

### 3. Renderização Condicional

- **Lógica de Exibição:**  
  O sistema utiliza estruturas condicionais (`if/elif`) para renderizar apenas o dashboard selecionado, otimizando performance e experiência do usuário.
- **Carregamento Dinâmico:**  
  Cada dashboard é carregado sob demanda, evitando processamento desnecessário de dados não visualizados.

## Estrutura do Código

- `streamlit_app.py` (ou arquivo correspondente): Página principal de dashboards com sistema de navegação.
- `utils/ui/display.py`: Funções utilitárias para padronização visual e layout.
- `utils/confeccoes/dashboards/`: Diretório contendo as implementações específicas de cada dashboard:
  - `rgf_dashboard.py`: Dashboard do Relatório de Gestão Fiscal
  - `mdic_comercio_exterior_dashboard.py`: Dashboard do Comércio Exterior
  - `paines_externos.py`: Integrações com dashboards externos (Power BI, etc.)

## Fluxo de Navegação

1. **Acesso Inicial:** O usuário acessa a página e visualiza três botões de navegação com o "Observatório do Orçamento" pré-selecionado.
2. **Seleção:** O usuário clica em um dos botões para alternar entre os dashboards disponíveis.
3. **Atualização de Estado:** O sistema atualiza `st.session_state["pagina_atual"]` e executa `st.rerun()` para recarregar a página.
4. **Renderização:** O dashboard correspondente é renderizado dinamicamente com base na seleção atual.
5. **Interação:** O usuário pode interagir com o dashboard ativo e alternar para outros quando necessário.

## Características Técnicas

- **Performance:** Carregamento sob demanda evita processamento desnecessário de múltiplos dashboards simultaneamente.
- **Responsividade:** Layout configurado como "wide" para melhor aproveitamento do espaço em tela.
- **Integração Externa:** Suporte a dashboards externos via iframe e links diretos.
- **Modularidade:** Cada dashboard é implementado em módulo separado, facilitando manutenção e expansão.

## Expansibilidade

Para adicionar novos dashboards:
1. Criar a função de renderização em `utils/confeccoes/dashboards/`
2. Adicionar botão de navegação na interface principal
3. Incluir condição de renderização no sistema de navegação
4. Importar a função de renderização no início do arquivo

---

**Créditos:** Este projeto foi desenvolvido por [Lucas Falcão](https://www.linkedin.com/in/falkzera/).