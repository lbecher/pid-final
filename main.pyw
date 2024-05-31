from tkinter import Button, Canvas, Checkbutton, filedialog, Label, Menu, messagebox, NW, Scale, Tk, Toplevel
from PIL import Image, ImageTk
import cv2
import numpy as np

from processamento_global import ProcessamentoGlobal
from processamento_regional import ProcessamentoRegional
from processamento_local import ProcessamentoLocal

class App:
    def __init__(self, raiz):
        # Parâmetros iniciais
        self.caminho = None
        self.imagem_original = None
        self.imagem_deteccao_de_bordas = None
        self.imagem_bordas_corrigidas = None

        self.canny_usar_gaussiano = False
        self.canny_min = 100
        self.canny_max = 200

        self.processamento_local = ProcessamentoLocal()
        self.processamento_regional = ProcessamentoRegional(15)
        self.processamento_global = ProcessamentoGlobal(180, 100)

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
        self.menu_de_configuracao.add_command(label="Configurar Processamento Local...", command=self.configurar_processamento_local)
        self.menu_de_configuracao.add_command(label="Configurar Processamento Regional...", command=self.configurar_processamento_regional)
        self.menu_de_configuracao.add_command(label="Configurar Processamento Global...", command=self.configurar_processamento_global)
        self.barra_de_menu.add_cascade(label="Configurações", menu=self.menu_de_configuracao)

        self.menu_de_ferramentas = Menu(self.barra_de_menu, tearoff=0)
        self.menu_de_ferramentas.add_command(label="Aplicar Canny", command=self.aplicar_canny)
        self.menu_de_ferramentas.add_separator()
        self.menu_de_ferramentas.add_command(label="Aplicar Processamento Local", command=self.aplicar_processamento_local)
        self.menu_de_ferramentas.add_command(label="Aplicar Processamento Regional", command=self.aplicar_processamento_regional)
        self.menu_de_ferramentas.add_command(label="Aplicar Processamento Global", command=self.aplicar_processamento_global)
        self.barra_de_menu.add_cascade(label="Ferramentas", menu=self.menu_de_ferramentas)

        self.raiz.config(menu=self.barra_de_menu)

        # Exibição da imagem
        self.canvas = Canvas(self.raiz, width=800, height=600)
        self.canvas.pack(padx=10, pady=10)

    def abrir_imagem(self):
        self.caminho = filedialog.askopenfilename(defaultextension=".png", filetypes=[("Imagens", "*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff"), ("Todos os arquivos", "*.*")])
        if self.caminho:
            # Abre a imagem
            self.imagem_original = Image.open(self.caminho)

            self.imagem_deteccao_de_bordas = None
            self.imagem_bordas_corrigidas = None

            self.mostrar_imagem()

    def exportar_imagem(self):
        imagem = None

        if self.imagem_bordas_corrigidas:
            imagem = self.imagem_bordas_corrigidas
        elif self.imagem_deteccao_de_bordas is not None:
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

        # Checkbox para usar o filtro Gaussiano
        def modificar_canny_usar_gaussiano():
            self.canny_usar_gaussiano = not self.canny_usar_gaussiano

        usar_gaussiano = 0
        if self.canny_usar_gaussiano:
            usar_gaussiano = 1
        checkbox_usar_gaussiano = Checkbutton(janela, text="Usar filtro Gaussiano", variable=usar_gaussiano, onvalue=1, offvalue=0, command=modificar_canny_usar_gaussiano)
        checkbox_usar_gaussiano.pack(pady=10)

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
            aplicar()
            janela.destroy()

        btn_aplicar = Button(janela, text="Aplicar", command=aplicar)
        btn_aplicar.pack(pady=10)

        btn_ok = Button(janela, text="Ok", command=ok)
        btn_ok.pack(pady=10)
    
    def configurar_processamento_local(self):
        # Criar uma nova janela para configurar os parâmetros do processamento local
        janela = Toplevel(self.raiz)
        janela.title("Configuração do Processamento Local")

        # Label e controle deslizante para k
        label_k = Label(janela, text="K:")
        label_k.pack(pady=(10, 5))

        scale_k = Scale(janela, from_=0, to=20, resolution=1, orient="horizontal", length=300)
        scale_k.set(self.processamento_local.get_k())
        scale_k.pack(pady=5)

        # Label e controle deslizante para a faixa
        label_faixa = Label(janela, text="Faixa:")
        label_faixa.pack(pady=(10, 5))

        scale_faixa = Scale(janela, from_=0, to=45, resolution=1, orient="horizontal", length=300)
        scale_faixa.set(self.processamento_local.get_faixa())
        scale_faixa.pack(pady=5)

        # Label e controle deslizante para o limiar
        label_limiar = Label(janela, text="Limiar:")
        label_limiar.pack(pady=(10, 5))

        scale_limiar = Scale(janela, from_=0, to=1000, orient="horizontal", length=300)
        scale_limiar.set(self.processamento_local.get_limiar())
        scale_limiar.pack(pady=5)

        # Checkbox para usar todos os ângulos
        def modificar_todos_os_angulos():
            todos_os_angulos = self.processamento_local.get_todos_os_angulos()
            self.processamento_local.set_todos_os_angulos(not todos_os_angulos)

        todos_os_angulos = 0
        if self.processamento_local.get_todos_os_angulos():
            todos_os_angulos = 1
        checkbox_todos_os_angulos = Checkbutton(janela, text="Usar todos os ângulos", variable=todos_os_angulos, onvalue=1, offvalue=0, command=modificar_todos_os_angulos)
        checkbox_todos_os_angulos.pack(pady=10)

        # Label e controle deslizante para o ângulo
        label_angulo = Label(janela, text="Ângulo:")
        label_angulo.pack(pady=(10, 5))

        scale_angulo = Scale(janela, from_=0, to=180, resolution=45, orient="horizontal", length=300)
        scale_angulo.set(self.processamento_local.get_angulo())
        scale_angulo.pack(pady=5)
        
        def aplicar():
            self.processamento_local.set_faixa(scale_faixa.get())
            self.processamento_local.set_limiar(scale_limiar.get())
            self.processamento_local.set_angulo(scale_angulo.get())
            self.processamento_local.set_k(scale_k.get())
            if self.imagem_original:
                self.aplicar_processamento_local()
        
        def ok():
            aplicar()
            janela.destroy()

        btn_aplicar = Button(janela, text="Aplicar", command=aplicar)
        btn_aplicar.pack(pady=10)

        btn_ok = Button(janela, text="Ok", command=ok)
        btn_ok.pack(pady=10)
    
    def configurar_processamento_regional(self):
        # Criar uma nova janela para configurar os parâmetros do processamento local
        janela = Toplevel(self.raiz)
        janela.title("Configuração do Processamento regional")

        # Label e controle deslizante para t positivo
        label_t = Label(janela, text="Limiar:")
        label_t.pack(pady=(10, 5))

        scale_t = Scale(janela, from_=0, to=1000, orient="horizontal", length=300)
        scale_t.set(self.processamento_regional.get_t())
        scale_t.pack(pady=5)
        
        def aplicar():
            self.processamento_regional.set_t(scale_t.get())
            if self.imagem_deteccao_de_bordas is not None:
                self.aplicar_processamento_regional()
        
        def ok():
            aplicar()
            janela.destroy()

        btn_aplicar = Button(janela, text="Aplicar", command=aplicar)
        btn_aplicar.pack(pady=10)

        btn_ok = Button(janela, text="Ok", command=ok)
        btn_ok.pack(pady=10)
    
    def configurar_processamento_global(self):
        # Criar uma nova janela para configurar os parâmetros do processamento local
        janela = Toplevel(self.raiz)
        janela.title("Configuração do Processamento Global")

        # Label e controle deslizante para limiar positivo
        label_limiar = Label(janela, text="Limiar:")
        label_limiar.pack(pady=(10, 5))

        scale_limiar = Scale(janela, from_=0, to=1000, orient="horizontal", length=300)
        scale_limiar.set(self.processamento_global.get_limiar())
        scale_limiar.pack(pady=5)

        # Label e controle deslizante para quantidade de ângulos
        label_theta_intervalo = Label(janela, text="Intervalo de Theta:")
        label_theta_intervalo.pack(pady=(10, 5))

        scale_theta_intervalo = Scale(janela, from_=1, to=180, orient="horizontal", length=300)
        scale_theta_intervalo.set(self.processamento_global.get_theta_intervalo())
        scale_theta_intervalo.pack(pady=5)
        
        def aplicar():
            self.processamento_global.set_limiar(scale_limiar.get())
            self.processamento_global.set_theta_intervalo(scale_theta_intervalo.get())
            if self.imagem_deteccao_de_bordas is not None:
                self.aplicar_processamento_global()
        
        def ok():
            aplicar()
            janela.destroy()

        btn_aplicar = Button(janela, text="Aplicar", command=aplicar)
        btn_aplicar.pack(pady=10)

        btn_ok = Button(janela, text="Ok", command=ok)
        btn_ok.pack(pady=10)
    
    def configurar_processamento_regional(self):
        # Criar uma nova janela para configurar os parâmetros do processamento local
        janela = Toplevel(self.raiz)
        janela.title("Configuração do Processamento Regional")

        # Label e controle deslizante para t positivo
        label_t = Label(janela, text="Limiar:")
        label_t.pack(pady=(10, 5))

        scale_t = Scale(janela, from_=0, to=1000, orient="horizontal", length=300)
        scale_t.set(self.processamento_regional.get_t())
        scale_t.pack(pady=5)
        
        def aplicar():
            self.processamento_regional.set_t(scale_t.get())
            self.aplicar_processamento_regional()
        
        def ok():
            aplicar()
            janela.destroy()

        btn_aplicar = Button(janela, text="Aplicar", command=aplicar)
        btn_aplicar.pack(pady=10)

        btn_ok = Button(janela, text="Ok", command=ok)
        btn_ok.pack(pady=10)
    
    def aplicar_canny(self):
        if self.imagem_original:
            # Converte para tons de cinza
            imagem_monocromatica = cv2.cvtColor(np.array(self.imagem_original), cv2.COLOR_RGB2GRAY)

            # Suavizar imagem com filtro Gaussiano
            if self.canny_usar_gaussiano:
                imagem_monocromatica = cv2.GaussianBlur(imagem_monocromatica, (15, 15), 0)

            # Aplica algoritmo de Canny
            self.imagem_deteccao_de_bordas = cv2.Canny(imagem_monocromatica, self.canny_min, self.canny_max)

            self.imagem_bordas_corrigidas = None
            self.mostrar_imagem()
        else:
            messagebox.showerror("Erro", "Nenhuma imagem carregada para modificar.")
    
    def aplicar_processamento_local(self):
        if self.imagem_original:
            self.imagem_bordas_corrigidas = self.processamento_local.processar(self.imagem_original)
            self.mostrar_imagem()
        else:
            messagebox.showerror("Erro", "Nenhuma imagem carregada para modificar.")
    
    def aplicar_processamento_regional(self):
        if self.caminho is not None:
            self.imagem_bordas_corrigidas = self.processamento_regional.processar(self.caminho)
            self.mostrar_imagem()
        else:
            messagebox.showerror("Erro", "Nenhuma imagem carregada para modificar.")
    
    def aplicar_processamento_global(self):
        if self.imagem_deteccao_de_bordas is not None:
            self.imagem_bordas_corrigidas = self.processamento_global.processar(self.imagem_deteccao_de_bordas)
            self.mostrar_imagem()
        else:
            messagebox.showerror("Erro", "Aplique Canny em uma imagem para usar o Processamento Global.")

    def mostrar_imagem(self):
        imagem = None

        if self.imagem_bordas_corrigidas:
            imagem = self.imagem_bordas_corrigidas
        elif self.imagem_deteccao_de_bordas is not None:
            imagem = Image.fromarray(self.imagem_deteccao_de_bordas)
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
