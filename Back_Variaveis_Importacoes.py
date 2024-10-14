"""
Descrição:
    Código responsável por realizar todas as importações necessárias
    para a aplicação funcionar e por criar as variáveis que serão
    utilizadas por toda ela.
"""

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
from os import mkdir
from datetime import datetime as dt
from datetime import timedelta, time

# Importações de Manipulação de Dados
import netCDF4 as nc
from numpy.ma.core import MaskedArray
from numpy import linspace, where, ix_
import pandas as pd

# Importações de Visualização de Dados
from PIL import Image, ImageTk
from pprint import pprint
from matplotlib import pyplot as pp
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator

# -------------------------------------------------------------------------

diretorios = {
    # Indicador de Onde Nosso Banco de Dados Geral Ficará
    # Em teoria, ele armazenará os dados obtidos pelas Estações
    "Banco Geral": "./Banco Geral",
}

caminhos = {
    "Petropolis": "./petropolis.png"
}

# Variáveis Concorrentes
var_globais = {
    # Variáveis Necessárias Para Obtenção de Dados
    "bucket": "noaa-goes16",
    "vars_de_clima": [
        "ABI-L2-LSTF",  #
    ],
    "var_nomes": [
        "Temperatura(°C)",
        "Pressão(atm)"
    ],

    # Variáveis Necessárias Para Periodicidade de Funções
    "periodo_de_criacao_da_estacao": 60,  # EM SEGUNDOS
    "momentos_desejados_de_salvamento": [
        # Strings em Formato de Horário
        "13:15:00"
    ],

    "ultimo_momento_salvo_na_planilha": None

    #
}
