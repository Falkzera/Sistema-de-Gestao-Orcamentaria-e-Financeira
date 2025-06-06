opcoes_situacao_ted = sorted([
    "Análise - SOP",
    "BLOCO 434066 - SEPLAG - Demais Orgãos",
    "Na Unidade",
    "Em vigência",
    "Aguardando Publicação",
    "CONCLUIDO",
])

mapa_cores_situacao_ted = {
    # Análises em andamento (tons de amarelo/laranja)
    "Análise - SOP": "#FFD700",  # Amarelo ouro
    
    # Blocos (tons de roxo/roxo-azulado)
    "BLOCO 434066 - SEPLAG - Demais Orgãos": "#A2A1D2",  # Azul lavanda

    # Fluxo de publicação (tons de verde-azulado)
    "Aguardando Publicação": "#48D1CC",  # Turquesa médio

    # Status neutros (tons de cinza)
    "Na Unidade": "#BC9A9A",  # Cinza claro
    
    # Para os Processos de TED (Em vigência) # red
    "Em vigência": "#b81414",  # Vermelho
    "CONCLUIDO": "#23a713"
    
}