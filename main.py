import customtkinter as ctk
import database
from views.auth import SplashFrame

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AppJuridico(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("LexGen Studio - IA Jurídica")
        self.geometry("1150x800")
        
        # Inicia banco e estado do usuário
        database.criar_tabelas()
        self.usuario_logado = None
        
        # Chama o roteador para a primeira tela
        self.trocar_tela(SplashFrame)

    def trocar_tela(self, frame_class):
        """Destrói a tela atual e renderiza a nova (Splash -> Login -> Dashboard)"""
        for widget in self.winfo_children():
            widget.destroy()
            
        tela_nova = frame_class(self)
        tela_nova.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = AppJuridico()
    app.mainloop()