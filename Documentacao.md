### Detalhes

Dado que a interface e seus comandos já são anti-burros, a necessidade
de documentação é apenas para futuros desenvolvedores que se dedicarão
ao projeto.

Faremos uma explicação breve de como o código funciona na **ordem de
funcionamento**.

### Sumário de Documentações

[Sobre a Inicialização da Aplicação](#_inicializacaopy_)

[Sobre Variáveis e Importações Inerentes à Aplicação](#_back_variaveis_importacoespy_)

[Sobre Funções Básicas da Aplicação](#_back_funcoesbasicaspy_)

[Sobre Objetos Criados](#_back_classespy_)


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
de uma lista linkada. Por exemplo, imagine uma quantidade n de arquivos, A_1.py, ..., A_n.py.
O código A_i.py pede informações do código A_(i+1).py, seguindo a recorrência
até o código de **maior responsabilidade**, A_n.py. Entenda como maior responsabilidade
o tamanho do dano que a falha de um arquivo pode trazer, dado que se A_n.py
falhar, todos os antecessores falharão também.


## _Back_Variaveis_Importacoes.py_

Código responsável por:

* Importar todas as tecnologias inerentes à aplicação.

> É interessante a devida visualização do arquivo para melhor
compreensão de quais tecnologias são exatamente usadas.

* Criar variáveis inerentes à aplicação.

> Variáveis de caminho, pesquisa, conexão e demais são criadas neste
> código. Atente-se à variável _var_globais_, pois nela há diversas outras
> demais variáveis que são utilizadas.
> 
> Perceba que esta variável trata-se de um dicionário, então cuidado ao 
> tenta modificar nomes de chaves, pois elas deverão ser alteradas por 
> todo o código da aplicação.

## _Back_FuncoesBasicas.py_

Código responsável por:

* Criar funções simples e amplamente usadas.

## _Back_Classes.py_

Código responsável por:

* Criar um objeto de conexão com o servidor.
* Criar um objeto capaz de representar os arquivos do Satélite.
* Criar as Estações Virtuais.

## _Back_FuncoesConexao.py_

Código responsável por:

* Atualizar os valores dentro das estações.

## _FrontEndCompleto.py_

Código responsável por:

* Construir a interface principal.

