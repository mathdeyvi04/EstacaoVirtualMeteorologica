# Importações de Interface
from tkinter import messagebox as mb
import customtkinter as ctk
from tkinter.ttk import Treeview, Style
from tkinter import Canvas

# Importações de Servidor
from mypy_boto3_s3 import S3Client
import boto3 as bt
from botocore import UNSIGNED
from botocore.client import Config

# Importações de Sistema
from os.path import isdir, isfile
from os import mkdir, remove, listdir
from datetime import datetime as dt
from datetime import timedelta, time

# Importações de Manipulação de Dados
import netCDF4 as nc
from numpy.ma.core import MaskedArray
import numpy as np
import pandas as pd
from xarray import open_dataset

# Importações de Visualização de Dados
from PIL import Image, ImageTk
from matplotlib import pyplot as pp
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import cartopy.crs as ccrs
from cartopy.io import shapereader
from shapely.geometry import box

# -------------------------------------------------------------------------

diretorios = {
    # Indicador de Onde Nosso Banco de Dados Geral Ficará
    # Em teoria, ele armazenará os dados obtidos pelas Estações
    "Banco Geral": "./Banco Geral",
}

caminhos = {
    "Petropolis": "./petropolis.png",
    "Imagem_da_Estacao": "./img_estacao.png"
}

