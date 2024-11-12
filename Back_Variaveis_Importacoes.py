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
        "18:54:00"
    ],
    "margem_temporal_de_salvamento": timedelta(
        # Você pode colocar o valor que quiser, mas cuidade
        minutes=20
    ),

    "ultimo_momento_salvo_na_planilha": [None, None, None, None]
}