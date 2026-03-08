import customtkinter as ctk
import database

class SplashFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.app = master
        
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame, text="LEXGEN", font=ctk.CTkFont(size=60, weight="bold", family="Arial")).pack()
        ctk.CTkLabel(frame, text="S  T  U  D  I  O", font=ctk.CTkFont(size=30), text_color="#8A2BE2").pack(pady=(0, 30))
        ctk.CTkLabel(frame, text="Carregando IA Jurídica...", font=ctk.CTkFont(size=14), text_color="gray").pack()
        
        self.after(2500, self.ir_para_login)

    def ir_para_login(self):
        self.app.trocar_tela(LoginFrame)


class LoginFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        self.app = master
        
        frame = ctk.CTkFrame(self, width=400, corner_radius=15)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(frame, text="Acesso ao Sistema", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(30, 20), padx=40)

        self.entry_email = ctk.CTkEntry(frame, placeholder_text="E-mail", width=300)
        self.entry_email.pack(pady=10)
        self.entry_email.focus() # Foco automático no e-mail!

        self.entry_senha = ctk.CTkEntry(frame, placeholder_text="Senha", width=300, show="*")
        self.entry_senha.pack(pady=10)

        self.lbl_status = ctk.CTkLabel(frame, text="")
        self.lbl_status.pack()

        ctk.CTkButton(frame, text="Entrar", width=300, height=40, font=ctk.CTkFont(weight="bold"), command=self.efetuar_login).pack(pady=(10, 10))
        ctk.CTkButton(frame, text="Criar Conta Grátis", width=300, height=40, fg_color="transparent", border_width=1, command=self.efetuar_cadastro).pack(pady=(0, 30))

    def efetuar_login(self):
        user = database.autenticar_usuario(self.entry_email.get(), self.entry_senha.get())
        if user:
            self.app.usuario_logado = user
            from views.dashboard import DashboardFrame
            self.app.trocar_tela(DashboardFrame)
        else:
            self.lbl_status.configure(text="❌ E-mail ou senha incorretos!", text_color="red")

    def efetuar_cadastro(self):
        email = self.entry_email.get()
        senha = self.entry_senha.get()
        if not email or not senha:
            return self.lbl_status.configure(text="⚠️ Preencha todos os campos!", text_color="red")
            
        sucesso, msg = database.registrar_usuario(email, senha)
        if sucesso:
            self.lbl_status.configure(text="✅ Conta criada! Faça o login.", text_color="green")
        else:
            self.lbl_status.configure(text=msg, text_color="red")