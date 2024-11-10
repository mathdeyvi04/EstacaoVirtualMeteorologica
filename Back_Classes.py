"""
Descrição:
    Código responsável por gerenciar as classes que usaremos, são estas
    a representação do servidor e a representação do banco de dados.
"""
import xarray

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
        self.arq_geral = nc.Dataset(
            arquivo_de_dados
        )

        self.dados = self.arq_geral.variables

        self.nome_do_arquivo_base = arquivo_de_dados

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

        # América do Sul
        EXTENSOES = [
            -50,  # Min Lon  --> Fugindo de Grewitch
            -30,  # Max Lon  --> Indo para Grewitch
            -24,  # Min Lat  --> Descendo para Polo Sul
            -10,  # Max Lat  --> Subindo para Polo Norte
        ]

        abrindo_arq_bizuradamente = xarray.open_dataset(self.nome_do_arquivo_base)

        # Pegando as informações necessárias
        dat = abrindo_arq_bizuradamente.metpy.parse_cf('LST')

        # Criando a transformação necessária
        geos = dat.metpy.cartopy_crs

        x = dat.x
        y = dat.y

        fig = pp.figure(figsize=(10, 6))

        # Criando a projeção safa, algo que não haviamos sido capazes
        # até agora
        projecao = ccrs.PlateCarree()

        ax = fig.add_subplot(1, 1, 1, projection=projecao)
        ax.set_extent(
            # Aqui colocamos as limitações no mapa geral
            EXTENSOES,
            crs=projecao
        )

        # Visualizar a imagem na projeção retangular
        ax.imshow(
            dados_da_var,
            origin='upper',
            extent=(
                x.min(), x.max(), y.min(), y.max()
            ),
            transform=geos,
            interpolation='none'
        )

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

        # Títulos
        pp.title('GOES-16 True Color', loc='left', fontweight='bold', fontsize=15)

        pp.show()
        abrindo_arq_bizuradamente.close()

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

        Parâmetros:
            Nenhum

        Retorno:
            Apresentação das variáveis de clima da estação.
        """

        if self.se_ja_foi_clicado:
            return None
        else:
            self.se_ja_foi_clicado = True

        # Ao lado do botão, devemos criar uma espécie de frame
        X = self.posicao_na_janela[0] + 50
        Y = self.posicao_na_janela[1]
        W = 153
        H = 120
        frame_apresentador = ctk.CTkFrame(
            self.mestre,
            fg_color="#FFFFFF",
            bg_color="#FFFFFF",
            width=W,
            height=H,
        )
        frame_apresentador.place(
            x=X,
            y=Y
        )

        colunas = ["Medidas", "Valor"]
        tv = Treeview(
            frame_apresentador,
            columns=colunas,
            show="headings"
        )

        tams = [
            130,
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
            height=35 * i
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

            width=sum(tams) - 35,
            height=20,
            hover_color='#ccb4b4',

            command=lambda: self.historico(se_ja_existe_janela)
        ).place(
            x=5,
            y=35 * i
        )

        ctk.CTkButton(
            frame_apresentador,
            text="Fechar",
            text_color="#000000",
            fg_color='#fafafa',
            border_width=2,
            border_color="#000000",
            font=("Verdana", 10, 'bold'),

            width=sum(tams) - 35,
            height=20,
            hover_color='#ccb4b4',

            command=lambda: self.destruir(frame_apresentador)
        ).place(
            x=5,
            y=35 * i + 25
        )

        frame_apresentador.configure(
            height=35 * i + 50
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

                                obj_dt = dt.strptime(
                                    data_em_string,
                                    "%H:%M:%S %d/%m/%Y"
                                )

                                diferenca_em_dias = abs(
                                    (
                                            self.horario_e_data - obj_dt
                                    ).days
                                )

                                if diferenca_em_dias > x_dias_no_passado:
                                    # Então já temos todx o desejado

                                    return dados[indice_da_linha:]
                            else:
                                # Então teremos um vazio
                                dados.pop(indice_da_linha)
                                indice_da_linha += 1

                            indice_da_linha -= 1
                        except IndexError:
                            pass

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
        ] is None:
            """
            No caso, precisamos pegar o último momento salvo na planilha.
            Para evitar abrimos ela duas vezes, salvamos temporariamente ela.
            
            Mais a frente, caso precisemos salvar, usaremos.
            Caso não, apenas apagaremos. E como o 'ultimo_momento_salvo_na_planilha'
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
                ] = dt.strptime(
                    ultimo_momento_salvo_str,
                    "%H:%M:%S %d/%m/%Y"
                )
            except (IndexError, TypeError, ValueError):
                var_globais[
                    "ultimo_momento_salvo_na_planilha"
                ] = dt.strptime(
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
            ]:
                # Devemos verificar se já atingimos o instante
                if self.horario_e_data > horario_desejado:
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
                    ] = self.horario_e_data

                    break
