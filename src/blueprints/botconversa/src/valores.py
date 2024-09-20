# Definindo as categorias e os valores padrões para cada relação
categorias = ["Centro", "Normal", "Especial", "Extremidade"]
valores_padrao = {
    ("Centro", "Centro"): 10,
    ("Centro", "Normal"): 14,
    ("Centro", "Especial"): 15,
    ("Centro", "Extremidade"): 17,
    ("Normal", "Normal"): 16,
    ("Normal", "Centro"): 14,
    ("Normal", "Especial"): 17,
    ("Normal", "Extremidade"): 19,
    ("Especial", "Especial"): 20,
    ("Especial", "Centro"): 15,
    ("Especial", "Normal"): 17,
    ("Especial", "Extremidade"): 22,
    ("Extremidade", "Extremidade"): 25,
    ("Extremidade", "Centro"): 17,
    ("Extremidade", "Normal"): 19,
    ("Extremidade", "Especial"): 22
}

# Gerando e exibindo todas as relações com seus valores
for relacao, valor in valores_padrao.items():
    print(f"{relacao[0]} -> {relacao[1]}: R${valor:.2f}")
