# Repositório de Dados

## Lógica Central

A principal funcionalidade do repositório é fornecer dados atualizados sob demanda, gerenciando o processo de atualização de forma transparente para o usuário. Para isso, o sistema utiliza um cache persistente e uma configuração de atualização para cada base de dados.

### 1. Cache Persistente

*   **Objetivo:** Evitar atualizações desnecessárias das bases de dados, economizando recursos e garantindo uma boa experiência para o usuário.
*   **Implementação:**
    *   Um arquivo `.pkl` (pickle) é utilizado para armazenar um dicionário Python. Este dicionário mapeia o `id` de cada base de dados para o timestamp da sua última atualização.
    *   O arquivo de cache é armazenado no Google Drive, garantindo a persistência dos dados entre as sessões.
    *   As funções `read_pickle_file_from_drive` e `save_pickle_file_to_drive` (do módulo `src.google_drive_utils`) são responsáveis por ler e escrever o arquivo de cache, respectivamente.
*   **Funcionamento:**
    *   Na primeira vez que o sistema é executado, o arquivo de cache pode não existir. Nesse caso, a função `load_cache()` retorna um dicionário vazio.
    *   Após a primeira atualização de uma base de dados, o timestamp da atualização é armazenado no cache.
    *   Nas requisições subsequentes, o sistema verifica se o tempo decorrido desde a última atualização é maior do que o intervalo configurado para aquela base.

### 2. Configuração de Atualização

*   **Objetivo:** Definir a frequência com que cada base de dados deve ser atualizada.
*   **Implementação:**
    *   A variável `BASE_UPDATE_CONFIG` é um dicionário que mapeia o `id` de cada base de dados para uma tupla contendo:
        *   A função responsável por atualizar a base de dados (ex: `funcao_ibge_abate_animais`).
        *   O intervalo mínimo entre as atualizações, em horas.
*   **Exemplo:**

    ```python
    BASE_UPDATE_CONFIG = {
        "abate": (funcao_ibge_abate_animais, 12),  # Atualiza a cada 12 horas
        "leite": (funcao_ibge_leite_industrializado, 12),  # Atualiza a cada 12 horas
        # ... outras bases ...
    }
    ```

### 3. Processo de Download e Atualização

1.  **Requisição do Usuário:** O usuário interage com a interface Streamlit e clica no botão de download para uma base de dados específica.
2.  **Identificação da Base:** A função `processar_download()` recebe o nome do arquivo da base de dados e utiliza a lista `bases` para encontrar o `id` correspondente.
3.  **Verificação de Permissão e Atualização:**
    *   O sistema verifica se o usuário possui permissão para atualizar a base de dados (ex: se é um administrador).
    *   **Usuários com Permissão:**
        *   A função `update_base_if_needed()` é chamada com o `id` da base. Esta função:
            *   Verifica se a base de dados está presente na configuração de atualização (`BASE_UPDATE_CONFIG`).
            *   Chama a função `should_update()` para determinar se a base precisa ser atualizada.
            *   Se a atualização for necessária:
                *   A função de atualização específica da base é executada (ex: `funcao_ibge_abate_animais()`).
                *   O timestamp da atualização é armazenado no cache.
            *   **Tratamento de Falhas na Atualização:** Se a atualização falhar por algum motivo (ex: erro no script de coleta), o sistema registra o erro, mas continua com o processo de download da base de dados pré-existente. Isso garante que o usuário sempre receba algum dado, mesmo que não seja a versão mais recente.
        *   O sistema então prossegue com o download da base de dados (atualizada ou pré-existente).
    *   **Usuários sem Permissão:**
        *   O sistema ignora a etapa de atualização e prossegue diretamente com o download da base de dados pré-existente.
4.  **Download dos Dados:** Após a verificação e, possivelmente, a atualização, os dados da base são lidos do Google Drive (usando `read_parquet_file_from_drive()`), convertidos para o formato Excel (usando `convert_to_excel()`) e disponibilizados para download ao usuário.
5.  **Feedback Visual:** Durante o processo de leitura e conversão dos dados, uma barra de progresso é exibida na interface Streamlit para informar o usuário sobre o andamento da operação.

### 4. Funções de Atualização

*   As funções de atualização (ex: `funcao_ibge_abate_animais()`) são responsáveis por obter os dados mais recentes da fonte original (ex: scraping de um site, leitura de uma API) e salvar os dados no Google Drive, no formato Parquet.
*   É importante que essas funções sejam robustas e tratem possíveis erros (ex: falha na conexão com a fonte de dados) para evitar a corrupção do cache.

