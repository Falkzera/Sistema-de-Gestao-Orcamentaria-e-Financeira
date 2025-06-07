# Cadastro de Processos

Esta página faz parte do sistema e tem como objetivo centralizar e facilitar o cadastro de processos em diferentes bases, de acordo com o perfil e permissão do usuário.

## Lógica Central

A lógica da página é baseada em três pilares principais: autenticação do usuário, carregamento dinâmico da base de dados e exibição de formulários de cadastro específicos para cada tipo de processo.

### 1. Autenticação e Carregamento de Base

- **Autenticação:**  
  O sistema utiliza a função `carregar_base_por_usuario()` (do módulo `utils.auth.auth`) para identificar o usuário logado e determinar a qual base de dados ele tem acesso.  
- **Carregamento Dinâmico:**  
  Com base no usuário, são carregados:
    - O DataFrame correspondente à base permitida.
    - O nome da base principal.
    - O nome da base histórica (quando aplicável).

### 2. Exibição de Formulários de Cadastro

- **Seleção Automática:**  
  Após identificar a base de dados permitida para o usuário, a página exibe automaticamente o formulário de cadastro adequado:
    - Para `"Base Crédito SOP/GEO"`, é exibido o formulário de cadastro de processos de crédito GEO.
    - Para `"Base CPOF"`, é exibido o formulário de cadastro de processos CPOF.
    - Para `"Base TED"`, é exibido o formulário de cadastro de processos TED.  
    etc...
- **Permissões:**  
  Caso o usuário não tenha permissão para nenhuma das bases reconhecidas, é exibido um aviso informando que ele não pode cadastrar processos.

### 3. Componentes Visuais

- **Cabeçalho e Layout:**  
  O layout da página é configurado para ser amplo (`wide`), com título e ícone personalizados, utilizando funções utilitárias para padronização visual (`padrao_importacao_pagina`, `titulos_pagina`).
- **Rodapé:**  
  Um rodapé padronizado é exibido ao final da página, reforçando a identidade visual do sistema.

## Estrutura do Código

- `streamlit_app.py` (ou arquivo correspondente): Página principal de cadastro de processos.
- `utils/ui/display.py`: Funções utilitárias para padronização visual (títulos, rodapé, layout).
- `utils/auth/auth.py`: Função para autenticação e carregamento da base de dados conforme o usuário.
- `utils/cadastrar_processos/cadastro.py`: Funções específicas para exibição e processamento dos formulários de cadastro de cada tipo de processo.

## Fluxo Resumido

1. O usuário acessa a página.
2. O sistema identifica a base de dados permitida para o usuário.
3. O formulário de cadastro correspondente é exibido automaticamente.
4. Caso o usuário não tenha permissão, é exibido um aviso.
5. O rodapé é exibido ao final da página.

---

**Créditos:** Este projeto foi desenvolvido por [Lucas Falcão](https://www.linkedin.com/in/falkzera/).