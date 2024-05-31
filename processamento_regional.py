import cv2
import numpy as np
from PIL import Image
import math
import matplotlib.pyplot as plt

# Função para calcular a distância de um ponto a uma linha definida por dois pontos
def distancia_da_linha(ponto, pontos_da_linha):
    x0, y0 = ponto
    x1, y1 = pontos_da_linha[0]
    x2, y2 = pontos_da_linha[1]
    # Fórmula para calcular a distância entre um ponto e uma linha usando a fórmula de distância ponto-linha
    return abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1) / math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)

# Função para encontrar os dois pontos mais distantes em uma lista de pontos
def encontrar_pontos_mais_distantes(pontos):
    dist_max = 0
    ponto_a = None
    ponto_b = None

    for i in range(len(pontos)):
        for j in range(i + 1, len(pontos)):
            # Calcula a distância entre dois pontos usando a função hypot da biblioteca math
            dist = math.hypot(pontos[i][0] - pontos[j][0], pontos[i][1] - pontos[j][1])
            if dist > dist_max:
                dist_max = dist
                ponto_a = pontos[i]
                ponto_b = pontos[j]

    return [ponto_a, ponto_b]

# Função para calcular o ângulo entre um ponto e o centroide
def angulo_com_centroide(centroide, ponto):
    # Calcula o vetor entre o ponto e o centroide
    vetor = [ponto[0] - centroide[0], ponto[1] - centroide[1]]
    # Usa a função atan2 para calcular o ângulo entre o vetor e o eixo x
    return -math.atan2(vetor[1], vetor[0])

# Função para calcular a distância de referência usada no algoritmo
def calcular_distancia_referencia(pontos):
    # Calcula as coordenadas x e y dos pontos
    coords_x = [p[0] for p in pontos]
    coords_y = [p[1] for p in pontos]
    # Calcula a largura e a altura do retângulo envolvendo os pontos
    largura = max(coords_x) - min(coords_x)
    altura = max(coords_y) - min(coords_y)
    # Retorna 20% da menor dimensão do retângulo
    return 0.2 * min(largura, altura)

# Função para preencher os pontos faltantes entre os pontos da borda
def preencher_pontos_faltantes_da_borda(pontos):
    pontos_preenchidos = []
    for i in range(len(pontos) - 1):
        x1, y1 = pontos[i]
        x2, y2 = pontos[i + 1]
        pontos_preenchidos.append(pontos[i])

        # Calcula a distância entre os dois pontos
        dist = math.hypot(x2 - x1, y2 - y1)
        # Calcula o número de passos necessários para preencher a distância entre os dois pontos
        num_passos = math.ceil(dist / 2)
        for passo in range(1, num_passos):
            t = passo / num_passos
            # Calcula os pontos intermediários entre os dois pontos originais
            x = round(x1 + t * (x2 - x1))
            y = round(y1 + t * (y2 - y1))
            pontos_preenchidos.append([x, y])

    pontos_preenchidos.append(pontos[-1])
    return pontos_preenchidos

# Função principal para realizar o processamento regional da borda
def processamento_regional_da_borda(imagem, limiar):
    pontos = []
    largura, altura = imagem.size
    taxa_amostragem = 1

    # Percorre a imagem e coleta os pontos brilhantes
    for y in range(0, altura, taxa_amostragem):
        for x in range(0, largura, taxa_amostragem):
            brilho = imagem.getpixel((x, y))
            if brilho > 0:
                pontos.append([x, y])

    # Se houver menos de dois pontos, retorna a lista de pontos
    if len(pontos) < 2:
        return pontos

    # Calcula o centroide dos pontos
    centroide = [sum(p[i] for p in pontos) / len(pontos) for i in range(2)]
    
    # Ordena os pontos de acordo com o ângulo em relação ao centroide
    pontos.sort(key=lambda p: angulo_com_centroide(centroide, p))

    # Encontra os dois pontos mais distantes
    B, A = encontrar_pontos_mais_distantes(pontos)
    
    # Calcula a distância de referência
    distancia_referencia = calcular_distancia_referencia(pontos)

    # Inicializa as pilhas AB e FE
    pilha_ab = [B, A]
    pilha_fe = [B]
    tamanho_ultima_pilha = 0

    # Realiza o processamento regional
    while pilha_ab and tamanho_ultima_pilha != len(pilha_ab):
        tamanho_ultima_pilha = len(pilha_ab)
        P1 = pilha_ab[-1]
        P2 = pilha_fe[-1]
        indice_P1 = pontos.index(P1)
        indice_P2 = pontos.index(P2)
        Dmax = 0
        Vmax = None

        # Percorre os pontos para encontrar o próximo ponto Vmax
        for i in range(indice_P1 + 1, indice_P1 + len(pontos)):
            ponto = pontos[i % len(pontos)]
            # Calcula a distância do ponto à linha formada por P1 e P2
            dist = distancia_da_linha(ponto, [P1, P2])
            if dist > Dmax:
                Dmax = dist
                Vmax = ponto
            if i % len(pontos) == indice_P2:
                break

        # Adiciona ou remove pontos das pilhas baseado no limiar
        if Dmax > limiar:
            pilha_ab.append(Vmax)
        else:
            ponto_removido = pilha_ab.pop()
            pilha_fe.append(ponto_removido)

    # Preenche os pontos faltantes da borda
    pontos_preenchidos = preencher_pontos_faltantes_da_borda(pilha_fe)
    return pontos_preenchidos

# Classe para encapsular o processamento regional da borda
class ProcessamentoRegional():
    def __init__(self, t):
        self.t = t

    def get_t(self):
        return self.t
    
    def set_t(self, t):
        self.t = t

    # Método para extrair os pontos da imagem
    def extrair_pontos_da_imagem(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # Afinamento (Skeletonization)
        thinned = cv2.ximgproc.thinning(binary)
        
        # Encontrar coordenadas dos pontos não-zero
        pontos = np.column_stack(np.where(thinned > 0))
        return pontos

    # Método principal para processar a imagem
    def processar(self, img_path):
        img = Image.open(img_path).convert('L')
        resultado = processamento_regional_da_borda(img, self.t)
        width, height = img.size

        # Cria uma imagem em branco para desenhar a borda
        saida = np.zeros((height, width, 3), dtype=np.uint8)
        for i in range(len(resultado) - 1):
            ponto_atual = tuple(resultado[i])
            proximo_ponto = tuple(resultado[i + 1])
            # Desenha uma linha entre os pontos adjacentes da borda
            cv2.line(saida, ponto_atual, proximo_ponto, (255, 255, 255), 1)
        
        # Converte a imagem resultante para um objeto PIL Image
        return Image.fromarray(saida)
