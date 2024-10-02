"""
Descrição:
    Código responsável por lidar com as verificações de existência e
    forçar a execução de toda a linha de arquivos.
    Sendo, portanto, o de menor hierárquia.
"""
from FrontEndCompleto import *


def precursor() -> None:
    """
    Descrição:
        Função responsável por dar início à execução da aplicação.

    Parâmetros:
        Nenhum.

    Retorno:
        Verificações de Existência e posterior execução da aplicação.
    """

    # Verificações de existência de arquivos e pastas
    for pasta_de_dados in diretorios:
        if not isdir(
                diretorios[pasta_de_dados]
        ):
            # Quer dizer que o caminho da pasta não existe.
            # Devemos criá-lo então.
            mkdir(
                diretorios["Banco Geral"]
            )
            mb.showinfo(
                "Criação",
                f"Não havia a pasta chamada {pasta_de_dados}, por isso a criei."
            )

    for arquivo in caminhos:
        if not isfile(
                caminhos[arquivo]
        ):
            if arquivo.startswith("Petro"):
                mb.showerror(
                    "ERROR",
                    "Não há uma imagem de petrópolis dentro do diretório local."
                )

    # Com todas as verificações feitas, podemos dar início
    interface_principal()


if __name__ == '__main__':
    precursor()
