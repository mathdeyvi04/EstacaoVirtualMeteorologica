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

        Se não colocarmos a última hora, não precisamos nos preocupar com o problema
        de tentar uma hora muito prematura.

        Outras situações de contingência serão cuidadas em uma função específica.

    Parâmetro:
        Nenhum

    Retorno:
        String no formato 2024/DIA_JUL e instante da última atualização feita.
    """

    hoje_universal = dt.utcnow()
    hoje_brasil = dt.now()

    hora_completa_instantanea = f"{hoje_brasil.hour}:{hoje_brasil.minute}:{hoje_brasil.second}"

    dia_juliano = hoje_universal.timetuple().tm_yday
    ano = hoje_universal.year
    string_codigo = f"/{ano}/{dia_juliano}"

    return string_codigo, hora_completa_instantanea


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


def corretor_de_geocoordenadas(
        valor_real: float,
        se_eh_lat: bool
) -> float:
    """
    Descrição:
        Função responsável por corrigir as coordenadas de latitude e de longitude.
        Por algum motivo, apenas colocar os valores reais não estavam funcionando.
        Façamos uma interpolação usando os valores que obtemos empiricamente para
        a América do Sul. Consideremos (x, y) = (Verdadeiro, Falso)

        Pensando primeiro na latitude, temos os pontos: (-55, 71) e (11.5 , -20)
        A partir dos quais, Falso = -1.36842 * (Verdadeiro) - 4.26316

        Agora para longitude, temos: (-81.2, -81.2) e (-34.8, -16.8)
        A partir dos quais, False = 1.38793 * (Verdadeiro) + 31.5

        Entretanto, esses valores ainda apresentam uma margem de erro significativa.
        Talvez um estudo futuro seja necessário para garantirmos uma maior precisão.

    Parâmetros:
        -> valor_real:
            Valor Real da Geocordenada
        -> se_eh_lat:
            Booleano indicando se o número se trata da latitude ou longetude.

    Retorno:
        Valor da geocoordenada corrigido para o sistema.
        """

    a, b = (- 1.36842, - 4.26316) if se_eh_lat else (1.38793, 31.5)

    return a * valor_real + b
