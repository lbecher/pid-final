from tkinter import Button, Canvas, filedialog, Label, Menu, messagebox, NW, Scale, Tk, Toplevel
from PIL import Image, ImageTk
import cv2
import numpy as np
from skimage import feature
from scipy.spatial import Delaunay
from scipy.interpolate import UnivariateSpline

ARQUIVO_PADRAO = ".png"
ARQUIVOS_SUPORTADOS = [("PNG", "*.png"), ("JPG", "*.jpg"), ("JPEG", "*.jpeg"), ("BMP", "*.bmp"), ("Todos os arquivos", "*.*")]

class App:
    def __init__(self, raiz):
        self.imagem_original = None
        self.imagem_processada = None
        self.imagem_final = None

        self.canny_min = 100
        self.canny_max = 200

        self.raiz = raiz
        self.raiz.title("Ligação de Pontos de Borda")

        # Barra de menu
        self.barra_de_menu = Menu(self.raiz)
        self.menu_de_arquivo = Menu(self.barra_de_menu, tearoff=0)
        self.menu_de_arquivo.add_command(label="Abrir...", command=self.abrir_imagem)
        self.menu_de_arquivo.add_command(label="Exportar...", command=self.exportar_imagem)
        self.menu_de_arquivo.add_separator()
        self.menu_de_arquivo.add_command(label="Fechar", command=self.fechar_aplicativo)
        self.barra_de_menu.add_cascade(label="Arquivo", menu=self.menu_de_arquivo)

        self.menu_de_configuracao = Menu(self.barra_de_menu, tearoff=0)
        self.menu_de_configuracao.add_command(label="Configurar Canny...", command=self.configurar_canny)
        self.menu_de_configuracao.add_separator()
        self.barra_de_menu.add_cascade(label="Configurações", menu=self.menu_de_configuracao)

        self.menu_de_ferramentas = Menu(self.barra_de_menu, tearoff=0)
        self.menu_de_ferramentas.add_command(label="Aplicar Canny", command=self.aplicar_canny)
        self.menu_de_ferramentas.add_separator()
        self.menu_de_ferramentas.add_command(label="Aplicar algoritmo local", command=self.fechar_aplicativo)
        self.menu_de_ferramentas.add_command(label="Aplicar algoritmo regional", command=self.aplicar_algoritmo_regional)
        self.menu_de_ferramentas.add_command(label="Aplicar algoritmo global", command=self.fechar_aplicativo)
        self.barra_de_menu.add_cascade(label="Ferramentas", menu=self.menu_de_ferramentas)

        self.raiz.config(menu=self.barra_de_menu)

        # Exibição da imagem
        self.canvas = Canvas(self.raiz, width=800, height=600)
        self.canvas.pack(padx=10, pady=10)

    def abrir_imagem(self):
        caminho = filedialog.askopenfilename(defaultextension=ARQUIVO_PADRAO, filetypes=[("Imagens", "*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff"), ("Todos os arquivos", "*.*")])
        if caminho:
            self.imagem_original = Image.open(caminho)
            self.imagem_processada = None
            self.imagem_final = None
            self.mostrar_imagem()

    def exportar_imagem(self):
        imagem = None

        if self.imagem_final:
            imagem = self.imagem_final
        elif self.imagem_processada:
            imagem = self.imagem_processada
        elif self.imagem_original:
            imagem = self.imagem_original
        else:
            messagebox.showerror("Erro", "Nenhuma imagem carregada para exportar.")
            return
        
        caminho = filedialog.asksaveasfilename(defaultextension=ARQUIVO_PADRAO, filetypes=[("PNG", "*.png")])
        if caminho:
            imagem.save(caminho)
            messagebox.showinfo("Salvo", "Imagem salva com sucesso.")
    
    def fechar_aplicativo(self):
        self.raiz.quit()
    
    def configurar_canny(self):
        # Criar uma nova janela para configurar os parâmetros do Canny
        configurar_canny_janela = Toplevel(self.raiz)
        configurar_canny_janela.title("Configuração do Canny")

        # Label e controle deslizante para limiar mínimo
        lbl_limiar_min = Label(configurar_canny_janela, text="Limiar mínimo:")
        lbl_limiar_min.pack(pady=(10, 5))

        scale_limiar_min = Scale(configurar_canny_janela, from_=0, to=255, orient="horizontal")
        scale_limiar_min.set(self.canny_min)  # Valor padrão

        scale_limiar_min.pack(pady=5)

        # Label e controle deslizante para limiar máximo
        lbl_limiar_max = Label(configurar_canny_janela, text="Limiar máximo:")
        lbl_limiar_max.pack(pady=(10, 5))

        scale_limiar_max = Scale(configurar_canny_janela, from_=0, to=255, orient="horizontal")
        scale_limiar_max.set(self.canny_max)  # Valor padrão

        scale_limiar_max.pack(pady=5)
        
        def configurar_e_aplicar_canny():
            self.canny_min = scale_limiar_min.get()
            self.canny_max = scale_limiar_max.get()
            if self.imagem_original:
                self.aplicar_canny()
            configurar_canny_janela.destroy()

        btn_aplicar = Button(configurar_canny_janela, text="Aplicar", command=configurar_e_aplicar_canny)
        btn_aplicar.pack(pady=10)
    
    def aplicar_canny(self):
        if self.imagem_original:
            # Converte para tons de cinza
            imagem_monocromatica = cv2.cvtColor(np.array(self.imagem_original), cv2.COLOR_RGB2GRAY)
            # Aplica algoritmo de Canny
            imagem_canny = cv2.Canny(imagem_monocromatica, self.canny_min, self.canny_max)

            self.imagem_processada = Image.fromarray(imagem_canny)

            if self.imagem_final:
                pass
            else:
                self.mostrar_imagem()
        else:
            messagebox.showerror("Erro", "Nenhuma imagem carregada para modificar.")
    
    def aplicar_algoritmo_regional(self):
        if self.imagem_processada:
            # Converte a imagem processada para um array numpy
            imagem_np = np.array(self.imagem_processada)

            # Encontra os contornos na imagem
            contornos, _ = cv2.findContours(imagem_np, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            for contorno in contornos:
                # Aplica a aproximação poligonal iterativa no contorno
                epsilon = 0.05 * cv2.arcLength(contorno, True)
                aprox = cv2.approxPolyDP(contorno, epsilon, True)

                # Desenha o contorno aproximado na imagem
                cv2.drawContours(imagem_np, [aprox], 0, (255), 2)

            # Converte o array numpy de volta para uma imagem PIL e armazena na imagem final
            self.imagem_final = Image.fromarray(imagem_np)

            # Mostra a imagem final
            self.mostrar_imagem()
        else:
            messagebox.showerror("Erro", "Nenhuma imagem processada para aplicar o algoritmo.")    

    def mostrar_imagem(self):
        imagem = None

        if self.imagem_final:
            imagem = self.imagem_final
        elif self.imagem_processada:
            imagem = self.imagem_processada
        elif self.imagem_original:
            imagem = self.imagem_original
        else:
            messagebox.showerror("Erro", "Nenhuma imagem carregada para mostrar.")
            return
        
        width, height = imagem.size
        max = 800
        if width > max or height > max:
            ratio = min(max / width, max / height)
            width = int(width * ratio)
            height = int(height * ratio)
            imagem = imagem.resize((width, height))
        
        self.imagem_de_exibicao = ImageTk.PhotoImage(imagem)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor=NW, image=self.imagem_de_exibicao)

if __name__ == "__main__":
    raiz = Tk()
    app = App(raiz)
    raiz.mainloop()