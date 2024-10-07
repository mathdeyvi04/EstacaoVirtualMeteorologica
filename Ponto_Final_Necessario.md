## Ponto Final Necessário para Desenvolvimento da UI

Ao final da lógica de fatiamento da imagem geral, 
as seguintes reflexões são necessárias:

### O que pode ser feito?

A partir de uma quantidade X de pixels, pode-se separar em
quadrantes e trabalhar com a média dessas submatrizes. Com 
o resultado centralizado das submatrizes, temos uma Estação.

### Produto Final

É interessante que o recurso final obtido seja:

````python
entidades_de_estacoes = {
    # Chave as posições de cada estação no mapa
    # Em geocoordenadas
    (lat, lon): [
        # Variáveis de Clima em correspondência
        # com a ordem da variável global var_globais['vars_de_clima']
        A,
        B,
        C
    ]
}
````

A partir disso, o desenvolvimento da UI segue.




