opcoes_deliberacao = [
    "Aprovado",
    "Aprovado com condicionante",
    "Aprovado parcial",
    "Devolvido",
    "Diligência",
    "Indeferido",
    "Intempestivo",
    "Material de consumo",
    "Segurar",
    "Vencido",
    "Disponível aos Membros CPOF",
    "Disponível para a próxima Reunião do CPOF",
]

mapa_cores_deliberacao = {
    # Status de aprovação (tons de verde)
    "Aprovado": "#90EE90",  # Verde claro
    "Aprovado com condicionante": "#66CDAA",  # Verde médio (verde água)
    "Aprovado parcial": "#32CD32",  # Verde lima
    
    # Situações que exigem retorno ou complementação (tons de laranja)
    "Devolvido": "#FFA07A",  # Salmão claro
    "Diligência": "#FF8C00",  # Laranja escuro
    "Disponível aos Membros CPOF": "#FFA500",  # Laranja
    "Disponível para a próxima Reunião do CPOF": "#FFD700",  # Ouro
    
    # Situações negativas (tons de vermelho/roxo escuro)
    "Indeferido": "#DC143C",  # Carmesim
    "Intempestivo": "#8B0000",  # Vermelho escuro
    "Segurar": "#800080",  # Roxo
    
    # Situações neutras ou administrativas (tons de cinza)
    "Material de consumo": "#A9A9A9",  # Cinza escuro
    "Vencido": "#696969",  # Cinza chumbo
}