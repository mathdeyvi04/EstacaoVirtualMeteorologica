### Detalhes

Dado que a interface e seus comandos já são anti-burros, a necessidade
de documentação é apenas para futuros desenvolvedores que se dedicarão
neste projeto.

Faremos uma explicação breve de como o código funciona na **ordem de
funcionamento**.

### Sumário de Documentações

[Sobre a Inicialização da Aplicação](#inicializacao)

[Sobre Variáveis e Importações Inerentes à Aplicação](#back_variaveis_importacoes)

[Sobre Funções Básicas da Aplicação](#back_funcoes_basicas)

[Sobre Objetos Complexos](#back_classes)

[Sobre Conexão Com Servidor](#back_funcoes_conexao)

<div id='inicializacao'></div>

## _inicializacao.py_

Código responsável por:

* Fazer verificações de existência de caminhos inerentes à aplicação.


>Nesta parte a função faz a verificação dos caminhos nas seguintes variáveis
de dicionário que estão localizadas no arquivo _Back_Variaveis_Importacoes.py_
```python
diretorios = {
    "Nome_Da_Pasta": "caminho/ate/pasta"
    # ...
}

caminhos = {
    "Nome_Do_Arquivo": "caminho/ate/arquivo"
}
```
>Caso não existam alguns desses caminhos ou diretórios, a função cria-os
e avisa ao usuário sobre sua criação. Entretanto, com outros, o tratamento
não pode ser o mesmo, como nas imagens usadas na aplicação.

* Puxar a execução completa da aplicação.

>O sistema de importações de arquivos de código-fonte é linear e inicia-se
no arquivo de nome _Back_Variaveis_Importacoes.py_. Seguindo a ideia 
de uma lista linkada.

> Por exemplo, imagine uma quantidade n de arquivos, A_1.py, ..., A_n.py.
O código A_i.py pede informações do código A_(i+1).py, seguindo a recorrência
até o código de **maior responsabilidade**, A_n.py. Entenda como maior responsabilidade
o tamanho do dano que a falha de um arquivo pode trazer, dado que se A_n.py
falhar, todos os antecessores falharão também.

<div id="back_variaveis_importacoes"></div>

## _Back_Variaveis_Importacoes.py_

Código responsável por:

* Importar todas as tecnologias inerentes à aplicação.

> É interessante a devida visualização no arquivo para melhor
compreensão de quais tecnologias são exatamente usadas, mas a princípio:
>* _tkinter_ e seus derivados para a criação de interface.
>* _tkinter_ e seus derivados para a criação de interface.
>* _boto3_ e seus derivados para conexão com o terminal.
>* _os_ e _datetime_ para manipulação de dados operacionais.
>* _numpy_ e _netcdf4_ para manipulação de dados do satélite.
>* _pandas_ para manipulação de planilhas.
>* _matplotlib_ para visualização de gráficos.

* Criar variáveis inerentes à aplicação.

> Variáveis de caminho, pesquisa, conexão e demais são criadas neste
> código. Atente-se à variável _var_globais_, pois nela há diversas outras
> demais variáveis que são utilizadas.
> 
> Perceba que esta variável trata-se de um dicionário, então cuidado ao 
> tenta modificar nomes de chaves, pois elas deverão ser alteradas por 
> todo o código da aplicação.

<div id="back_funcoes_basicas"></div>

## _Back_FuncoesBasicas.py_

Código responsável por:

* Criar funções simples e amplamente usadas.

> Por exemplo, a função de correção da string dos dados do 
> satélite:

```python
def consertando_sufixo(
        #...
) -> str:
    """..."""
```

> Ou a função que corrige os dados de posição da cidade de 
> petrópolis e das estações. Dado que estes são obtidos em
> forma de latitude e de longitude.

<div id="back_classes"></div>

## _Back_Classes.py_

Código responsável por:

* Criar objetos mais detalhados:
  
    * Servidor()

    > Classe que organiza e representa todas as funcionalidades inerentes ao 
     servidor do satélite. Capaz de extrair, normalizar e baixar dados do mesmo.

    * DadosSat()
    
    > Classe que gerencia dados de satélite que já haviam sido previamente baixados.
    Capaz de obter informações realmente úteis sobre os dados e sequenciá-las.
  
    * Estacao()
    
    > Classe que representa as estações virtuais. Contendo todas as funcionalidades
    de Back e de Front da mesma. Atente-se a essa última parte.



<div id="back_funcoes_conexao"></div>

## _Back_FuncoesConexao.py_

Código responsável por:

* Gerenciar dados obtidos do servidor.

> Neste código, foca-se em utilizar-se principalmente das classes
> de Servidor() e DadosSat() a fim 
