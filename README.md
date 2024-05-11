# pid-final

## Descrição

Boa tarde a todos.

O trabalho final para a disciplina de PID (ano letivo 2023) consistirá na implementação dos algoritmos para Ligação dos Pontos de Borda. As três abordagens devem ser implementadas: processamento local, regional e global.

O processamento local deve incorporar o algoritmo apresentado no slide 42 das notas de aula ([Segmentação de Imagens.pdf](https://www.inf.unioeste.br/~adair/PID/Notas%20Aula/Segmentacao%20de%20Imagens.pdf)). O processamento regional deve incorporar o algoritmo apresentado no slide 47 das mesmas notas. O processamento global deve ser realizado pela transformada de Hough, aplicada somente para linhas.

Qualquer implementação outra, que não os algoritmos acima solicitados, não será considerada. Ou seja, leiam os slides e implementem o que está apresentado neles.

A entrada para os programas consistirá em imagens em tons de cinza. Estas imagens deverão sofrer pré-processamentos como filtragem passa-baixa e limiarização, por exemplo.

Além disso, é necessidade intrínseca ao processamento local de bordas, a construção das imagens magnitude do gradiente e ângulos do vetor gradiente, pois são necessárias no algoritmo.

A saída dos programas consistirá em imagens com as bordas ligadas pelos algoritmos das diferentes estratégias implementadas.

Podem ser usadas bibliotecas externas, limitadas às operações de leitura e escrita de arquivos em disco. As operações de processamento de imagens necessárias devem ser implementadas no escopo do trabalho.

Quaisquer dúvidas, entrem em contato.

Att.
Adair Santa Catarina
Professor da disciplina de PID.
