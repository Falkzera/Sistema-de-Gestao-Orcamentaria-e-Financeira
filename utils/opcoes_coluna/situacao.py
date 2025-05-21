# utils/buscadores/origem_recursos.py

opcoes_situacao = [
    "Análise - SOP",
    "Análise - SEFAZ",
    "Não Reconhecido - SEFAZ",
    "Reconhecido - SEFAZ",
    "Análise - CPOF",
    "Aprovado - CPOF",
    "BLOCO 434075 - SEPLAG - Despachos e Decretos",
    "BLOCO 434078 - SEFAZ - Despachos e Decretos",
    "BLOCO 434066 - SEPLAG - Demais Orgãos",
    "BLOCO 434050 - SOP - Superintendente",
    "Aguardando Envio",
    "Aguardando publicação",
    "Publicado",
    "Em produção - Decreto",
    "Em produção - Despacho",
    "Na Unidade",
    "Processo Encerrado",
    "Publicado - Poderes",
    "Publicado - Especial",
    "Atendido - Decreto Folha",
    "Aguardando correção da unidade",
    "Análise - SUPLAN/SEPLAG",
    "Minuta de decreto confeccionada"
]


mapa_cores_situacao = {
    # Análises em andamento (tons de amarelo/laranja)
    "Análise - SOP": "#FFD700",  # Amarelo ouro
    "Análise - SEFAZ": "#FFA500",  # Laranja
    "Análise - CPOF": "#FFC04D",  # Amarelo claro
    "Análise - SUPLAN/SEPLAG": "#FFB347",  # Laranja claro
    
    # Reconhecimento SEFAZ (tons de azul)
    "Não Reconhecido - SEFAZ": "#ADD8E6",  # Azul claro (neutro)
    "Reconhecido - SEFAZ": "#4682B4",  # Azul aço
    
    # Status de aprovação (tons de verde)
    "Aprovado - CPOF": "#90EE90",  # Verde claro
    "Minuta de decreto confeccionada": "#77DD77",  # Verde médio
    
    # Blocos (tons de roxo/roxo-azulado)
    "BLOCO 434075 - SEPLAG - Despachos e Decretos": "#C9A0DC",  # Lavanda
    "BLOCO 434078 - SEFAZ - Despachos e Decretos": "#B19CD9",  # Lilás claro
    "BLOCO 434066 - SEPLAG - Demais Orgãos": "#A2A1D2",  # Azul lavanda
    "BLOCO 434050 - SOP - Superintendente": "#9B59B6",  # Roxo médio
    
    # Fluxo de publicação (tons de verde-azulado)
    "Aguardando Envio": "#AFEEEE",  # Turquesa claro
    "Aguardando publicação": "#48D1CC",  # Turquesa médio
    "Publicado": "#20B2AA",  # Verde-azulado
    "Publicado - Poderes": "#008080",  # Teal
    "Publicado - Especial": "#5F9EA0",  # Azul-cadete
    
    # Produção (tons de marrom/terra)
    "Em produção - Decreto": "#D2B48C",  # Tan
    "Em produção - Despacho": "#CD853F",  # Peru
    
    # Status neutros (tons de cinza)
    "Na Unidade": "#D3D3D3",  # Cinza claro
    "Aguardando correção da unidade": "#C0C0C0",  # Prata
    
    # Situações finais (tons de verde escuro)
    "Processo Encerrado": "#2E8B57",  # Verde mar
    "Atendido - Decreto Folha": "#3CB371",  # Verde médio

    # Para os Processos de TED (Em vigência) # red
    "Em vigência": "#b81414",  # 
    "Na unidade": "#D3D3D3",  # Cinza claro
    "CONCLUIDO": "#23a713"
    
}