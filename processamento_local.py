from PIL import Image
import cv2
import numpy as np

class ProcessamentoLocal():
    def __init__(self):
        self.todos_os_angulos = True
        self.angulo = 0
        self.faixa = 2
        self.limiar = 100
        self.k = 3

    def set_todos_os_angulos(self, todos_os_angulos):
        self.todos_os_angulos = todos_os_angulos
    
    def get_todos_os_angulos(self):
        return self.todos_os_angulos
    
    def set_angulo(self, angulo):
        self.angulo = angulo
    
    def get_angulo(self):
        return self.angulo
    
    def set_faixa(self, faixa):
        self.faixa = faixa
    
    def get_faixa(self):
        return self.faixa
    
    def set_limiar(self, limiar):
        self.limiar = limiar
    
    def get_limiar(self):
        return self.limiar
    
    def set_k(self, k):
        self.k = k
    
    def get_k(self):
        return self.k

    def processar(self, imagem):
        # Converte imagem para matriz em tons de cinza
        f = cv2.cvtColor(np.array(imagem), cv2.COLOR_RGB2GRAY)

        # Calcula as matrizes M(x,y) e alpha(x,y)
        x = cv2.Sobel(f, cv2.CV_64F, 1, 0, ksize=3)
        y = cv2.Sobel(f, cv2.CV_64F, 0, 1, ksize=3)

        m = np.sqrt(x**2 + y**2)
        alpha = np.arctan2(x, y)

        g = np.zeros(f.shape, dtype=np.uint8)

        # Aplica os limites
        margem = np.deg2rad(self.faixa / 2)
        if self.todos_os_angulos:
            angulo = 0
            g |= (m > self.limiar) & ((alpha > angulo - margem) & (alpha < angulo + margem))
            for _ in range(4):
                angulo += np.pi / 4
                g |= (m > self.limiar) & ((alpha > angulo - margem) & (alpha < angulo + margem))
        else:
            angulo = np.deg2rad(self.angulo)
            g |= (m > self.limiar) & ((alpha > angulo - margem) & (alpha < angulo + margem))

        def marcar_falhas(g, k):
            for i in range(g.shape[0]):
                zeros = []
                for j in range(g.shape[1]):
                    if g[i, j] == 0:
                        zeros.append(j)
                    else:
                        if 0 < len(zeros) <= k:
                            for z in zeros:
                                g[i, z] = 1
                        zeros = []
                if 0 < len(zeros) <= k:
                    for z in zeros:
                        g[i, z] = 1

            for j in range(g.shape[1]):
                zeros = []
                for i in range(g.shape[0]):
                    if g[i, j] == 0:
                        zeros.append(i)
                    else:
                        if 0 < len(zeros) <= k:
                            for z in zeros:
                                g[z, j] = 1
                        zeros = []
                if 0 < len(zeros) <= k:
                    for z in zeros:
                        g[z, j] = 1

        def rotacionar_imagem(g, angulo):
            (h, w) = g.shape
            centro = (w // 2, h // 2)
            matriz_rotacao = cv2.getRotationMatrix2D(centro, np.degrees(angulo), 1.0)
            g_rotacionada = cv2.warpAffine(g, matriz_rotacao, (w, h))
            return g_rotacionada

        marcar_falhas(g, self.k)

        for theta in [np.pi / 4, -np.pi / 4, np.pi / 2, -np.pi / 2]:
            g_rotacionada = rotacionar_imagem(g, theta)
            marcar_falhas(g_rotacionada, self.k)
            g = rotacionar_imagem(g_rotacionada, -theta)

        # Converte matriz g para imagem
        return Image.fromarray(g * 255)