# Variáveis Concorrentes
var_globais = {
    # Variáveis Necessárias Para Obtenção de Dados
    "bucket": "noaa-goes16",
    "vars_de_clima": [
        "ABI-L2-LSTF",  # Temperatura na Superficie
        "ABI-L2-TPWF",  # Agua Precipitavel
        "ABI-L2-ACHAF",  # Altura do Topo da Nuvem
        "ABI-L2-ACHTF",  # Temperatura do Topo da Nuvem
    ],
    "var_nomes": [
        "Temperatura(°C)",
        "AguaPrecipitavel(mm)",
        "AlturaNuvem(m)",
        "TemperaturaNuvem(°C)"
    ],

    # Variáveis Necessárias Para Periodicidade de Funções
    "periodo_de_criacao_da_estacao": 60 * 10,  # EM SEGUNDOS
    "momentos_desejados_de_salvamento": [
        # Strings em Formato de Horário "H:M:S"
        # Precisa estar em sequência crescente
        "8:00:00",
        "12:00:00",
        "16:00:00",
        "20:00:00",
        "00:00:00"
    ],
    "margem_temporal_de_salvamento": timedelta(
        # Você pode colocar o valor que quiser, mas cuidade
        minutes=30
    ),

    "ultimo_momento_salvo_na_planilha": [None, None, None, None]
}


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
            print(f"Buscando: {string_definidora}")
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

        string_final_do_arquivo = variavel_de_clima + ".nc"

        if string_final_do_arquivo not in listdir():
            self.portal_de_conexao.download_file(
                var_globais["bucket"],
                resposta["Key"],
                string_final_do_arquivo
            )

        return string_final_do_arquivo

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
        """
        Descrição:
            Método responsável por dar início ao banco de dados do satélite.
        """
        self.arq_geral = nc.Dataset(
            arquivo_de_dados
        )

        self.dados = self.arq_geral.variables

        self.nome_do_arquivo_base = arquivo_de_dados

        self.nome_da_variavel_de_clima = arquivo_de_dados.replace(".nc", "").split("-")[-1]

        # Necessário, pois dentro do arquivo de dados ainda
        # não aparece como temos
        relacao_chave_valor = {
            # Qual o nome do atributo que contém a variável desejada.
            "LSTF": "LST",
            "ACHAF": "HT",
            "CMIPF": "CMI",
            "ACHTF": "TEMP",
            "TPWF": "TPW"
        }
        try:
            self.abreviacao_do_nome_da_variavel = relacao_chave_valor[
                self.nome_da_variavel_de_clima
            ]
        except KeyError:
            print("As disponiveis chaves são: ")
            pprint(self.dados.keys())

    def __str__(self):
        return str(self.dados)

    def obtendo_dados_da_variavel_principal(self) -> nc.Variable:
        """
        Descrição:
            Método responsável por obter as informações gerais da variável de clima
            do arquivo de dados aberto.

        Parâmetros:
            Nenhum

        Retorno:
            Informações gerais da variável de clima.
        """

        return self.dados[
            self.abreviacao_do_nome_da_variavel
        ]

    def colhendo_pixels(
            self,
            dados_da_var: nc.Variable
    ) -> list[float] | list[str]:
        """
        Descrição:
            Função responsável por, a partir da matriz imagem completa,
            selecionar quais são os pixels relativos.

        Parâmetros:
            -> dados_da_var:
                Resultado do método obtendo_dados_da_variavel_de_clima

        Retorno:
            Lista dos valores de cada pixel.
        """

        if not isinstance(
                dados_da_var,
                nc.Variable
        ):
            raise TypeError

        def visualizando_mapa_de_pixels() -> None:
            """
            Descrição:
                Função responsável por, caso seja o desejo do dev,
                apresentar um mapa contendo os limites de estados e municipios
                da imagem do GOES-16.

                Mais a frente dentro da função, existem os parâmetros responsáveis por
                manter o quadrado de petrópolis. O qual pode ser alterado. Atente-se à
                tendência de cada valor.

            Parâmetros:
                -> conjunto_de_arquivos_do_ibge:
                    Para se possa ter os limites dos municipios, faz-se necessário o
                    download externo de um conjunto de arquivos encontrados no site do ibge.
                    Basta pesquisar por shape.
                    São necessários os 4 arquivos do .zip.

            Retorno:
                Imagem plotada de uma determinada região, a princípio petrópolis.
                Pode demorar bastante, caso se deseje ver os limites de estado e,
                principalmente, os limites de municipios.
            """
            # Petrópolis
            lon_min = -43.4  # Min Lon  --> Fugindo de Grewitch
            lon_max = -42.95  # Max Lon  --> Indo para Grewitch
            lat_min = -22.6  # Min Lat  --> Descendo para Polo Sul
            lat_max = -22.16  # Max Lat  --> Subindo para Polo Norte

            abrindo_arq_bizuradamente = open_dataset(self.nome_do_arquivo_base)

            # Pegando as informações necessárias usando a biblioteca metpy.
            # Caso não tenha, instale.
            dat = abrindo_arq_bizuradamente.metpy.parse_cf(
                self.abreviacao_do_nome_da_variavel
            )

            # Criando o sistema referência, o global.
            geos = dat.metpy.cartopy_crs

            # Delimitando alguns eixos
            x = dat.x
            y = dat.y

            fig = pp.figure(figsize=(10, 6))

            # Finalmente, a projeção que permitiu tudo isso
            projecao = ccrs.PlateCarree()

            ax = fig.add_subplot(1, 1, 1, projection=projecao)
            ax.set_extent(
                # Aqui colocamos as limitações no mapa geral
                [
                    lon_min,
                    lon_max,
                    lat_min,
                    lat_max
                ],
                crs=projecao
            )

            # Visualizar a imagem na projeção retangular
            ax.imshow(
                dados_da_var[:],
                origin='upper',
                extent=(
                    x.min(), x.max(), y.min(), y.max()
                ),
                transform=geos,
                interpolation='none'
            )
            """
            Super Algoritmo para achar pixel de valor determinado
            """

            def adicionando_estados() -> None:
                """
                Descrição:
                    Função responsável por delimitar os estados.
                    Sem muitas dificuldades.

                Parâmetros:
                    Nenhum

                Retorno:
                    Delimitação dos estados
                """
                # Adiciona linhas costeiras
                ax.coastlines(
                    resolution='110m',
                    color='black',
                    linewidth=0.5
                )
                ax.add_feature(
                    # É isso que permite os estados aparecerem
                    ccrs.cartopy.feature.STATES,
                    linewidth=0.5
                )

            adicionando_estados()

            def adicionando_municipios() -> None:
                """
                Descrição:
                    Função responsável por colocar os municipios
                    dentro da imagem que temos.
                    Lembre-se que quanto maior a imagem, maior
                    será o tempo de verificações e de inserções.

                Parâmetros:
                    -> Conjunto dos quatros arquivos shapefile do Brasil.

                Retorno:
                    Delimitação dos municipios na região.
                """
                # Deve ter os 4 arquivo de shape baixados no site do IBGE
                leitor_de_cidades = shapereader.Reader(
                    "BR_Municipios_2022.shp"
                )
                caixa_limitadora = box(
                    lon_min,
                    lat_min,
                    lon_max,
                    lat_max
                )
                for cidade in leitor_de_cidades.geometries():
                    if cidade.intersects(caixa_limitadora):
                        ax.add_geometries(
                            [cidade],
                            crs=projecao,
                            edgecolor='gray',
                            facecolor='none',
                            linewidth=5
                        )

            # adicionando_municipios()

            # Título
            pp.title('GOES-16 Rio de Janeiro', loc='left', fontweight='bold', fontsize=15)
            pp.show()

            abrindo_arq_bizuradamente.close()

        # visualizando_mapa_de_pixels()

        # A partir de muito sanha envolvido, finalmente
        # conseguimos MAPEAR OS PIXELS DE PETRÓPOLIS.
        matriz_imagem = dados_da_var[:].tolist()

        """
        Aparentemente, cada variável tem formas diferentes de pixel.
        Nos resta sanha do mais puro valor.
        """

        match self.abreviacao_do_nome_da_variavel:

            case "LST":
                valores = [
                    matriz_imagem[775][840],
                    matriz_imagem[775][841],
                    matriz_imagem[776][840],
                    matriz_imagem[774][841],
                ]

                return [
                    float(valor) - 273.15 if valor is not None else "S/T" for valor in valores
                ]

            case "HT":
                valores = [
                    matriz_imagem[775][840],
                    matriz_imagem[775][841],
                    matriz_imagem[776][840],
                    matriz_imagem[774][841],
                ]

                return [
                    float(valor) if valor is not None else "S/N" for valor in valores
                ]

            case "TEMP":
                # TEMPERATURA DAS NUVENS
                # resolução diferente

                try:
                    valores = [
                        matriz_imagem[775][840],
                        matriz_imagem[775][841],
                        matriz_imagem[776][840],
                        matriz_imagem[774][841],
                    ]

                    return [
                        float(valor) - 273.15 if valor is not None else "S/T" for valor in valores
                    ]

                except:
                    return ["S/N"] * 4

            case "TPW":
                # AGUA PRECIPITAVEL
                valores = [
                    matriz_imagem[775][840],
                    matriz_imagem[775][841],
                    matriz_imagem[776][840],
                    matriz_imagem[774][841],
                ]

                return [
                    float(valor) if valor is not None else "S/N" for valor in valores
                ]

            case _:
                # O sanha venceu e o lima perdeu.
                return [-1, -1, -1, -1]

    def auto_destruicao(
            self
    ) -> None:
        """
        Descrição:
            Método responsável por fechar o arquivo corretamente
            e destruí-lo.
        """

        self.arq_geral.close()
        remove(
            self.nome_do_arquivo_base
        )