## Estrutura do Código

*   `streamlit_app.py`: Arquivo principal do aplicativo Streamlit, responsável pela interface do usuário e pela lógica de interação com o usuário.
*   `src/`: Diretório contendo o código fonte do projeto.
    *   `google_drive_utils.py`: Funções utilitárias para leitura e escrita de arquivos no Google Drive.
    *   `coleta_de_dados/`: Diretório contendo as funções de coleta de dados para cada base de dados.
        *   `ibge_abate_animais.py`: Função para coletar dados de abate de animais do IBGE.
        *   `ibge_leite_industrializado.py`: Função para coletar dados de leite industrializado do IBGE.
        *   ... outras funções de coleta ...
    *   `utils/`: Diretório contendo funções utilitárias para a interface do usuário e para a manipulação dos dados.
        *   `ui/`: Diretório contendo funções para exibir elementos na interface do usuário.
            *   `display.py`: Funções para exibir elementos como títulos, rodapés e padrões de importação.
        *   `confeccoes/`: Diretório para funções que preparam os dados para exibição ou download, como a criação de relatórios.
            *   `relatorio.py`: (Exemplo) Funções para gerar relatórios a partir dos dados coletados.

## Adicionando Novas Bases de Dados

Para adicionar uma nova base de dados ao repositório, siga os seguintes passos:

1.  **Crie um script de coleta de dados:**
    *   Crie um novo arquivo Python dentro do diretório `src/coleta_de_dados/`. O nome do arquivo deve ser descritivo da base de dados (ex: `src/coleta_de_dados/minha_nova_base.py`).
    *   Implemente uma função dentro deste arquivo que seja responsável por coletar os dados da fonte original, transformá-los (se necessário) e salvá-los no Google Drive no formato Parquet. Esta função será a função de atualização da base de dados.
2.  **Crie uma função de preparação dos dados (se necessário):**
    *   Se for necessário preparar os dados para exibição ou download (ex: gerar um relatório), crie uma função dentro do diretório `utils/confeccoes/`.
    *   Por exemplo, você pode criar um arquivo `utils/confeccoes/relatorio.py` e implementar uma função que gera um relatório a partir dos dados coletados.
3.  **Atualize a lista `bases`:**
    *   No arquivo `streamlit_app.py`, adicione um novo dicionário à lista `bases` com as informações da nova base de dados (id, nome, arquivo, descrição, tags, icone, tamanho).
4.  **Atualize a configuração de atualização (`BASE_UPDATE_CONFIG`):**
    *   No arquivo `streamlit_app.py`, adicione uma nova entrada ao dicionário `BASE_UPDATE_CONFIG` mapeando o `id` da nova base de dados para a tupla contendo a função de atualização (criada no passo 1) e o intervalo de atualização desejado.

## Lógica da Página do Repositório

A página principal do repositório (`streamlit_app.py`) é responsável por exibir as bases de dados disponíveis e permitir que os usuários as busquem e baixem.

*   **Implementação de Cards:** A página exibe as bases de dados em formato de cards, cada um contendo uma breve descrição da base, algumas tags e um botão de download.
*   **Buscador de Palavras-Chave:** A página possui um buscador de palavras-chave que permite aos usuários filtrarem as bases de dados exibidas com base no nome ou nas tags.
*   **Download:** Ao clicar no botão de download, o sistema verifica se o usuário possui permissão para atualizar a base de dados.
    *   **Usuários com Permissão:** O sistema verifica se a base de dados precisa ser atualizada e, se necessário, a atualiza antes de disponibilizar o download.
    *   **Usuários sem Permissão:** O sistema disponibiliza o download da base de dados pré-existente, sem verificar se ela está atualizada.

## Considerações Adicionais

*   **Gerenciamento de Erros:** O código inclui tratamento de erros para lidar com situações como falha na leitura do cache ou na atualização de uma base de dados.
*   **Interface do Usuário:** A interface do usuário é construída com Streamlit e oferece uma forma intuitiva para os usuários buscarem e baixarem as bases de dados.
*   **Escalabilidade:** Para adicionar novas bases de dados, basta seguir os passos descritos acima.
*   **Segurança:** É importante garantir que as funções de coleta de dados sejam seguras e não exponham informações sensíveis.

---

**Créditos:** Este projeto foi desenvolvido por [Lucas Falcão](https://www.linkedin.com/in/falkzera/).