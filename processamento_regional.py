import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import math

import math
from PIL import Image

def distancia_da_linha(ponto, pontos_da_linha):
    x0, y0 = ponto
    x1, y1 = pontos_da_linha[0]
    x2, y2 = pontos_da_linha[1]
    return abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1) / math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2)

def encontrar_pontos_mais_distantes(pontos):
    dist_max = 0
    ponto_a = None
    ponto_b = None

    for i in range(len(pontos)):
        for j in range(i + 1, len(pontos)):
            dist = math.hypot(pontos[i][0] - pontos[j][0], pontos[i][1] - pontos[j][1])
            if dist > dist_max:
                dist_max = dist
                ponto_a = pontos[i]
                ponto_b = pontos[j]

    return [ponto_a, ponto_b]

def angulo_com_centroide(centroide, ponto):
    vetor = [ponto[0] - centroide[0], ponto[1] - centroide[1]]
    return -math.atan2(vetor[1], vetor[0])

def calcular_distancia_referencia(pontos):
    coords_x = [p[0] for p in pontos]
    coords_y = [p[1] for p in pontos]
    largura = max(coords_x) - min(coords_x)
    altura = max(coords_y) - min(coords_y)
    return 0.2 * min(largura, altura)

def preencher_pontos_faltantes_da_borda(pontos):
    pontos_preenchidos = []
    for i in range(len(pontos) - 1):
        x1, y1 = pontos[i]
        x2, y2 = pontos[i + 1]
        pontos_preenchidos.append(pontos[i])

        dist = math.hypot(x2 - x1, y2 - y1)
        num_passos = math.ceil(dist / 2)
        for passo in range(1, num_passos):
            t = passo / num_passos
            x = round(x1 + t * (x2 - x1))
            y = round(y1 + t * (y2 - y1))
            pontos_preenchidos.append([x, y])

    pontos_preenchidos.append(pontos[-1])
    return pontos_preenchidos

def processamento_regional_da_borda(imagem, limiar):
    pontos = []
    largura, altura = imagem.size
    taxa_amostragem = 1

    for y in range(0, altura, taxa_amostragem):
        for x in range(0, largura, taxa_amostragem):
            brilho = imagem.getpixel((x, y))
            if brilho > 0:
                pontos.append([x, y])

    if len(pontos) < 2:
        return pontos

    centroide = [sum(p[i] for p in pontos) / len(pontos) for i in range(2)]
    pontos.sort(key=lambda p: angulo_com_centroide(centroide, p))

    B, A = encontrar_pontos_mais_distantes(pontos)
    distancia_referencia = calcular_distancia_referencia(pontos)

    pilha_ab = [B, A]
    pilha_fe = [B]
    tamanho_ultima_pilha = 0

    while pilha_ab and tamanho_ultima_pilha != len(pilha_ab):
        tamanho_ultima_pilha = len(pilha_ab)
        P1 = pilha_ab[-1]
        P2 = pilha_fe[-1]
        indice_P1 = pontos.index(P1)
        indice_P2 = pontos.index(P2)
        Dmax = 0
        Vmax = None

        for i in range(indice_P1 + 1, indice_P1 + len(pontos)):
            ponto = pontos[i % len(pontos)]
            dist = distancia_da_linha(ponto, [P1, P2])
            if dist > Dmax:
                Dmax = dist
                Vmax = ponto
            if i % len(pontos) == indice_P2:
                break

        if Dmax > limiar:
            pilha_ab.append(Vmax)
        else:
            ponto_removido = pilha_ab.pop()
            pilha_fe.append(ponto_removido)

    pontos_preenchidos = preencher_pontos_faltantes_da_borda(pilha_fe)
    return pontos_preenchidos


class ProcessamentoRegional():
    def __init__(self, t):
        self.t = t

    def get_t(self):
        return self.t
    
    def set_t(self, t):
        self.t = t

    def extrair_pontos_da_imagem(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # Afinamento (Skeletonization)
        thinned = cv2.ximgproc.thinning(binary)
        
        # Encontrar coordenadas dos pontos não-zero
        pontos = np.column_stack(np.where(thinned > 0))
        return pontos

    def processar(self, img_path):
        img = Image.open(img_path).convert('L')
        resultado = processamento_regional_da_borda(img, self.t)
        width, height = img.size

        saida = np.zeros((height, width, 3), dtype=np.uint8)
        for i in range(len(resultado) - 1):
            ponto_atual = tuple(resultado[i])
            proximo_ponto = tuple(resultado[i + 1])
            cv2.line(saida, ponto_atual, proximo_ponto, (255, 255, 255), 1)
        
        # Convertendo o resultado para um objeto PIL Image
        return Image.fromarray(saida)