class Estacao:
    """
    Descrição:
        Classe responsável por representar uma estação virtual.
        Possuindo diversas funcionalidades e, por isso, tornou-se
        necessário essa classe mais específica.
    """

    def __init__(
            self,
            janela: ctk.CTk,
            posicao_da_estacao: tuple[float, float],
            lista_de_variaveis_de_clima: list[float],
            instante: dt,
            numero: int
    ):
        """
        Descrição:
            Método responsável por criar nossa estação

        Parâmetros:
            -> janela:
                Autoexplicativo

            -> posicao_da_estacao:
                Em teoria, devemos receber uma tupla de valores em latitude e longitude.
                Baseado nisso, uma transformação deve ser feita para colocarmos a estação
                em um ponto da interface que equivale ao correspondente no mapa!

            -> lista_de_variaveis_de_clima:
                Lista de valores numéricos correspondentes em ordem às variáveis de clima.

            -> numero:
                Apenas um indicador de qual estação estamos tratando
        """

        self.mestre = janela

        # Essencialmente, será um botão.
        self.entidade = ctk.CTkButton(
            self.mestre,

            image=ctk.CTkImage(
                Image.open(
                    'img_estacao.png'
                ),
                size=(30, 30)
            ),
            text="",

            fg_color="#0D251B",
            bg_color="#0D251B",
            hover_color="#55543F",
            width=30,

        )
        # E posicionamos ele na coordenada correta.
        # Aqui, apenas para exemplo
        self.posicao_na_janela = posicao_da_estacao
        self.entidade.place(
            x=self.posicao_na_janela[0],
            y=self.posicao_na_janela[1]
        )

        # Atributos Necessários
        self.valores = lista_de_variaveis_de_clima
        self.se_ja_foi_clicado = False
        self.id = numero
        self.horario_e_data = instante
        self.caminho_a_ser_buscado = diretorios[
                                         "Banco Geral"
                                     ] + f"/Estacao{self.id}/historico{instante.year}.xlsx"

        self.frame_apresentador = None

        # Funções Inerentes
        self.entidade.configure(
            command=self.clicado
        )
        self.atualizar_historico()

    def clicado(self):
        """
        Descrição:
            Método responsável por, quando o botão for clicado, uma janelinha
            surgir e apresentar valores específicos.

            Há a opção do usuário clicar novamente nela e fechar o frame.

        Parâmetros:
            Nenhum

        Retorno:
            Apresentação das variáveis de clima da estação.
        """

        if self.se_ja_foi_clicado:
            # Então devemos retirar o frame.

            # Então com certeza temos um frame
            self.frame_apresentador.destroy()
            self.frame_apresentador = None

            self.se_ja_foi_clicado = False
            return None
        else:
            self.se_ja_foi_clicado = True

        # Ao lado do botão, devemos criar uma espécie de frame
        X = self.posicao_na_janela[0] + 50
        Y = self.posicao_na_janela[1]
        W = 200
        frame_apresentador = ctk.CTkFrame(
            self.mestre,
            fg_color="#FFFFFF",
            bg_color="#FFFFFF",
            width=W,
            height=155,
        )
        self.frame_apresentador = frame_apresentador
        frame_apresentador.place(
            x=X,
            y=Y
        )

        colunas = [f"Medidas(E{self.id})", "Valor"]
        tv = Treeview(
            frame_apresentador,
            columns=colunas,
            show="headings"
        )

        tams = [
            188,
            50
        ]

        a = 10
        est = Style()
        est.configure("Treeview", font=('Verdana', a, 'bold'))
        est.configure("Treeview.Heading", font=('Verdana', a, 'bold'))

        for col, TAM in zip(colunas, tams):
            tv.heading(
                col,
                text=col,
                anchor="center"
            )
            tv.column(
                col,
                width=TAM,
                anchor="center"
            )

        i = 0
        for conj in zip(
                self.valores,
                var_globais["var_nomes"]
        ):
            tv.insert("", "end", values=conj[::-1])
            i += 1

        tv.place(
            x=5,
            y=5,
            height=120
        )

        # Devemos criar um botão capaz de destruí-lo.
        se_ja_existe_janela = ctk.BooleanVar(frame_apresentador)
        se_ja_existe_janela.set(False)
        ctk.CTkButton(
            frame_apresentador,
            text="Histórico",
            text_color="#000000",
            fg_color='#fafafa',
            border_width=2,
            border_color="#000000",
            font=("Verdana", 10, 'bold'),

            width=191,
            height=20,
            hover_color='#ccb4b4',

            command=lambda: self.historico(se_ja_existe_janela)
        ).place(
            x=5,
            y=105,
        )

        ctk.CTkButton(
            frame_apresentador,
            text="Fechar",
            text_color="#000000",
            fg_color='#fafafa',
            border_width=2,
            border_color="#000000",
            font=("Verdana", 10, 'bold'),

            width=191,
            height=20,
            hover_color='#ccb4b4',

            command=lambda: self.destruir(frame_apresentador)
        ).place(
            x=5,
            y=130
        )

    def destruir(self, frame: ctk.CTkFrame):
        """Método responsável por destruir a apresentação base do botão"""

        self.se_ja_foi_clicado = False
        frame.destroy()

    def verificacao_de_existencia_de_historico(self):
        """
        Descrição:
            Método responsável por fazer a devidamente verificação
            de existência dos arquivos inerentes à estação.
        """

        def criar_historico() -> None:
            """
            Descrição:
                Função responsável por criar o histórico da estação.

            Parâmetros:
                Nenhum

            Retorno:
                Criação do arquivo de histórico em planilha
            """

            pd.DataFrame(
                columns=[
                            "INSTANTE"
                        ] + var_globais[
                            "var_nomes"
                        ]
            ).to_excel(
                self.caminho_a_ser_buscado,
                index=False
            )

        dir_a_ser_buscado = "/".join(self.caminho_a_ser_buscado.split("/")[:-1])
        if not isdir(
                dir_a_ser_buscado
        ):
            mb.showwarning(
                "Cuidado",
                "Não havia histórico disponível para esta estação, foi criado agora."
            )

            mkdir(
                dir_a_ser_buscado
            )

            # Como não havia, podemos criar também
            criar_historico()

        if not isfile(
                self.caminho_a_ser_buscado
        ):
            criar_historico()

    def historico(
            self,
            se_ja_existe_janela_de_grafico: ctk.BooleanVar
    ) -> None:
        """
        Descrição:
            Método responsável por apresentar uma nova tela dispondo
            gráficos representantes dos valores da estação com o tempo.
        """

        def apresentando_grafico_do_historico(
                janela_atual: ctk.CTkToplevel,
                dados_completos: list[str],
                opcao_temporal_desejada: str,
                opcao_de_variavel_desejada: str,
                opcao_de_tempo_decorrido: str
        ) -> None:
            """
            Descrição:
                Função responsável por plotar o gráfico do histórico dentro da janela.
                Para isso, ela realiza uma filtragem dos dados para termos apenas o
                desejado.

            Parâmetros:
                Autoexplicativos.

            Retorno:
                Gráfico plotado.
            """

            def retirando_dados_inuteis(
                    dados: list[str],
                    momento_a_filtrar: str
            ) -> list[str]:
                """
                Descrição:
                    Função responsável por, a partir de quanto tempo se deseja
                    visualizar, retirar os dados que não fazem parte.

                    Haverá um algoritmo para a lógica de ignorar.
                    Atenção à ele.

                Parâmetros:
                    Autoexplicativos.

                Retorno:
                    Lista de Dados Atualizada.
                """

                def ignorar_dados(
                        x_dias_no_passado: int
                ) -> list[str]:
                    """
                    Descrição:
                        Função responsável por guardar o algoritmo para ignorarmos
                        as informações desejadas.

                        Se x = 1, vamos pegar o deste dia e o do dia anterior.
                        Se x = 7, vamos pegar o deste dia e de 7 dias anteriores.
                        Se x = 30, mesma lógica.

                    Parâmetros:
                        -> x_dias_no_passado:
                            Valor que indicará quanto desejamos voltar no passado.

                    Retorno:
                        Lista de informações desejadas.
                    """

                    # Lembre-se que os primeiros elementos
                    # da lista são os primeiros que foram adicionados
                    # Então devemos fazer nossa busca a partir
                    # do final
                    indice_da_linha = -1
                    while True:
                        try:
                            if len(dados[indice_da_linha][0]) > 4:

                                data_em_string = dados[indice_da_linha][0] + f"/{self.horario_e_data.year}"

                                obj_dt_do_dado_instantaneo = dt.strptime(
                                    data_em_string,
                                    "%H:%M:%S %d/%m/%Y"
                                )

                                diferenca_em_dias = abs(
                                    (
                                            self.horario_e_data - obj_dt_do_dado_instantaneo
                                    ).days
                                )
                                # print(f"Vejo o {indice_da_linha} que está defasado de {diferenca_em_dias} de hoje")
                                # print(f"Irei comparar com {x_dias_no_passado}")
                                if diferenca_em_dias >= x_dias_no_passado:
                                    # Então já temos todx o desejado
                                    if indice_da_linha == -1:
                                        return []

                                    return dados[indice_da_linha + 1:]
                            else:
                                # Então teremos um vazio
                                dados.pop(indice_da_linha)
                                indice_da_linha += 1

                            indice_da_linha -= 1
                        except IndexError:
                            # Pois já chegaremos no final
                            return dados[indice_da_linha + 1:]

                match momento_a_filtrar:

                    case "Tudo":
                        return dados

                    case "Último Dia":
                        return ignorar_dados(
                            1
                        )

                    case "Última Semana":
                        return ignorar_dados(
                            7
                        )

                    case "Último Mês":
                        return ignorar_dados(
                            30
                        )

                    case _:
                        return [""]

            def filtrando(
                    index_da_var: int
            ) -> tuple[list[str], list[float]]:
                """
                Descrição:
                    Função responsável por filtrar os dados conforme a necessidade temporal.

                Parâmetros:
                    -> index_da_var:
                        Indice indicador de qual variável deveremos pegar

                Retorno:
                    Tupla de duas listas, sendo uma string e outra de float
                """

                vetor_x, vetor_y = [], []

                match opcao_temporal_desejada:
                    case "Momentaneamente":
                        # Desejamos colocar todas os dados momentâneos

                        for lista_de_dados in dados_completos:

                            if len(lista_de_dados[0]) > 5:
                                vetor_x.append(
                                    lista_de_dados[0]
                                )
                                vetor_y.append(
                                    float(lista_de_dados[index_da_var])
                                )

                    case "Diariamente":
                        dia = ''
                        for lista_de_dados in dados_completos:

                            if len(lista_de_dados[0]) > 5:

                                dia_mes = lista_de_dados[0].split(" ")[-1]
                                dia_da_string = dia_mes.split("/")[0]

                                if dia == dia_da_string:
                                    # Então devemos atualizar o valor deste dia
                                    vetor_y[-1] += lista_de_dados[index_da_var]

                                else:
                                    dia = dia_da_string
                                    vetor_x.append(
                                        dia_mes
                                    )
                                    vetor_y.append(
                                        lista_de_dados[index_da_var]
                                    )

                    case "Mensalmente":
                        mes = ''
                        for lista_de_dados in dados_completos:

                            if len(lista_de_dados[0]) > 5:
                                mes_da_string = lista_de_dados[0].split(" ")[-1].split("/")[-1]

                                if mes == mes_da_string:
                                    # Atualizamos o último valor
                                    vetor_y[-1] += lista_de_dados[index_da_var]

                                else:
                                    mes = mes_da_string
                                    vetor_y.append(
                                        lista_de_dados[index_da_var]
                                    )
                                    vetor_x.append(
                                        mes
                                    )

                    case _:
                        return vetor_x, vetor_y

                return vetor_x, vetor_y

            if "" in {opcao_temporal_desejada, opcao_de_variavel_desejada}:
                return None

            # Devemos verificar se já há algum gráfico plotado
            ultimo_elemento = janela_atual.winfo_children()[-1]
            if isinstance(
                    ultimo_elemento,
                    Canvas
            ):
                ultimo_elemento.destroy()

            # A partir da seleção de opção temporal e opção de variável,
            # devemos fazer a filtragem de dados.
            index_da_var_desejada = 1  # Começamos com 1 devido à coluna chamada INSTANTE
            for nome_de_var in var_globais["var_nomes"]:
                if nome_de_var == opcao_de_variavel_desejada:
                    break

                index_da_var_desejada += 1

            # Devemos retirar também todx o tempo que não se
            # encaixa no tempo desejado.
            dados_completos = retirando_dados_inuteis(
                dados_completos,
                opcao_de_tempo_decorrido
            )

            if len(dados_completos) == 0:
                # Quer dizer que não existe nada útil para plotarmos
                mb.showinfo(
                    "Info",
                    "Não há dados a serem plotados nesta aglutinação de tempo"
                )

                return None

            eixo_x, eixo_y = filtrando(
                index_da_var_desejada
            )

            # Criando a figura adequada
            figura_a_ser_disposta = Figure(
                figsize=(10, 10)
            )
            figura_a_ser_disposta.subplots_adjust(
                left=0.1,
                right=0.97,
                top=0.95,
                bottom=0.3
            )
            axes = figura_a_ser_disposta.add_subplot(111)

            # Controlando a quantidade de labels que serão
            # apresentadas

            axes.bar(
                eixo_x,
                eixo_y
            )
            axes.set_xlabel("Tempo")
            axes.set_ylabel("Valores")
            axes.grid(True)
            axes.set_xticklabels(
                eixo_x,
                rotation=40,
                ha='right'
            )

            canvas = FigureCanvasTkAgg(
                figura_a_ser_disposta,
                janela_atual
            )
            canvas.draw()

            canvas.get_tk_widget().place(
                x=5,
                y=125,
                width=700,
                height=405
            )

        def criando_tela_para_disposicao(
                dados_completos: list[str]
        ) -> None:
            """
            Descrição:
                Função responsável pela criação e ajuste inicial da tela
                de disposição de dados do histórico da estação

            Parâmetros:
                -> dados_completos:
                    Lista de todas as linhas.

            Retorno:
                Subjanela ligada à interface principal
            """
            # Agora, devemos abrir uma nova janela, apresentando os dados da planilha.
            subjan = ctk.CTkToplevel(
                self.mestre
            )
            subjan.title(f"Apresentando Histórico Estação {self.id}")

            subjan.geometry(
                "565x430"
            )
            subjan.focus_force()

            ctk.CTkLabel(
                subjan,
                text="Tipo de Exibição Temporal: ",

                font=("Verdana", 12)
            ).place(x=5, y=5)

            combobox_de_apresentacao_temporal = ctk.CTkComboBox(
                subjan,
                values=[
                    "",
                    "Momentaneamente",
                    "Diariamente",
                    "Mensalmente"
                ],
                text_color="black",
                font=("Verdana", 12),

                fg_color="white",
                corner_radius=0,
                width=150,
                height=20
            )
            combobox_de_apresentacao_temporal.place(
                x=170,
                y=8
            )

            ctk.CTkLabel(
                subjan,
                text="Variável de Clima a ser Exibida: ",

                font=("Verdana", 12)
            ).place(x=5, y=35)

            combobox_de_var_de_clima = ctk.CTkComboBox(
                subjan,
                values=[""] + var_globais["var_nomes"],
                text_color="black",
                font=("Verdana", 12),

                fg_color="white",
                corner_radius=0,
                width=150,
                height=20
            )
            combobox_de_var_de_clima.place(
                x=200,
                y=5 + 35
            )

            ctk.CTkLabel(
                subjan,
                text="Quanto Tempo a Ser Exibido: ",

                font=("Verdana", 12)
            ).place(x=5, y=70)
            combobox_de_tempo = ctk.CTkComboBox(
                subjan,
                values=[
                    "Tudo",
                    "Último Dia",
                    "Última Semana",
                    "Último Mês"
                ],
                text_color="black",
                font=("Verdana", 12),

                fg_color="white",
                corner_radius=0,
                width=150,
                height=20
            )
            combobox_de_tempo.place(
                x=190,
                y=5 + 70
            )

            combobox_de_var_de_clima.configure(
                command=lambda event: apresentando_grafico_do_historico(subjan, dados_completos, combobox_de_apresentacao_temporal.get(), combobox_de_var_de_clima.get(), combobox_de_tempo.get())
            )

            combobox_de_apresentacao_temporal.configure(
                command=lambda event: apresentando_grafico_do_historico(subjan, dados_completos, combobox_de_apresentacao_temporal.get(), combobox_de_var_de_clima.get(), combobox_de_tempo.get())
            )

            combobox_de_tempo.configure(
                command=lambda event: apresentando_grafico_do_historico(subjan, dados_completos, combobox_de_apresentacao_temporal.get(), combobox_de_var_de_clima.get(), combobox_de_tempo.get())
            )

            subjan.protocol(
                "WM_DELETE_WINDOW",
                # Assim manipulamos melhor a sua destruição
                lambda: (
                    se_ja_existe_janela_de_grafico.set(False),
                    subjan.destroy()
                )
            )

        if se_ja_existe_janela_de_grafico.get():
            return None
        else:
            se_ja_existe_janela_de_grafico.set(True)

        # Primeiro, verificar se o arquivo de planilha existe.
        self.verificacao_de_existencia_de_historico()

        # Extraindo todos os dados que poderão ser usados
        dados_totais_extraidos = pd.read_excel(
            self.caminho_a_ser_buscado
        ).values.tolist()

        criando_tela_para_disposicao(
            dados_totais_extraidos
        )

    def atualizar_historico(
            self
    ):
        """
        Descrição:
            Método responsável por verificar se já é possível salvar os valores obtidos
            pela estação. Caso sim, atualiza-os.

            Há uma lista de strings que marcarão os horários que desejamos salvar.
            Entretanto, o instante em que conseguimos uma resposta do servidor não é
            completamente certeiro.

            Há toda uma lógica.
        """

        self.verificacao_de_existencia_de_historico()

        # Obtendo ultimo momento salvo
        if var_globais[
            "ultimo_momento_salvo_na_planilha"
        ][self.id - 1] is None:
            """
            No caso, precisamos pegar o último momento salvo na planilha.
            Para evitar abrirmos ela duas vezes, salvamos temporariamente o arquivo aberto.

            Mais a frente, caso precisemos salvar, usaremos oq já foi salvo.
            Caso não, apenas apagaremos.

            E como o 'ultimo_momento_salvo_na_planilha'
            não será mais None, isso não acontecerá novamente
            """
            temporariamente: pd.DataFrame = pd.read_excel(
                self.caminho_a_ser_buscado
            )

            # Obtemos o valor desejado
            try:
                ultimo_momento_salvo_str = str(temporariamente["INSTANTE"].iloc[-1]) + f"/{self.horario_e_data.year}"
                var_globais[
                    "ultimo_momento_salvo_na_planilha"
                ][self.id - 1] = dt.strptime(
                    ultimo_momento_salvo_str,
                    "%H:%M:%S %d/%m/%Y"
                )
            except (IndexError, TypeError, ValueError):
                # Basta colocar um valor suficientemente antigo
                var_globais[
                    "ultimo_momento_salvo_na_planilha"
                ][self.id - 1] = dt.strptime(
                    "00:00:00 1/1/2020",
                    "%H:%M:%S %d/%m/%Y"
                )

            # E então salvamos o histórico
            var_globais["historico_temporario"] = temporariamente

        string_de_atualizacao_para_data = f" {self.horario_e_data.day}/{self.horario_e_data.month}/{self.horario_e_data.year}"
        for horario_desejado_em_str in var_globais["momentos_desejados_de_salvamento"]:
            # Obtendo uma variável de tempo
            horario_desejado_em_str += string_de_atualizacao_para_data
            horario_desejado = dt.strptime(
                horario_desejado_em_str,
                "%H:%M:%S %d/%m/%Y"
            )

            # Afinal, os valores anteriores ao último momento salvo JÁ foram salvos
            if horario_desejado > var_globais[
                "ultimo_momento_salvo_na_planilha"
            ][
                self.id - 1
            ]:
                # Devemos verificar se já atingimos o instante
                if horario_desejado < self.horario_e_data < (
                        horario_desejado + var_globais[
                        "margem_temporal_de_salvamento"
                    ]
                ):
                    # Caso sim:
                    # Salvamos na planilha
                    arquivo_historico = var_globais.get(
                        "historico_temporario"
                    )

                    if arquivo_historico is None:
                        # Então abrimos
                        arquivo_historico = pd.read_excel(
                            self.caminho_a_ser_buscado
                        )
                    else:
                        var_globais.pop("historico_temporario")

                    arquivo_historico.loc[
                        len(arquivo_historico)
                    ] = [
                            self.horario_e_data.strftime(
                                "%H:%M:%S %d/%m"
                            )
                        ] + self.valores

                    arquivo_historico.to_excel(
                        self.caminho_a_ser_buscado,
                        index=False
                    )

                    # Atualizamos o último momento salvo
                    var_globais[
                        "ultimo_momento_salvo_na_planilha"
                    ][
                        self.id - 1
                    ] = self.horario_e_data

                    break


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
        (240, 360): [],  # 1
        (420, 350): [],  # 2
        (280, 450): [],  # 3
        (370, 220): [],  # 4
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


