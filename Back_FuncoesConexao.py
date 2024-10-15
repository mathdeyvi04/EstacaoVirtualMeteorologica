"""
Descrição:
    Código responsável pelas funções de conexão com servidor.
"""

from Back_Classes import *


def extraindo_informacoes_de_clima() -> tuple[dict, dt] | None:
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
        Dicionário que representará as estações.
        {
            (lat, lon): [A, B, C, ...]
        }
        E o horário que ocorreu esta ultima busca.
    """

    """Assim que isso iniciar, devemos mudar algo na tela para indicar que o travamento
    é devido à busca de novos dados."""

    sufixo_codigo, horario_e_data_atualizacao = obtendo_instante_mais_recente()

    # Devemos fazer a conexão do portal e a extração dos arquivos .nc
    portal_de_conexao = Servidor()

    if not portal_de_conexao.conexao_estabelecida:
        return None

    """
    LOOP DAS VARIÁVEIS DE CLIMA ENTRANDO EM CADA ESTAÇÃO.
    """

    portal_de_conexao.fechando_portao()

    return {}, horario_e_data_atualizacao



