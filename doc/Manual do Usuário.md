# Sistema de Gestão Orçamentário e Financeiro  
*Atualizado em: 10/06/2025*

---

## 📖 Manual do Usuário

---

## 1. Tipos de Usuário

O Sistema de Gestão Orçamentário e Financeiro possui um sistema de login, onde cada usuário credenciado tem acesso a diferentes visualizações e funcionalidades, de acordo com seu nível hierárquico. As restrições de acesso abrangem desde a visualização de páginas até permissões sobre bases de dados e funcionalidades específicas.

*Níveis Hierárquicos:*

- *Usuário SUDO:* Acesso completo a tudo, inclusive ao que está em teste.
- *Usuário ADMIN:* Acesso completo a tudo que está pronto.
- *Usuário SOP:* Acesso restrito às condições destinadas ao SOP.
- *Usuário GEO:* Acesso restrito às condições destinadas à GEO.
- *Usuário CPOF:* Acesso restrito às condições destinadas ao CPOF.
- *Membro CPOF:* Acesso restrito às condições do membro do CPOF.
- *Usuário Externo:* Acesso restrito às condições de Externo.

*Conteúdo das páginas é ancorado em tópicos:*
- *Propósito:* Motivo pelo qual a página existe.
- *Funcionalidades:* Funções óbvias e ocultas.
- *Permissão da Página:* Quem pode visualizar.
- *Permissão de Conteúdo:* Quem acessa o quê.

---

## 2. Páginas do Sistema

O sistema possui *09 páginas principais*:

---

### 📂 Repositório de Dados

- *Propósito:* Guardar as bases de dados internas e externas do SIGOF.
- *Funcionalidades:* Campo de busca por nome ou TAG, filtragem de bases.
  - *Total de Bases:* 20
    - *Internas (12):* Dotação Orçamentária, Despesas Orçamentárias, Receitas Orçamentárias, RGF Completo, Dívida Sobre RCL, Dívida Líquida sobre RCL, Despesa com Pessoal/RCL, ITCMD, ICMS, IPVA, IRRF, IPI
    - *Externas (8):* Leite Industrializado, Abate de Animais, Comércio Exterior, Produção de Etanol, Gás Natural, Gás Liquefeito Natural, Petróleo, Preço de Combustíveis
- *Permissão da Página:* Todos os membros cadastrados e usuários externos.
- *Permissão de Conteúdo:*  
  - Usuários cadastrados: acesso a todas as bases.  
  - Usuários externos: acesso apenas às bases externas.

---

### 📝 Manifestação Técnica

- *Propósito:* Membros do CPOF visualizam e respondem processos com TAG específica.
- *Funcionalidades:*  
  - Botões para filtrar processos aguardando resposta ou já respondidos, com contadores.
  - Dataframe com campo "Insira seu parecer" para resposta via selectbox ou digitação manual.
  - Botão "Clique aqui para salvar" para registrar alterações.
  - Opções para desistência de resposta antes/depois de salvar, e para modificar ou remover pareceres.
- *Permissão da Página:* Membros do CPOF, SUDO e ADMIN.
- *Permissão de Conteúdo:*  
  - Cada membro responde apenas nos campos destinados ao seu login.

---

### 📊 Dashboards

- *Propósito:* Visualização de dashboards, painéis e gráficos internos e externos.
- *Funcionalidades:* Botões para alternar entre dashboards disponíveis:
  - Observatório do Orçamento
  - Mapa do Comércio Exterior
  - Dashboard - RGF
- *Permissão da Página:* Todos os usuários cadastrados e externos.
- *Permissão de Conteúdo:*  
  - Usuários cadastrados: acesso a todos os dashboards.  
  - Usuários externos: acesso apenas ao Mapa do Comércio Exterior.

---

### 📑 Relatórios

- *Propósito:* Visualização e download de relatórios produzidos pelo sistema.
- *Funcionalidades:* Caixa de seleção para escolher relatórios:
  - Relatório CPOF
  - Boletim Conjuntural Alagoano
  - Relatório de Despesa dos Órgãos
- *Permissão da Página:* Todos os usuários cadastrados e externos.
- *Permissão de Conteúdo:*  
  - Usuários cadastrados: acesso a todos os relatórios.  
  - Usuários externos: acesso apenas ao Boletim Conjuntural Alagoano.

---

### 🕑 Histórico

- *Propósito:* Visualização do histórico de modificações dos processos.
- *Funcionalidades:*  
  - Visualização hierárquica das alterações de cada processo.
- *Permissão da Página:* Todos os usuários cadastrados, exceto membros do CPOF.
- *Permissão de Conteúdo:*  
  - Cada usuário vê o histórico de sua respectiva base.

---

### 🔍 Visualizar Processo

- *Propósito:* Visualização e edição dos processos cadastrados.
- *Funcionalidades:*
  - *Visualização:* Filtros por deliberação/situação/status, palavra-chave, filtros na tabela, manutenção dos filtros ao navegar.
  - *Edição:*  
    - Modificação de deliberação/situação/status via duplo clique e selectbox.
    - Edição de outros campos via caixa de expansão e formulário.
    - Alerta: Não é possível editar deliberação/situação/status e outros campos simultaneamente.
  - *Geração de Resumos:*  
    - Gerador Automático de Resumos por base.
    - Geração de ATA dos processos respondidos, com opções para adicionar/remover/resetar membros.
- *Permissão da Página:* Todos os usuários cadastrados (usuários externos não têm acesso).
- *Permissão de Conteúdo:* Depende da base de acesso do usuário.

---

### ➕ Cadastrar Processos

- *Propósito:* Cadastro de novos processos recebidos.
- *Funcionalidades:*  
  - Campos obrigatórios para cadastro.
  - Alerta para processos já cadastrados, com opção de edição via página de visualização.
- *Permissão da Página:* Todos os usuários cadastrados, exceto membros do CPOF.
- *Permissão de Conteúdo:* Todo conteúdo permitido para quem tem acesso.

---

### 🏠 Home

- *Propósito:* Página inicial do sistema.
- *Permissão:* Todos têm acesso.

---

## ⚙ Funcionalidades Gerais

- O sistema atualiza todas as bases a cada cinco minutos.
- Sempre que um botão de "Salvar" é acionado, a base correspondente é atualizada.
- Após as 08h, o primeiro usuário a acessar a Home ativa o gatilho de envio automático de e-mails (uma vez ao dia).
- No repositório, ao baixar uma base, ela é atualizada antes do download (uma vez por mês), desde que o usuário esteja nas dependências da SEPLAG/intranet.
- Se o usuário estiver fora da SEPLAG/intranet, o download será do último arquivo atualizado.

---

## 📝 Observações Finais

- O sistema foi projetado para garantir segurança, rastreabilidade e facilidade de uso, respeitando as permissões de cada usuário.
- Em caso de dúvidas, consulte o suporte técnico ou o administrador do sistema.

---

*Desenvolvido por:*  
Lucas Falcão