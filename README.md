📁 Projeto
├── 📁 .streamlit/
│   └── config.toml (Estilização streamlit)
├── 📁 image/ (imagens utilizadas durante o aplicativo)
├── 📁 pages/
│   ├── cadastro.py (Página onde o usuário ira cadastrar um processo) - 24 linhas
│   ├── canal_resposta_cpof.py (Página onde os membros do CPOF iram informar o parecer técnico) - 76 linhas
│   ├── dashboards.py (página onde será posto os dashboards) - 30 linhas
│   ├── historico.py (página dedicada a rastrear o histórico de edição dos processos) - 71 linhas
│   ├── login.py (página de login) - 34 linhas
│   ├── relatorio.py (página onde será posto os relatórios para o usuário baixar) - 159 linhas
│   └── visualizar.py (página onde será possível visualizar os processos salvos na base e também editar os mesmos, como também gerar resumos processuais e ATA's) - 50 linhas
├── 📁 src/
│   ├── base.py (Onde está as funções que vão carregar as bases do drive/google sheets) - 55 linhas
│   ├── google_drive_utils.py (Todas as funções de conexao para o google drive e outras questoes como upload e leitura de arquivos no googledrive) - 306 linhas
│   ├── salvar_alteracoes.py (Funções de salvar as alterações feita nas base de dados diretamente no arquivo google sheet, como tmabém suas modificações) - 269 linhas
│   ├── salvar_historico.py (funcao de mapear as modificacoes dos processos em esquema de arvore e também salva em um google sheets de modificações) - 135 linhas
│   ├── editar_processo_geral.py (Toda lógica de edição de processos) - 464 linhas
│   └── 📁 coleta_de_dados/
│       ├── anp_etanol.py (Script de donwload de dados do etanol) - 28 linhas
│       ├── anp_preco_combustivel.py (Script para donwload de precos de combustivel) - 28 linhas
│       ├── anp_producao_combustivel.py (scirpt para donwload de dados de producao de combustiveis) - 35 linhas
│       ├── ibge_abate_animais.py (script para donwload de abates de animais) - 33 linhas
│       ├── ibge_leite_industrializado.py (script para download de leite industrializado) - 26 linhas
│       ├── mdic_comercio_exterior.py (script para donwload de dados da balnaça comercial, mercado exterior) - 64 linhas
│       ├── rgf.py (função para baixar dados do rgf) - 40 linhas
│       ├── sefaz_despesa_ano_corrente.py (script para baixar dados de despesas referente ao ano corrente) - 98 linhas
│       ├── sefaz_despesa_completo.py (script para donwload completo dos dados de desepsa) - 107 linhas
│       ├── sefaz_dotacao_ano_corrente.py (script para donwload de dotacao para o ano corrente) - 107 linhas
│       └── sefaz_dotacao_completo.py - 106 linhas
├── 📁 utils/
│   ├── 📁 auth/
│   │   └── auth.py (funções lógicas que vão gerenciar o login dos usuarios) - 132 linhas
│   ├── 📁 cadastrar_processos/
│   │   └── cadastro.py (Lógica de cadastros de processos que vai fornecer as funcoes para a página de cadastro) - 262 linhas
│   ├── 📁 confeccoes/
│   │   ├── confeccao_ata.py (fnção que montará a composição e o formato da ata do cpof) - 138 linhas
│   │   ├── formatar.py (Arquivo com diversas funções que formatam diversos tipos de coisas, desde números para o formato brasileiro, com cifrão, sem, arredondado, completo, graficos de barra, linha, area, pizza, analises, texto pré prontos, etc, o arquivo mais completo com cerca de 1000 linhas) - 935 linhas
│   │   ├── gerar_baixar_confeccao.py (Função que ira renderizar a confecção dos relatórios e ata's) - 155 linhas
│   │   ├── resumos.py (Função para construção dos resumos orçamentários e forms) - 340 linhas
│   │   ├── 📁 dashboards/
│   │   │   ├── mdic_bandeiras.py (uma função para mapear as bandeiras dos países) - 207 linhas
│   │   │   ├── mdic_comercio_exterior_dashboard.py (construção do dashboard de balança comercial) - 492 linhas
│   │   │   └── rgf_dashboard.py (construção do dashboard do RGF) - 109 linhas
│   │   └── 📁 relatorio/
│   │       ├── padronizacao_relatorio.py (conjunto de funções que vao desde a função que gera o pdf a partir do html pelo weasypdf e função que gera em docs) - 168 linhas
│   │       ├── relatorio_anp_etanol.py (arquivo que montará o conteúdo do relatório de etanol) - 299 linhas
│   │       ├── relatorio_anp_gn.py (arquivo que montará o conteúdo do relatório de gás natual) - 127 linhas
│   │       ├── relatorio_anp_lgn.py (arquivo que montará o conteúdo do relatório de liquido gás natural) - 130 linhas
│   │       ├── relatorio_anp_petroleo.py (arquivo que montará o conteúdo do relatório da produção de petroleo) - 134 linhas
│   │       ├── relatorio_anp_preco_combustivel.py (arquivo que montará o conteudo dos relatorios de preço de combustiveis) - 555 linhas
│   │       ├── relatorio_cpof.py (arquivo que montará o relatório do CPOF) - 372 linhas
│   │       ├── relatorio_ibge_abate_animais.py (arquivo que montará o relatório de abate de animais) - 226 linhas
│   │       ├── relatorio_ibge_leite_industrializado.py (arquivo que montará o relatório de leite industrial) - 237 linhas
│   │       ├── relatorio_mdic_comercio_exterior.py (arquivo que montará o relatorio da balança comercial, exportacoes e importacoes) - 289 linhas
│   │       └── relatorio_sefaz_despesa.py (arquivo que montará o relatório da de despesa dos orgãos) - 373 linhas
│   ├── 📁 filtros/
│   │   └── filtros.py (arquivos que definem os filtros de busca dos processos na página visualizar) - 131 linhas
│   ├── 📁 limite/
│   │   └── limite_credito.py (arquivo que faz o calculo e define os valores do limite orçamentario do ano vigente e o calculo do limite) - 26 linhas
│   ├── 📁 opcoes_coluna/
│   │   ├── contabilizar_limite.py (construção das opções de contabilizar no limite, sim ou não) - 1 linha
│   │   ├── deliberacao.py (definição das desliberações e de suas cores) - 2 linhas
│   │   ├── fonte_recurso.py (opções de fonte de recurso) - 1 linha
│   │   ├── grupo_despesa.py (opcoes de grupo de despesa) - 1 linha
│   │   ├── orgao_uo.py (definição dos orgãos) - 1 linha
│   │   ├── origem_recurso.py (definição das origens de recursos) - 1 linha
│   │   ├── situacao.py (definição das situações e de suas cores) - 2 linhas
│   │   ├── tipo_credito.py (definicao dos tipos de creditos) - 1 linha
│   │   ├── tipo_despesa.py (definicao dos tipos de despesa e de suas cores) - 2 linhas
│   │   └── 📁 validadores/
│   │       ├── data.py (valida as datas e verifica se está correto) - 37 linhas
│   │       ├── numero_ata.py (verifique se de fato é um número) - 10 linhas
│   │       ├── numero_decreto.py (formata e valida os números de decreto) - 30 linhas
│   │       ├── numero_processo.py (valida o número de processo) - 6 linhas
│   │       ├── objetivo.py (sanitiza o campo de objetivo) - 3 linhas
│   │       ├── observacao.py (sanitiza o campo de obhservação) - 3 linhas
│   │       ├── processo.py (unifica as validacoes e verifica de uma unica vez todos os campos) - 78 linhas
│   │       ├── validar_campos_livres.py (sanitiza os campos de livre digitação) - 17 linhas
│   │       └── valor.py (formata o valor e valida o valor) - 42 linhas
│   └── 📁 ui/
│       ├── dataframe.py (construção e personalização da tabela, todos seus parametros e funcionalidades) - 510 linhas
│       ├── display.py (toda a customização do display) - 268 linhas
│       └── icones.py (mapa de icones) - 1 linha
├── home.py (página inicial que contém os graficos do limite) - 250 linhas
├── packages.txt (pacotes necessários)
└── requirements.txt (bibliotecas necessárias)



📊 Resumo do Projeto
Total de linhas de código: 9.449 linhas

📈 Distribuição por módulos:
utils/confeccoes/: 2.565 linhas (27.1%)
src/: 1.229 linhas (13.0%)
pages/: 444 linhas (4.7%)
utils/ui/: 779 linhas (8.2%)
utils/opcoes_coluna/: 238 linhas (2.5%)
home.py: 250 linhas (2.6%)
Outros módulos: 3.944 linhas (41.9%)