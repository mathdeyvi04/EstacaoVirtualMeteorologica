"""
Descrição:
    Código responsável pelas funções de conexão com servidor.
"""

from Back_Classes import *


def extraindo_informacoes_de_clima():
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
        Dicionário das estações
        {
            (lat, lon): [A, B, C, ...]
        }
    """

    """Assim que isso iniciar, devemos mudar algo na tela para indicar que o travamento
    é devido à busca de novos dados."""

    sufixo_codigo, horario_da_ultima_atualizacao = obtendo_instante_mais_recente()

    # Devemos fazer a conexão do portal e a extração dos arquivos .nc
    portal_de_conexao = Servidor()

    if not portal_de_conexao.conexao_estabelecida:
        return None

    # LSTF -> Temperatura da Superfície
    #
    for variavel_de_clima in var_globais["vars_de_clima"]:
        resposta_do_servidor = portal_de_conexao.extrair(
            "ABI-L2-LSTF/2024/279"
        )

        # Sabendo não haver arquivo .nc no diretório local, podemos
        # baixar o arquivo.

        nome_do_arquivo_baixado = portal_de_conexao.baixando_arquivo(
            resposta_do_servidor,
            variavel_de_clima
        )

        # De posse do arquivo baixado.
        info_dados = DataSat(
            variavel_de_clima + ".nc"
        )

        dados_gerais_var_clima = info_dados.obtendo_dados_da_variavel_principal()

        matriz_de_pixels = info_dados.colhendo_pixels(
            dados_gerais_var_clima
        )

        # info_dados.auto_destruicao()



        # De posse dos pixels, devemos fazer o devido tratamento de seus valores.
    portal_de_conexao.fechando_portao()

    # return dicionario de estações

    return {}, horario_da_ultima_atualizacao

