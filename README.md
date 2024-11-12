# Estação Virtual Meteorológica
 
## Descrição

Por meio da matéria Introdução à Projetos de Engenharia,
o grupo Lima Salgados composto pelos alunos:

* De Melo
* Santana 
* Deyvisson
* Moraes
* Machado
* Bertolini

Possui o trabalho de construir uma espécie de software de
Estação Virtual Meteorológica. Em teoria, deve gerar
informações de atmosfera partir de dados obtidos de satélite,
em especial GOES - 16.

## Necessidades Inerentes ao Projeto

* Obtenção de Dados a partir do satélite.
* Apresentação de Informações de Clima em tempo quase-real.
* Armazenamento Inteligente de Informações

## Tecnologias Utilizadas

Neste trabalho serão utilizados os seguintes módulos e seus respectivos
motivos:

* netCDF4 ----- Manipulação dos Dados Gerados pelo Satélite GOES - 16
* boto3 ----- Conexão com Servidor
* customtkinter ----- Interfaces Gráficas
* pandas ----- Manipulação de Planilhas em código
* cartopy ----- Projeção Geoestacionária

## Como fazer funcionar?

#### Sobre a precursão
O arquivo _inicializacao.py_ é o arquivo que deve ser executado
para que a aplicação funcione.

#### Sobre as Variáveis de Clima
No arquivo *Back_Variaveis_Importacoes.py* residem as variáveis 
e importações intrínsecas à aplicação, em especial um dicionário:
```python
var_globais = {
    'vars_de_clima': [
        'xxxx',
        'yyyy'
    ],
}
```
Alterando os códigos que existem dentro desta lista, sendo estes
aqueles produtos disponíveis, por exemplo: _ABI-L2-LSTF_, alteramos
as variáveis que serão buscadas pela aplicação.
