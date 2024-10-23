"""
Descrição:
    Código responsável por armazenar as funções mais simples, como
    de verificações ou manipulações.
"""
from Back_Variaveis_Importacoes import *


def obtendo_instante_mais_recente() -> tuple[str, dt]:
    """
    Descrição:
        Função responsável por, usando o datetime, gerar uma string que representará
        o último instante das informações.

        Se não colocarmos a última hora, não precisamos nos preocupar com o problema
        de tentar uma hora muito prematura.

        Outras situações de contingência serão cuidadas em uma função específica.

    Parâmetro:
        Nenhum

    Retorno:
        String no formato 2024/DIA_JUL e instante da última atualização feita.
    """

    hoje_universal = dt.utcnow()

    dia_juliano = hoje_universal.timetuple().tm_yday
    ano = hoje_universal.year
    string_codigo = f"/{ano}/{dia_juliano}"

    return string_codigo, dt.now()


def consertando_sufixo(
        string_definidora: str
) -> str:
    """
    Descrição:
        Função responsável por consertar o sufixo da string definidora
        quando não for possível obter arquivos de dados para o momento.

    Parâmetros:
        Autoexplicativo

    Retorno:
        String_definidora correta.
    """

    codigo, ano, dia_jul = string_definidora.split("/")

    if int(dia_jul) == 1:
        # Então devemos retornar um ano.
        ano = str(
            int(ano) - 1
        )

        # E o dia para 365, ou 366 para bissextos
        dia_jul = str(
            365 if ano % 4 else 366
        )

    else:
        # Geralmente será isso
        dia_jul = str(
            int(dia_jul) - 1
        )

    return "/".join(
        [
            codigo,
            ano,
            dia_jul
        ]
    )

