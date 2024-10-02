"""
Descrição:
    Código responsável pelas funções de conexão com servidor.
"""

from Back_Classes import *


def extraindo_informacoes_de_clima() -> list[dict]:
    """
    Descrição:
        Função responsável por varrer as variáveis de clima
        e buscar suas informacoes.

        Em teoria, vamos baixar as informações mais recentes,
        em seguida, extrair as informações e logo depois destruir
        os arquivos.

        Podemos reconsiderar essa última parte.

    Parâmetros:
        Nenhum

    Retorno:
        Lista de Dicionários os quais representarão as informações de
        cada estação.
    """

    sufixo_codigo, horario_da_ultima_atualizacao = obtendo_instante_mais_recente()


    # Devemos fazer a conexão do portal e a extração dos arquivos .nc




