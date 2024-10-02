### Documentação de Cada Função

Cada função deve ter seus parâmetros bem detalhados
e tipados da forma mais autoexplicativa possível.
Além de sua própria documentação.

```python
def saindo_da_ala(
        itens_a_serem_verificados_antes_da_saida: list[str],
        objetivos_a_serem_alcancados_fora_da_ala: list[str]
) -> bool:
    """
    Descrição:
        Função responsável por...
        --- Explicação sucinta do que a função faz---
    
    Parâmetros:
        Autoexplicativos.
        --- Caso não seja tão trivial assim a compreensão, 
        deve haver uma explicação ---
        
    Retorno:
        Booleano que indicará se a saída está permitida ou não.
    """
   ```


### Criação de Novos Arquivos de Código

Neles também deverão haver:

```python
"""
Descrição:
    Código responsável por...
    --- Explicação sobre o que deve ter naquele código
"""
   ```

### Sugestões

Tenha em mente que outras pessoas lerão seus códigos então
seja sempre claro.