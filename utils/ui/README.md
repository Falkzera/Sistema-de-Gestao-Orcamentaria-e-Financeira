# Módulo de Interface (display.py)

Este módulo contém funções para personalizar a interface do usuário no Streamlit, com foco na barra lateral e cabeçalhos da aplicação do Sistema de Gestão Orçamentária.

## Funções Disponíveis

### `ocultar_barra_lateral_streamlit()`
Remove a barra de navegação padrão do Streamlit usando CSS personalizado.

### `configurar_sidebar_marca()`
Exibe o logo de ALAGOAS no topo da barra lateral e adiciona um separador visual.

### `configurar_cabecalho_principal()`
Configura o cabeçalho principal da aplicação, exibindo o título "Sistema de Gestão Orçamentária" e o logo da SEPLAG em colunas separadas.

### `exibir_info_usuario_sidebar()`
Exibe o nome do usuário logado em uma caixa estilizada na barra lateral, quando disponível no `session_state`.

### `customizar_sidebar()`
Função principal que aplica todas as personalizações de interface, incluindo ocultar a barra lateral padrão, configurar a marca, o cabeçalho e exibir informações do usuário.