def alocando_estacoes(
        interface: ctk.CTk
) -> None:
    """
    Descrição:
        Função responsável por aplicar todx layout das estações
        e puxar suas funcionalidades do backend.

    Parâmetros:
        Autoexplicativo.

    Retorno:
        Estações Em Condições de Serem Usadas.
    """

    # Devemos verificar se há estações alocadas.
    # Vamos destruí-las
    widgets = interface.winfo_children()[::-1]
    if len(widgets) > 1:
        for elemento in widgets:
            if isinstance(elemento, ctk.CTkButton):
                elemento.destroy()
            else:
                if isinstance(elemento, ctk.CTkLabel):
                    elemento.destroy()
                break

    informacoes, horario_e_data_ultima_atualizacao = extraindo_informacoes_de_clima()
    horario_e_data_ultima_atualizacao: datetime

    # Podemos então colocar um aviso
    instante = f"{horario_e_data_ultima_atualizacao.hour}:{horario_e_data_ultima_atualizacao.minute}:{horario_e_data_ultima_atualizacao.second}"
    ctk.CTkLabel(
        interface,
        text=f" Última atualização: {instante}",
        text_color="#000000",
        font=("Verdana", 12),

        bg_color='#C2E5D1',
    ).place(
        x=0,
        y=interface.winfo_height() - 175
    )

    # De posse das informações, posso fazer o seguinte:
    i = 1
    for posicao_de_estacao in informacoes:
        Estacao(
            interface,
            posicao_de_estacao,
            informacoes[posicao_de_estacao],
            horario_e_data_ultima_atualizacao,
            i
        )
        i += 1

    # Recursão
    interface.after(
        # Não retira esse pow(10, 3), pois ele converte de
        # microsegundos para segundos
        var_globais["periodo_de_criacao_da_estacao"] * pow(10, 3),
        lambda: alocando_estacoes(interface)
    )


