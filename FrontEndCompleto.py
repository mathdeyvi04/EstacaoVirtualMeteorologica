"""
Descrição:
    Código responsável por criar todx o layout da aplicação.
"""
from Back_FuncoesConexao import *


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

    # Devemos verificar se há botões
    widgets = interface.winfo_children()[::-1]
    if len(widgets) > 1:
        for elemento in widgets:
            if isinstance(elemento, ctk.CTkButton):
                elemento.destroy()
            else:
                if isinstance(elemento, ctk.CTkLabel):
                    elemento.destroy()
                break

    informacoes, instante = extraindo_informacoes_de_clima()
    informacoes = {
        (100, 100): [12, 34]
    }

    # Podemos então colocar um aviso
    ctk.CTkLabel(
        interface,
        text=f"Última atualização: {instante}",
        text_color="#000000",
        font=("Verdana", 12),

        bg_color='#C2E5D1'
    ).place(
        x=0,
        y=interface.winfo_height() - 140
    )

    # De posse das informações, posso fazer o seguinte:
    i = 1
    for posicao_de_estacao in informacoes:
        Estacao(
            interface,
            posicao_de_estacao,
            informacoes[posicao_de_estacao],
            instante,
            i
        )
        i += 1

    # Recursão
    interface.after(var_globais["periodo_estacao"] * pow(10, 3), lambda: alocando_estacoes(interface))

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

    comp, alt = 600, 450
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

    # Referenciando a cidade de petrópolis
    colocando_imagem_de_petropolis(
        interface,
        comp,
        alt
    )

    # Aqui, iniciamos a brincadeira.
    alocando_estacoes(interface)


    interface.mainloop()
