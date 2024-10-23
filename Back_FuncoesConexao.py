"""
Descrição:
    Código responsável pelas funções de conexão com servidor.
"""

from Back_Classes import *


def extraindo_informacoes_de_clima() -> dict | None:
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

    for codigo_de_variavel_de_clima in var_globais[
        "vars_de_clima"
    ]:
        resposta_do_servidor = portal_de_conexao.extrair(
            "ABI-L2-LSTF/2024/270"
        )

        nome_do_arquivo_temporario_criado = portal_de_conexao.baixando_arquivo(
            resposta_do_servidor,
            codigo_de_variavel_de_clima
        )

        conj_de_dados = DataSat(
            nome_do_arquivo_temporario_criado
        )

        conj_de_dados.colhendo_pixels(
            conj_de_dados.obtendo_dados_da_variavel_principal()
        )

        # Para não entupir de arquivos
        # conj_de_dados.auto_destruicao()

    for variavel_de_clima in var_globais["vars_de_clima"]:
        resposta_do_servidor = portal_de_conexao.extrair(
            variavel_de_clima + sufixo_codigo
        )

        # Sabendo não haver arquivo .nc no diretório local, podemos
        # baixar o arquivo.

        """nome_do_arquivo_baixado = portal_de_conexao.baixando_arquivo(
            resposta_do_servidor,
            variavel_de_clima
        )"""

        # De posse do arquivo baixado.
        info_dados = DataSat(
            variavel_de_clima + ".nc"
        )

        dados_gerais_var_clima = info_dados.obtendo_dados_da_variavel_principal()

        matriz_de_pixels = info_dados.colhendo_pixels(
            dados_gerais_var_clima
        )

        # De posse dos pixels, devemos fazer o devido tratamento de seus valores.
        print(matriz_de_pixels)
        print(len(matriz_de_pixels))
        print(len(matriz_de_pixels[0]))
    portal_de_conexao.fechando_portao()

    # return dicionario de estações

    return {}, horario_e_data_atualizacao

