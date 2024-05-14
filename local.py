from PIL import Image
import cv2
import numpy as np

class ProcessamentoLocal():
    def __init__(self, tm, ac):
        self.tm = tm # Quantidade de ângulos
        self.ac = ac # Número de ângulos
        self.ta = (np.pi * 2) / ac # Limiar de ângulo positivo

    def set_ac(self, ac):
        self.ac = ac # Quantidade de ângulos
        self.ta = (np.pi * 2) / ac # Limiar de ângulo positivo
    
    def set_tm(self, tm):
        self.tm = tm # Limiar positivo
    
    def get_ac(self):
        return self.ac
    
    def get_tm(self):
        return self.tm

    def processar(self, imagem):
        # Converte imagem para matriz em tons de cinza
        f = cv2.cvtColor(np.array(imagem), cv2.COLOR_RGB2GRAY)

        # Calcula as matrizes M(x,y) e alpha(x,y)
        x = cv2.Sobel(f, cv2.CV_64F, 1, 0, ksize=3)
        y = cv2.Sobel(f, cv2.CV_64F, 0, 1, ksize=3)

        m = np.sqrt(x**2 + y**2)
        alpha = np.arctan2(x, y)

        # Aplica os limites
        g = np.zeros(f.shape, dtype=np.uint8)
        angulo = -np.pi
        for _ in range(self.ac):
            angulo += self.ta
            g |= (m > self.tm) & (np.abs(alpha) > angulo) # np.abs(alpha)

        # Converte matriz g para imagem
        return Image.fromarray(g * 255)