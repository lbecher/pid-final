from tkinter import Canvas, filedialog, Menu, messagebox, NW, Tk
from PIL import Image, ImageTk

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor de Imagem")

        self.image = None
        self.image_path = ""

        # Criação da barra de menu
        self.menu_bar = Menu(self.root)
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Abrir...", command=self.open_image)
        self.file_menu.add_command(label="Salvar", command=self.save_image)
        self.file_menu.add_command(label="Salvar como...", command=self.save_image_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Fechar", command=self.close_app)
        self.menu_bar.add_cascade(label="Arquivo", menu=self.file_menu)

        self.root.config(menu=self.menu_bar)

        # Exibição da imagem
        self.canvas = Canvas(self.root, width=800, height=600)
        self.canvas.pack(padx=10, pady=10)
    
    def close_app(self):
        self.root.quit()

    def open_image(self):
        file_path = filedialog.askopenfilename(defaultextension=".png", filetypes=[("PNG", "*.png"),
                                                                                         ("JPEG", "*.jpg"),
                                                                                         ("Todos os arquivos", "*.*")])
        if file_path:
            self.image_path = file_path
            self.image = Image.open(file_path)
            self.display_image()

    def display_image(self):
        if self.image:
            self.canvas.delete("all")  # Limpa o canvas
            image_width, image_height = self.image.size
            max_size = 800
            if image_width > max_size or image_height > max_size:
                ratio = min(max_size / image_width, max_size / image_height)
                image_width = int(image_width * ratio)
                image_height = int(image_height * ratio)
                self.image = self.image.resize((image_width, image_height))
            self.photo = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, anchor=NW, image=self.photo)
        else:
            messagebox.showerror("Erro", "Nenhuma imagem carregada.")

    def save_image(self):
        if self.image_path:
            self.image.save(self.image_path)
            messagebox.showinfo("Salvo", "Imagem salva com sucesso.")
        else:
            messagebox.showerror("Erro", "Nenhuma imagem carregada para salvar.")

    def save_image_as(self):
        if self.image:
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"),
                                                                                         ("JPEG", "*.jpg"),
                                                                                         ("Todos os arquivos", "*.*")])
            if file_path:
                self.image.save(file_path)
                messagebox.showinfo("Salvo", "Imagem salva com sucesso.")
        else:
            messagebox.showerror("Erro", "Nenhuma imagem carregada para salvar.")

if __name__ == "__main__":
    root = Tk()
    app = App(root)
    root.mainloop()
