# Trabalho final da disciplina de Processamento de Imagens Digitais
>Colaboradores: [Luiz Becher](https://github.com/lbecher) e [Heloisa Alves](https://github.com/Helogizzy)

## Descrição
Consiste na implementação dos algoritmos para Ligação dos Pontos de Borda. As três abordagens implementadas são: 
- processamento local;
- regional;
- global.

O processamento local deve incorporar o algoritmo apresentado no slide 42 das notas de aula ([Segmentação de Imagens.pdf](https://www.inf.unioeste.br/~adair/PID/Notas%20Aula/Segmentacao%20de%20Imagens.pdf)). O processamento regional deve incorporar o algoritmo apresentado no slide 47 das mesmas notas. O processamento global deve ser realizado pela transformada de Hough, aplicada somente para linhas.

A entrada consiste em imagens em tons de cinza, estas imagens passam por um pré-processamento do algortimo de Canny e o Filtro Gaussinao passa-baixa. Além disso, o processamento local de bordas constroi as imagens magnitude do gradiente e ângulos do vetor gradiente.

A saída dos programas consiste em imagens com as bordas ligadas pelos algoritmos das diferentes estratégias implementadas.
