import cv2
import numpy as np
import math
from PIL import Image

def calcular_parametros_reta(A, B):
    A_coef = B[1] - A[1]
    B_coef = A[0] - B[0]
    C_coef = A_coef * A[0] + B_coef * A[1]
    return A_coef, B_coef, C_coef

def calcular_distancia_ponto_reta(A_coef, B_coef, C_coef, ponto):
    x, y = ponto
    denominador = math.sqrt(A_coef**2 + B_coef**2)
    if denominador == 0:
        return float('inf')
    return abs(A_coef * x + B_coef * y - C_coef) / denominador

def processamento_bordas(P, T):
    Ab = []
    Fe = []

    for i in range(len(P)):
        A, B = P[i], P[(i + 1) % len(P)]
        if A[1] > B[1]:
            Ab.append(B)
            Fe.append(A)
        else:
            Ab.append(A)
            Fe.append(B)

    media_Ab = (sum(p[0] for p in Ab) / len(Ab), sum(p[1] for p in Ab) / len(Ab))
    media_Fe = (sum(p[0] for p in Fe) / len(Fe), sum(p[1] for p in Fe) / len(Fe))
    A_coef, B_coef, C_coef = calcular_parametros_reta(media_Ab, media_Fe)

    D_max = -1
    V_max = None
    for ponto in P:
        distancia = calcular_distancia_ponto_reta(A_coef, B_coef, C_coef, ponto)
        if distancia > D_max:
            D_max = distancia
            V_max = ponto

    while Ab:
        A = Ab.pop()
        distancia = calcular_distancia_ponto_reta(A_coef, B_coef, C_coef, A)
        if distancia > T:
            Fe.append(A)

    return Fe

class ProcessamentoRegional():
    def __init__(self, t):
        self.t = t

    def get_t(self):
        return self.t
    
    def set_t(self, t):
        self.t = t

    def processar(self, imagem):
        imagem_np = np.array(imagem)

        height, width = imagem_np.shape

        saida = np.zeros((height, width, 3), dtype=np.uint8)

        contornos, _ = cv2.findContours(imagem, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for contorno in contornos:
            pontos_borda = contorno[:, 0, :].tolist()

            resultado = processamento_bordas(pontos_borda, self.t)
            
            for i in range(len(resultado) - 1):
                ponto_atual = tuple(resultado[i])
                proximo_ponto = tuple(resultado[i + 1])
                cv2.line(saida, ponto_atual, proximo_ponto, (255), 1)

        return Image.fromarray(saida)

