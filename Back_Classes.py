"""
Descrição:
    Código responsável por gerenciar as classes que usaremos, são estas
    a representação do servidor e a representação do banco de dados.
"""
from Back_FuncoesBasicas import *


class Servidor:
    """
    Descrição:
        Classe responsável por representar nossa conexão com servidor.

    Parâmetros:
        Nenhum

    Retorno:
        Portal de Conexão com servidor do satélite.
    """

    def __init__(self):
        try:
            self.portal_de_conexao: S3Client = bt.client(
                "s3",
                config=Config(signature_version=UNSIGNED)
            )
            self.conexao_estabelecida = True
        except Exception as error:
            mb.showerror(
                "ERROR",
                f"Houve erro ao tentar conectar-se com servidor: {error}"
            )
            self.conexao_estabelecida = False

    def extrair(
            self,
            string_definidora: str
    ) -> dict:
        """
        Descrição:
            Método responsável por obter os dados de satélite mais recentes.

        Parâmetros:
            -> string_definidora:
                String para buscarmos conteúdos

        Retorno:
            Dicionário que representa os arquivos de dados.
        """

        while True:
            resposta = self.portal_de_conexao.list_objects_v2(
                Bucket=var_globais["bucket"],
                Prefix=string_definidora
            )

            if "Contents" not in resposta:
                string_definidora = consertando_sufixo(
                    string_definidora
                )
            else:
                break

        # Temos a garantia que há resposta
        return resposta["Contents"][-1]

    def baixando_arquivo(
            self,
            resposta: dict,
            variavel_de_clima: str
    ) -> str:
        """
        Descrição:
            Método responsável por baixar um arquivo.

        Parâmetros:
            -> resposta:
                informações do arquivo de dados mais recente
            -> variavel_de_clima:
                string representante do código de dados

        Retorno:
            Download do arquivo e retorno do nome do arquivo criado.
        """

        try:
            self.portal_de_conexao.download_file(
                var_globais["bucket"],
                resposta["Key"],
                variavel_de_clima + ".nc"
            )
        except FileExistsError:
            pass

        return variavel_de_clima + ".nc"

    def fechando_portao(
            self
    ) -> None:
        """Autoexplicativo"""

        self.portal_de_conexao.close()


class DataSat:
    """
    Descrição:
        Classe responsável por representar os dados de satélite.
    """

    def __init__(
            self,
            arquivo_de_dados: str
    ):
        self.dados = nc.Dataset(
            arquivo_de_dados
        ).variables

    def __str__(self):
        return str(self.dados)
