"""
Descrição:
    Código responsável por realizar todas as importações necessárias
    para a aplicação funcionar e por criar as variáveis que serão
    utilizadas por toda ela.
"""

# Importações de Interface
from tkinter import messagebox as mb
import customtkinter as ctk

# Importações de Servidor
from mypy_boto3_s3 import S3Client
import boto3 as bt
from botocore import UNSIGNED
from botocore.client import Config

# Importações de Sistema
from os.path import isdir, isfile
from os import mkdir
from datetime import datetime as dt


# Importações de Manipulação de Dados
import netCDF4 as nc

# Importações de Visualização de Dados
from PIL import Image, ImageTk
from pprint import pprint


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
    "bucket": "noaa-goes16",

    "vars_de_clima": [
        "ABI-L2-TPWF",  # Total Precipitable Water Full Disk
    ]
}

