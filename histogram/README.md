# Histogram

O algoritmo pedido foi implementado.
Pode-se separar a implementação da tarefa em dois passos:
- Leitura de input, alimentando dicionário de contagem (histograma)
- Ordenação decrescente do histograma em função da contagem

A estrutura de dados escolhida para manter o histograma foi um array de 26 posições, onde a `i`-esima corresponde ao `i`-esimo caracter (letra minúscula) da tabela ASCII.
Como a quantidade de caracteres é fixa, para esse caso específico, essa opção possui mesma complexidade assintótica de hash tables ou árvores binárias de busca.
Porém, sabe-se que essa opção possui melhor constante que as demais. Logo, foi a implementada.
  
Nota-se que, ao invés de um `vector<int>`, utilizou-se um `vector<pair<char,int>>`. 
Isso foi feito para, após a ordenação do segundo passo, quais caracteres ocupam quais posições no vetor ordenado.
  
Sendo `N` a quantidade de caracteres do input, o primeiro passo executa em tempo `Theta(N)`.
A ordenação empregada foi a padrão do `stl` (quicksort), mas ordenação em tempo linear (por contagem) também poderia ser utilizada aqui.
Porém, não foi necessária, já que, como dito, a quantidade de caracteres é fixa e pequena, e a implementação dessa ordenação traria complexidade de código desnecessária.