def interface_principal() -> None:
    """
    Descrição:
        Função responsável por gerar a interface principal na qual
        tudo estará funcionando.
        Executará diversas outras funcionalidades, esteja preparado.

    Parâmetros:
        Nenhum

    Retorno:
        Aplicação em condições.
    """

    def colocando_imagem_de_petropolis(
            janela_pai: ctk.CTk,
            tam_x: int,
            tam_y: int
    ) -> None:
        """
        Descrição:
            Função responsável por colocar a imagem na janela principal.
            Caso a imagem não exista, não vai dar exatamente erro, mas vai ficar uma bosta.

        Parâmetros:
            Autoexplicativos

        Retorno:
            Imagem de Petropólis ao fundo
        """

        try:
            imagem = Image.open(
                caminhos["Petropolis"]
            ).convert("RGBA")

            # Controlamos a opacidade da imagem aqui
            # 0 -> Opaco Completo
            # 255 -> Nenhum pouco opaco
            opacidade = 200
            imagem.putalpha(
                opacidade
            )

            imagem_configurada = ctk.CTkImage(
                imagem,
                size=(tam_x, tam_y)
            )

            ctk.CTkLabel(
                janela_pai,
                image=imagem_configurada,
                text=""
            ).place(
                x=0,
                y=0
            )

        except FileNotFoundError:
            # Barro
            pass

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    comp, alt = 670, 600
    interface = ctk.CTk()
    interface.title(
        "Apresentação Petrópolis"
    )
    interface.geometry(
        f"{comp}x{alt}"
    )
    interface.resizable(
        False,
        False
    )
    interface.iconbitmap("icone.ico")

    # Referenciando a cidade de petrópolis
    colocando_imagem_de_petropolis(
        interface,
        comp,
        alt
    )

    # Aqui, iniciamos a brincadeira.
    alocando_estacoes(interface)

    interface.mainloop()


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
# pyinstaller --onefile --windowed --copy-metadata numpy --icon=icone.ico TheBigOnes/EstacaoVirtualMeteorologica/Local_Storm.py
# pyinstaller Local_Storm.spec
