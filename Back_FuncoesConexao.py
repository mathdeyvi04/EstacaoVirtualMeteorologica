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
            (TUPLA_DE_POSICAO_NA_INTERFACE): [A, B, C, ...]
        }
    """

    """Assim que isso iniciar, devemos mudar algo na tela para indicar que o travamento
    é devido à busca de novos dados."""

    sufixo_codigo, horario_da_ultima_atualizacao = obtendo_instante_mais_recente()

    # Devemos fazer a conexão do portal e a extração dos arquivos .nc
    portal_de_conexao = Servidor()

    if not portal_de_conexao.conexao_estabelecida:
        return None

    estacoes_a_serem_colocadas = {
        # (LOCAL_NO_INTERFACE) = [VALORES]
        (230, 360): [],  # 1
        (410, 350): [],  # 2
        (270, 450): [],  # 3
        (360, 220): [],  # 4
    }
    # LSTF -> Temperatura da Superfície
    # ACHAF -> Altura do Topo da Nuvem
    for variavel_de_clima in var_globais["vars_de_clima"]:
        resposta_do_servidor = portal_de_conexao.extrair(
            variavel_de_clima + sufixo_codigo
        )

        # Sabendo não haver arquivo .nc no diretório local, podemos
        # baixar o arquivo. Caso haja, não baixará de novo.
        nome_do_arquivo_baixado = portal_de_conexao.baixando_arquivo(
            resposta_do_servidor,
            variavel_de_clima
        )

        # De posse do arquivo baixado.
        info_dados = DataSat(
            variavel_de_clima + ".nc"
        )

        dados_gerais_var_clima = info_dados.obtendo_dados_da_variavel_principal()

        pixels_de_cada_estacao = info_dados.colhendo_pixels(
            dados_gerais_var_clima
        )

        # Esses pixels já estão ordenados com suas respestivas estações
        for estacao, valor_do_pixel in zip(
                estacoes_a_serem_colocadas,
                pixels_de_cada_estacao
        ):
            estacoes_a_serem_colocadas[
                estacao
            ].append(
                valor_do_pixel
            )

        info_dados.auto_destruicao()
        # print(f"Leitura Concluída e Destruição do Arquivo {nome_do_arquivo_baixado} realizada.\n")

    # print(estacoes_a_serem_colocadas)
    portal_de_conexao.fechando_portao()

    # return dicionario de estações

    return estacoes_a_serem_colocadas, horario_da_ultima_atualizacao
