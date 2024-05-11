from tkinter import Canvas, filedialog, Menu, messagebox, NW, Tk
from PIL import Image, ImageTk
import cv2
import numpy

ARQUIVO_PADRAO = ".png"
ARQUIVOS_SUPORTADOS = [("PNG", "*.png"), ("JPG", "*.jpg"), ("JPEG", "*.jpeg"), ("BMP", "*.bmp"), ("Todos os arquivos", "*.*")]

class App:
    def __init__(self, raiz):
        self.imagem_original = None
        self.imagem_processada = None
        self.imagem_final = None

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
        self.menu_de_ferramentas.add_command(label="Aplicar algoritmo regional", command=self.fechar_aplicativo)
        self.menu_de_ferramentas.add_command(label="Aplicar algoritmo global", command=self.fechar_aplicativo)
        self.barra_de_menu.add_cascade(label="Ferramentas", menu=self.menu_de_ferramentas)

        self.raiz.config(menu=self.barra_de_menu)

        # Exibição da imagem
        self.canvas = Canvas(self.raiz, width=800, height=600)
        self.canvas.pack(padx=10, pady=10)

    def abrir_imagem(self):
        caminho = filedialog.askopenfilename(defaultextension=ARQUIVO_PADRAO, filetypes=ARQUIVOS_SUPORTADOS)
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
        
        caminho = filedialog.asksaveasfilename(defaultextension=ARQUIVO_PADRAO, filetypes=ARQUIVOS_SUPORTADOS)
        if caminho:
            imagem.save(caminho)
            messagebox.showinfo("Salvo", "Imagem salva com sucesso.")
    
    def fechar_aplicativo(self):
        self.raiz.quit()
    
    def configurar_canny(self):
        
        if self.imagem_original:
            self.aplicar_canny()
    
    def aplicar_canny(self):
        if self.imagem_original:
            # Converte para tons de cinza
            imagem_monocromatica = cv2.cvtColor(numpy.array(self.imagem_original), cv2.COLOR_RGB2GRAY)
            # Aplica algoritmo de Canny
            imagem_monocromatica = cv2.Canny(imagem_monocromatica, 100, 200)

            self.imagem_processada = Image.fromarray(imagem_monocromatica)

            if self.imagem_final:
                pass
            else:
                self.mostrar_imagem()
        else:
            messagebox.showerror("Erro", "Nenhuma imagem carregada para modificar.")

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
