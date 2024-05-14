from tkinter import Button, Canvas, filedialog, Label, Menu, messagebox, NW, Scale, Tk, Toplevel
from PIL import Image, ImageTk
import cv2
import numpy as np

from local import ProcessamentoLocal

class App:
    def __init__(self, raiz):
        # Parâmetros iniciais
        self.imagem_original = None
        self.imagem_deteccao_de_bordas = None
        self.imagem_bordas_corrigidas = None

        self.canny_min = 100
        self.canny_max = 200

        self.processamento_local = ProcessamentoLocal(100, 2)

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
        self.menu_de_configuracao.add_command(label="Configurar Processamento Local", command=self.configurar_processamento_local)
        self.barra_de_menu.add_cascade(label="Configurações", menu=self.menu_de_configuracao)

        self.menu_de_ferramentas = Menu(self.barra_de_menu, tearoff=0)
        self.menu_de_ferramentas.add_command(label="Aplicar Canny", command=self.aplicar_canny)
        self.menu_de_ferramentas.add_separator()
        self.menu_de_ferramentas.add_command(label="Aplicar algoritmo local", command=self.aplicar_processamento_local)
        self.menu_de_ferramentas.add_command(label="Aplicar algoritmo regional", command=self.fechar_aplicativo)
        self.menu_de_ferramentas.add_command(label="Aplicar algori5tmo global", command=self.fechar_aplicativo)
        self.barra_de_menu.add_cascade(label="Ferramentas", menu=self.menu_de_ferramentas)

        self.raiz.config(menu=self.barra_de_menu)

        # Exibição da imagem
        self.canvas = Canvas(self.raiz, width=800, height=600)
        self.canvas.pack(padx=10, pady=10)

    def abrir_imagem(self):
        caminho = filedialog.askopenfilename(defaultextension=".png", filetypes=[("Imagens", "*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff"), ("Todos os arquivos", "*.*")])
        if caminho:
            # Abre a imagem
            self.imagem_original = Image.open(caminho)

            self.imagem_deteccao_de_bordas = None
            self.imagem_bordas_corrigidas = None

            self.mostrar_imagem()

    def exportar_imagem(self):
        imagem = None

        if self.imagem_bordas_corrigidas:
            imagem = self.imagem_bordas_corrigidas
        elif self.imagem_deteccao_de_bordas:
            imagem = self.imagem_deteccao_de_bordas
        elif self.imagem_original:
            imagem = self.imagem_original
        else:
            messagebox.showerror("Erro", "Nenhuma imagem carregada para exportar.")
            return
        
        caminho = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if caminho:
            imagem.save(caminho)
            messagebox.showinfo("Salvo", "Imagem salva com sucesso.")
    
    def fechar_aplicativo(self):
        self.raiz.quit()
    
    def configurar_canny(self):
        # Criar uma nova janela para configurar os parâmetros do Canny
        janela = Toplevel(self.raiz)
        janela.title("Configuração do Canny")
        janela.geometry('200x400')

        # Label e controle deslizante para limiar mínimo
        label_limiar_min = Label(janela, text="Limiar mínimo:")
        label_limiar_min.pack(pady=(10, 5))

        scale_limiar_min = Scale(janela, from_=0, to=255, orient="horizontal", length=300)
        scale_limiar_min.set(self.canny_min)
        scale_limiar_min.pack(pady=5)

        # Label e controle deslizante para limiar máximo
        label_limiar_max = Label(janela, text="Limiar máximo:")
        label_limiar_max.pack(pady=(10, 5))

        scale_limiar_max = Scale(janela, from_=0, to=255, orient="horizontal", length=300)
        scale_limiar_max.set(self.canny_max)
        scale_limiar_max.pack(pady=5)
        
        def aplicar():
            self.canny_min = scale_limiar_min.get()
            self.canny_max = scale_limiar_max.get()
            if self.imagem_original:
                self.aplicar_canny()
        
        def ok():
            self.canny_min = scale_limiar_min.get()
            self.canny_max = scale_limiar_max.get()
            if self.imagem_original:
                self.aplicar_canny()
            janela.destroy()

        btn_aplicar = Button(janela, text="Aplicar", command=aplicar)
        btn_aplicar.pack(pady=10)

        btn_ok = Button(janela, text="Ok", command=ok)
        btn_ok.pack(pady=10)
    
    def configurar_processamento_local(self):
        # Criar uma nova janela para configurar os parâmetros do processamento local
        janela = Toplevel(self.raiz)
        janela.title("Configuração do Processamento Local")

        # Label e controle deslizante para limiar positivo
        label_limiar_positivo = Label(janela, text="Limiar positivo:")
        label_limiar_positivo.pack(pady=(10, 5))

        scale_limiar_positivo = Scale(janela, from_=0, to=1000, orient="horizontal", length=300)
        scale_limiar_positivo.set(self.processamento_local.get_tm())
        scale_limiar_positivo.pack(pady=5)

        # Label e controle deslizante para quantidade de ângulos
        label_quantidade_de_angulos = Label(janela, text="Quantidade de ângulos:")
        label_quantidade_de_angulos.pack(pady=(10, 5))

        scale_quantidade_de_angulos = Scale(janela, from_=0, to=15, orient="horizontal", length=300)
        scale_quantidade_de_angulos.set(self.processamento_local.get_ac())
        scale_quantidade_de_angulos.pack(pady=5)
        
        def aplicar():
            self.processamento_local.set_tm(scale_limiar_positivo.get())
            self.processamento_local.set_ac(scale_quantidade_de_angulos.get())
            if self.imagem_original:
                self.aplicar_processamento_local()
        
        def ok():
            self.processamento_local.set_tm(scale_limiar_positivo.get())
            self.processamento_local.set_ac(scale_quantidade_de_angulos.get())
            if self.imagem_original:
                self.aplicar_processamento_local()
            janela.destroy()

        btn_aplicar = Button(janela, text="Aplicar", command=aplicar)
        btn_aplicar.pack(pady=10)

        btn_ok = Button(janela, text="Ok", command=ok)
        btn_ok.pack(pady=10)
    
    def aplicar_canny(self):
        if self.imagem_original:
            # Converte para tons de cinza
            imagem_monocromatica = cv2.cvtColor(np.array(self.imagem_original), cv2.COLOR_RGB2GRAY)
            # Aplica algoritmo de Canny
            imagem_canny = cv2.Canny(imagem_monocromatica, self.canny_min, self.canny_max)

            self.imagem_deteccao_de_bordas = Image.fromarray(imagem_canny)

            if self.imagem_bordas_corrigidas:
                pass
            else:
                self.mostrar_imagem()
        else:
            messagebox.showerror("Erro", "Nenhuma imagem carregada para modificar.")
    
    def aplicar_processamento_local(self):
        if self.imagem_original:
            self.imagem_bordas_corrigidas = self.processamento_local.processar(self.imagem_original)
            self.mostrar_imagem()
        else:
            messagebox.showerror("Erro", "Nenhuma imagem carregada para modificar.")

    def mostrar_imagem(self):
        imagem = None

        if self.imagem_bordas_corrigidas:
            imagem = self.imagem_bordas_corrigidas
        elif self.imagem_deteccao_de_bordas:
            imagem = self.imagem_deteccao_de_bordas
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
