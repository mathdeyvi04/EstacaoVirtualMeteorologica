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
        """
        Descrição:
            Método responsável por dar início ao banco de dados do satélite.
        """
        self.dados = nc.Dataset(
            arquivo_de_dados
        ).variables

        self.nome_da_variavel_de_clima = arquivo_de_dados.replace(".nc", "").split("-")[-1]

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
        for var in self.dados:
            if self.nome_da_variavel_de_clima.startswith(
                    var
            ):
                # Achamos
                return self.dados[var]

    def ampliando(
            self,
            matriz_de_pixels_total: MaskedArray
    ) -> MaskedArray:
        """
        Descrição:
            Método responsável por, a partir da matriz de pixels completa,
            fazer os cortes necessários para se obter apenas a região desejada.

        Parâmetros:
            Autoexplicativos

        Retorno:
            Matriz de pixels cortada.
        """

        # Aparentemente, há o padrão de que a lat e o lon vem em:
        informacoes_de_posicao_geoespacial: nc.Variable = self.dados[
            "geospatial_lat_lon_extent"
        ]
        """
        Ao fazermos print(informa...), obtemos:
        
        <class 'netCDF4._netCDF4.Variable'>
        float32 geospatial_lat_lon_extent()
            long_name: geospatial latitude and longitude references
            geospatial_westbound_longitude: 156.2995
            geospatial_northbound_latitude: 81.3282
            geospatial_eastbound_longitude: 6.2995
            geospatial_southbound_latitude: -81.3282
            geospatial_lat_center: 0.0
            geospatial_lon_center: -75.0
            geospatial_lat_nadir: 0.0
            geospatial_lon_nadir: -75.0
            geospatial_lat_units: degrees_north
            geospatial_lon_units: degrees_east
        unlimited dimensions:
            current shape = ()
        filling on, default _FillValue of 9.969209968386869e+36 used
        """

        # Como sabemos que as informações vêm em uma ordem específica
        # Não precisamos de loop para obtê-las
        indice_dos_atributos_desejados = [1, 2, 3, 4]
        nome_dos_atributos = informacoes_de_posicao_geoespacial.ncattrs()

        lon_min, lat_max, lon_max, lat_min = [
            informacoes_de_posicao_geoespacial.getncattr(
                nome_dos_atributos[index]
            ) for index in indice_dos_atributos_desejados
        ]

        """Explicação:
        Latitude Mais Ao Norte -> lat_max
        Latitude Mais Ao Sul -> lat_min ( Esta estará em negativo )
        
        Longetude Mais Ao Leste -> lon_max
        Longetude Mais Ao Oeste -> long_min (Esta estará em negativo )
        """

        # De posse das latitudes da imagem completa, devemos setar apenas o desejado.
        """Petrópolis Centro -> Lat: -22.510072  Lon: -43.191425"""
        MAX_LAT = 0
        MIN_LAT = -20

        # Imagine que voce está no centro da terra
        # A máxima longitude é obtida indo cada vez mais para o oeste.
        MAX_LON = -80
        MIN_LON = -20

        # Vamos criar uma função para estes valores
        lat_desejado_max, lat_desejado_min = corretor_de_geocoordenadas(MIN_LAT, True), corretor_de_geocoordenadas(MAX_LAT, True)
        lon_desejado_max, lon_desejado_min = corretor_de_geocoordenadas(MIN_LON, False), corretor_de_geocoordenadas(MAX_LON, False)

        # Supondo linearidade, podemos:
        n_linhas = len(
            matriz_de_pixels_total
        )
        n_colunas = len(
            matriz_de_pixels_total[0]
        )
        vetor_de_lat = linspace(
            lat_min,
            lat_max,
            n_linhas
        )
        vetor_de_lon = linspace(
            lon_min,
            lon_max,
            n_colunas
        )

        val_lat_desejados = where(
            (
                    vetor_de_lat >= lat_desejado_min
            ) & (
                    vetor_de_lat <= lat_desejado_max
            )
        )[0]
        val_lon_desejados = where(
            (
                    vetor_de_lon >= lon_desejado_min
            ) & (
                    vetor_de_lon <= lon_desejado_max
            )
        )[0]

        return matriz_de_pixels_total[ix_(val_lat_desejados, val_lon_desejados)]

    def colhendo_pixels(
            self,
            dados_da_var: nc.Variable
    ) -> MaskedArray:
        """
        Descrição:
            Método responsável por gerar a matriz de pixels da variável.
            Aqui devemos pegar a matriz total e buscar pela cidade de Petrópolis.

        Parâmetros:
            -> dados_da_var:
                Resultado do método obtendo_dados_da_variavel_de_clima

        Retorno:
            Matriz de valores da variável de clima.
        """

        if not isinstance(
                dados_da_var,
                nc.Variable
        ):
            raise TypeError

        matriz = dados_da_var[:]

        matriz = self.ampliando(
            matriz
        )

        # Caso testes futuros sejam necessários, é importante descomentar
        # essa parte para termos acessos aos gráficos gerados pelo fatiamento.
        pp.imshow(
            matriz,
            cmap="gray"
        )
        pp.grid(True)
        pp.title(self.nome_da_variavel_de_clima)
        pp.show()

        return matriz


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
            lista_de_variaveis_de_clima: list[float]
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

            fg_color="#C2E5D1",
            bg_color="#C2E5D1",
            hover_color="#C0FFC3",
            width=30,

        )
        # E posicionamos ele na coordenada correta.
        # Aqui, apenas para exemplo
        self.posicao_na_janela = posicao_da_estacao
        self.entidade.place(
            x=self.posicao_na_janela[0],
            y=self.posicao_na_janela[1]
        )

        self.valores = lista_de_variaveis_de_clima

        self.entidade.configure(
            command=self.clicado
        )

    def clicado(self):
        """
        Descrição:
            Método responsável por, quando o botão for clicado, uma janelinha
            surgir e apresentar valores específicos.

        Parâmetros:
            Nenhum

        Retorno:
            Apresentação das variáveis de clima da estação.
        """

        # Ao lado do botão, devemos criar uma espécie de frame
        X = self.posicao_na_janela[0] + 50
        Y = self.posicao_na_janela[1]
        W = 80
        H = 20
        frame_apresentador = ctk.CTkFrame(
            self.mestre,
            fg_color="#FFFFFF",
            bg_color="#FFFFFF",
            width=W,
            height=H
        )
        frame_apresentador.place(
            x=X,
            y=Y
        )

        # Vamos apresentar as coisas
        for valor_numerico, nome_da_variavel in zip(self.valores, var_globais["var_nomes"]):
            ctk.CTkLabel(
                frame_apresentador,
                text=f"{nome_da_variavel} -> {valor_numerico}",
                text_color="#000000",
                font=(
                    "Verdana",
                    10
                )
            ).place(
                x=5,
                y=H + 30
            )

        var_globais[
            "area_dos_frames_apresentados"
        ].append(
            [
                X, Y, W, H
            ]
        )






