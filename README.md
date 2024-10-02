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
Estação Virtual Meteorológica. Em teoria, deve conseguir gerar
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

## Recomendação
Caso deseje ser um contribuidor, sugiro a leitura do arquivo de
Padroes_de_Codigo_a_Serem_Seguidos.md