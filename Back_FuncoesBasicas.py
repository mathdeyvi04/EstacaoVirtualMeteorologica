"""
Descrição:
    Código responsável por armazenar as funções mais simples, como
    de verificações ou manipulações.
"""
from Back_Variaveis_Importacoes import *


def obtendo_instante_mais_recente() -> tuple[str, str]:
    """
    Descrição:
        Função responsável por, usando o datetime, gerar uma string que representará
        o último instante das informações.

    Parâmetro:
        Nenhum

    Retorno:
        String no formato 2024/DIA_JUL/ULTIMA_HORA e instante da última atualização feita.
    """

    hoje = dt.now()

    ano = hoje.year
    hora_completa_instantanea = f"{hoje.hour}:{hoje.minute}:{hoje.second}"

    dia_juliano = hoje.timetuple().tm_yday

    string_codigo = f"/{ano}/{dia_juliano}/{hoje.hour}"

    return string_codigo, hora_completa_instantanea




