import customtkinter as ctk
import database
from views.ferramentas import ConfigFrame, UpgradeFrame, PeticaoFrame, ProcuracaoFrame, IaMagicaFrame, LeitorContratosFrame

LIMITE_IA_BASIC = 5

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.app = master
        self.app.usuario_logado = database.obter_usuario(self.app.usuario_logado['email'])

        # Tecla de atalho global Ctrl+V
        self.app.bind('<Control-v>', self.evento_colar_teclado)

        self.montar_sidebar()

        # Área de Conteúdo (onde as telas injetam)
        self.main_content = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        self.mostrar_tela(ConfigFrame)

    def mostrar_tela(self, frame_class, **kwargs):
        """Limpa o lado direito e injeta a nova ferramenta"""
        for widget in self.main_content.winfo_children():
            widget.destroy()
        tela = frame_class(self.main_content, dashboard=self, **kwargs)
        tela.pack(fill="both", expand=True)

    def montar_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")

        ctk.CTkLabel(self.sidebar, text="LexGen Studio", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20, 5), padx=20)

        cor_plano = "#FFD700" if self.app.usuario_logado['plano'] == 'pro' else "gray"
        texto_plano = f"Plano: {self.app.usuario_logado['plano'].upper()}"
        ctk.CTkLabel(self.sidebar, text=texto_plano, font=ctk.CTkFont(size=12, weight="bold"), text_color=cor_plano).pack(pady=(0, 20))

        ctk.CTkButton(self.sidebar, text="⚙️ Configurações", fg_color="transparent", border_width=1, command=lambda: self.mostrar_tela(ConfigFrame)).pack(pady=5, padx=20)

        ctk.CTkLabel(self.sidebar, text="CRIAÇÃO MANUAL", text_color="gray").pack(pady=(15, 0), padx=20, anchor="w")
        
        self.combo_pecas = ctk.CTkOptionMenu(self.sidebar, values=["Nova Peça...", "Petição Inicial", "Contestação", "Réplica"], command=self.abrir_peticao)
        self.combo_pecas.pack(pady=5, padx=20)

        self.combo_procuracoes = ctk.CTkOptionMenu(self.sidebar, values=["Nova Procuração...", "Ad Judicia", "Previdenciária"], command=self.abrir_procuracao)
        self.combo_procuracoes.pack(pady=5, padx=20)

        ctk.CTkLabel(self.sidebar, text="INTELIGÊNCIA ARTIFICIAL", text_color="gray").pack(pady=(20, 0), padx=20, anchor="w")

        ctk.CTkButton(self.sidebar, text="✨ Redação Mágica", fg_color="#8A2BE2", hover_color="#5D3FD3", command=lambda: self.mostrar_tela(IaMagicaFrame)).pack(pady=5, padx=20)
        ctk.CTkButton(self.sidebar, text="🔍 Leitor de Contratos", fg_color="#D2691E", hover_color="#BA55D3", command=lambda: self.mostrar_tela(LeitorContratosFrame)).pack(pady=5, padx=20)

        if self.app.usuario_logado['plano'] == 'basic':
            self.lbl_uso_ia = ctk.CTkLabel(self.sidebar, text=f"Uso IA: {self.app.usuario_logado['usos_ia']}/{LIMITE_IA_BASIC}", text_color="orange")
            self.lbl_uso_ia.pack(pady=(30, 0))
            ctk.CTkButton(self.sidebar, text="⭐ Seja PRO Ilimitado", fg_color="#FFD700", text_color="black", hover_color="#DAA520", command=lambda: self.mostrar_tela(UpgradeFrame)).pack(pady=5, padx=20)
        else:
            ctk.CTkLabel(self.sidebar, text="Uso IA: Ilimitado", text_color="green").pack(pady=(30, 0))

    def abrir_peticao(self, tipo):
        if tipo != "Nova Peça...":
            self.combo_procuracoes.set("Nova Procuração...")
            self.mostrar_tela(PeticaoFrame, tipo=tipo)

    def abrir_procuracao(self, tipo):
        if tipo != "Nova Procuração...":
            self.combo_pecas.set("Nova Peça...")
            self.mostrar_tela(ProcuracaoFrame, tipo=tipo)

    def evento_colar_teclado(self, event):
        for widget in self.main_content.winfo_children():
            if hasattr(widget, 'colar_print'):
                widget.colar_print()

    def tem_cota_ia(self):
        user = database.obter_usuario(self.app.usuario_logado['email'])
        if user['plano'] == 'pro': return True
        return user['usos_ia'] < LIMITE_IA_BASIC

    def consumir_cota_ia(self):
        if self.app.usuario_logado['plano'] == 'basic':
            database.registrar_uso_ia(self.app.usuario_logado['email'])
            self.app.usuario_logado = database.obter_usuario(self.app.usuario_logado['email'])
            if hasattr(self, 'lbl_uso_ia'):
                self.lbl_uso_ia.configure(text=f"Uso IA: {self.app.usuario_logado['usos_ia']}/{LIMITE_IA_BASIC}")