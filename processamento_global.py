import cv2
import numpy as np
from PIL import Image

class ProcessamentoGlobal:
    def __init__(self, theta_intervalo, limiar, rho_max=None):
        self.theta_intervalo = theta_intervalo
        self.rho_max = rho_max
        self.limiar = limiar
    
    def set_limiar(self, limiar):
        self.limiar = limiar

    def get_limiar(self):
        return self.limiar
    
    def set_theta_intervalo(self, theta_intervalo):
        self.theta_intervalo = theta_intervalo

    def get_theta_intervalo(self):
        return self.theta_intervalo

    def transformada(self, bordas):
        # Determinar rho máximo se não for fornecido
        if self.rho_max is None:
            max_dist = max(np.linalg.norm(ponto) for ponto in bordas)
            self.rho_max = int(np.ceil(max_dist))
        
        # Dimensões da imagem
        height, width = bordas.shape

        # Inicializar o acumulador
        acumulador = np.zeros((2 * self.rho_max, self.theta_intervalo), dtype=np.uint8)

        # Gerar a Transformada de Hough
        for y in range(height):
            for x in range(width):
                if bordas[y, x] > 0:  # Se é um pixel de borda
                # Calcula rho e vota no acumulador para possíveis valores de theta
                    for theta in range(self.theta_intervalo):
                        theta_rad = np.deg2rad(theta)
                        rho = int(x * np.cos(theta_rad) + y * np.sin(theta_rad))
                        acumulador[rho + self.rho_max, theta] += 1

        return acumulador
    
    def processar(self, bordas):
        # Dimensões da imagem
        height, width = bordas.shape

        # Encontrar coordenadas dos pixels de borda na imagem
        pontos = []
        altura, largura = bordas.shape
        for y in range(altura):
            for x in range(largura):
                if bordas[y, x] > 0:  # Se o pixel for uma borda
                    pontos.append((x, y))

        # Calcular a Transformada de Hough para os pontos de borda
        acumulador = self.transformada(bordas)
        
        # Limiariza o acumulador para encontrar os picos significativos
        linhas = []
        for rho in range(acumulador.shape[0]):
            for theta in range(acumulador.shape[1]):
                if acumulador[rho, theta] > self.limiar:
                    # Converte os parâmetros de volta para coordenadas cartesianas
                    a = np.cos(np.deg2rad(theta))
                    b = np.sin(np.deg2rad(theta))
                    x0 = a * (rho - self.rho_max)
                    y0 = b * (rho - self.rho_max)
                    pt1 = (int(x0 + 1000 * (-b)), int(y0 + 1000 * (a)))
                    pt2 = (int(x0 - 1000 * (-b)), int(y0 - 1000 * (a)))
                    linhas.append((pt1, pt2))
        
        # Gera imagem de saída
        saida = np.zeros((height, width, 3), dtype=np.uint8)
        for linha in linhas:
            pt1, pt2 = linha
            cv2.line(saida, pt1, pt2, (255, 255, 255), 2)
            
        return Image.fromarray(saida)
