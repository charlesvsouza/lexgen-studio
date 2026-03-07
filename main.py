import customtkinter as ctk
from tkinter import filedialog
import threading
import os
import tempfile
from dotenv import load_dotenv
from PIL import ImageGrab

import database
import ia
import documentos

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

LIMITE_IA_BASIC = 5

class AppJuridico(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("LexGen Studio - IA Jurídica")
        self.geometry("1150x800")
        database.criar_tabelas()

        self.usuario_logado = None

        # Inicia pela tela de Splash
        self.mostrar_splash()

    def limpar_janela(self):
        """Remove absolutamente tudo da janela principal para trocar de sistema"""
        for widget in self.winfo_children():
            widget.destroy()

    # ==========================================
    # TELA 1: SPLASH (APRESENTAÇÃO)
    # ==========================================
    def mostrar_splash(self):
        self.limpar_janela()
        
        frame_splash = ctk.CTkFrame(self, fg_color="transparent")
        frame_splash.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame_splash, text="LEXGEN", font=ctk.CTkFont(size=60, weight="bold", family="Arial")).pack()
        # CORREÇÃO AQUI: Removido o letterspacing e adicionado os espaços na string manualmente
        ctk.CTkLabel(frame_splash, text="S  T  U  D  I  O", font=ctk.CTkFont(size=30), text_color="#8A2BE2").pack(pady=(0, 30))
        
        ctk.CTkLabel(frame_splash, text="Carregando IA Jurídica...", font=ctk.CTkFont(size=14), text_color="gray").pack()
        
        # Pula para login após 2.5 segundos
        self.after(2500, self.mostrar_login)

    # ==========================================
    # TELA 2: LOGIN E CADASTRO
    # ==========================================
    def mostrar_login(self):
        self.limpar_janela()
        
        frame_login = ctk.CTkFrame(self, width=400, corner_radius=15)
        frame_login.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(frame_login, text="Acesso ao Sistema", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(30, 20), padx=40)

        self.entry_email = ctk.CTkEntry(frame_login, placeholder_text="E-mail", width=300)
        self.entry_email.pack(pady=10)

        self.entry_senha = ctk.CTkEntry(frame_login, placeholder_text="Senha", width=300, show="*")
        self.entry_senha.pack(pady=10)

        self.lbl_status_login = ctk.CTkLabel(frame_login, text="")
        self.lbl_status_login.pack()

        btn_entrar = ctk.CTkButton(frame_login, text="Entrar", width=300, height=40, font=ctk.CTkFont(weight="bold"), command=self.efetuar_login)
        btn_entrar.pack(pady=(10, 10))

        btn_cadastrar = ctk.CTkButton(frame_login, text="Criar Conta Grátis", width=300, height=40, fg_color="transparent", border_width=1, command=self.efetuar_cadastro)
        btn_cadastrar.pack(pady=(0, 30))

    def efetuar_login(self):
        email = self.entry_email.get()
        senha = self.entry_senha.get()
        user = database.autenticar_usuario(email, senha)
        
        if user:
            self.usuario_logado = user
            self.montar_dashboard_principal()
        else:
            self.lbl_status_login.configure(text="❌ E-mail ou senha incorretos!", text_color="red")

    def efetuar_cadastro(self):
        email = self.entry_email.get()
        senha = self.entry_senha.get()
        if not email or not senha:
            return self.lbl_status_login.configure(text="⚠️ Preencha todos os campos!", text_color="red")
            
        sucesso, msg = database.registrar_usuario(email, senha)
        if sucesso:
            self.lbl_status_login.configure(text="✅ Conta criada! Faça o login.", text_color="green")
        else:
            self.lbl_status_login.configure(text=msg, text_color="red")

    # ==========================================
    # TELA 3: DASHBOARD PRINCIPAL (SISTEMA)
    # ==========================================
    def montar_dashboard_principal(self):
        self.limpar_janela()
        self.bind('<Control-v>', self.evento_colar_teclado)

        # Atualiza os dados do usuário para ter certeza do plano
        self.usuario_logado = database.obter_usuario(self.usuario_logado['email'])

        # ============ MENU LATERAL ============
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.pack(side="left", fill="y")

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="LexGen Studio", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.pack(pady=(20, 5), padx=20)

        # Etiqueta do Plano
        cor_plano = "#FFD700" if self.usuario_logado['plano'] == 'pro' else "gray"
        texto_plano = f"Plano: {self.usuario_logado['plano'].upper()}"
        ctk.CTkLabel(self.sidebar_frame, text=texto_plano, font=ctk.CTkFont(size=12, weight="bold"), text_color=cor_plano).pack(pady=(0, 20))

        self.btn_config = ctk.CTkButton(self.sidebar_frame, text="⚙️ Configurações", fg_color="transparent", border_width=1, command=self.mostrar_configuracoes)
        self.btn_config.pack(pady=5, padx=20)

        ctk.CTkLabel(self.sidebar_frame, text="CRIAÇÃO MANUAL", text_color="gray").pack(pady=(15, 0), padx=20, anchor="w")
        
        self.combo_pecas = ctk.CTkOptionMenu(self.sidebar_frame, values=["Nova Peça...", "Petição Inicial", "Contestação", "Réplica"], command=self.mostrar_peticao)
        self.combo_pecas.pack(pady=5, padx=20)

        self.combo_procuracoes = ctk.CTkOptionMenu(self.sidebar_frame, values=["Nova Procuração...", "Ad Judicia", "Previdenciária"], command=self.mostrar_procuracao)
        self.combo_procuracoes.pack(pady=5, padx=20)

        ctk.CTkLabel(self.sidebar_frame, text="INTELIGÊNCIA ARTIFICIAL", text_color="gray").pack(pady=(20, 0), padx=20, anchor="w")

        self.btn_ia = ctk.CTkButton(self.sidebar_frame, text="✨ Redação Mágica", fg_color="#8A2BE2", hover_color="#5D3FD3", command=self.mostrar_ia)
        self.btn_ia.pack(pady=5, padx=20)

        self.btn_analisar = ctk.CTkButton(self.sidebar_frame, text="🔍 Leitor de Contratos", fg_color="#D2691E", hover_color="#BA55D3", command=self.mostrar_analise)
        self.btn_analisar.pack(pady=5, padx=20)

        # Botão de Upgrade se for Basic
        if self.usuario_logado['plano'] == 'basic':
            self.lbl_uso_ia = ctk.CTkLabel(self.sidebar_frame, text=f"Uso IA: {self.usuario_logado['usos_ia']}/{LIMITE_IA_BASIC}", text_color="orange")
            self.lbl_uso_ia.pack(pady=(30, 0))
            self.btn_upgrade = ctk.CTkButton(self.sidebar_frame, text="⭐ Seja PRO Ilimitado", fg_color="#FFD700", text_color="black", hover_color="#DAA520", command=self.mostrar_upgrade)
            self.btn_upgrade.pack(pady=5, padx=20)
        else:
            ctk.CTkLabel(self.sidebar_frame, text="Uso IA: Ilimitado", text_color="green").pack(pady=(30, 0))

        # ============ ÁREA PRINCIPAL ============
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.mostrar_configuracoes()

    def limpar_tela_main(self):
        """Limpa apenas o painel direito (muda de aba)"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    # ==========================================
    # TELA DE UPGRADE PRO
    # ==========================================
    def mostrar_upgrade(self):
        self.limpar_tela_main()
        ctk.CTkLabel(self.main_frame, text="⭐ Atualize para o LexGen PRO", font=ctk.CTkFont(size=30, weight="bold"), text_color="#FFD700").pack(pady=(30, 10))
        
        ctk.CTkLabel(self.main_frame, text="Destrave o poder máximo da Inteligência Artificial no seu escritório.", font=ctk.CTkFont(size=16)).pack(pady=(0, 30))

        frame_planos = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        frame_planos.pack(pady=10)

        # Card PRO
        card_pro = ctk.CTkFrame(frame_planos, width=400, height=300, corner_radius=15, border_width=2, border_color="#FFD700")
        card_pro.pack(padx=20, pady=20)
        card_pro.pack_propagate(False)

        ctk.CTkLabel(card_pro, text="Plano PRO Ilimitado", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        ctk.CTkLabel(card_pro, text="✔️ Redação Mágica Ilimitada\n✔️ Análise de Documentos Ilimitada\n✔️ Suporte Prioritário\n✔️ Novas Funcionalidades Antecipadas", justify="left").pack(pady=10)
        ctk.CTkLabel(card_pro, text="R$ 97,00 / mês", font=ctk.CTkFont(size=24, weight="bold"), text_color="#8A2BE2").pack(pady=20)

        btn_assinar = ctk.CTkButton(card_pro, text="Confirmar Pagamento e Assinar", font=ctk.CTkFont(weight="bold"), fg_color="#FFD700", text_color="black", hover_color="#DAA520", command=self.efetuar_upgrade)
        btn_assinar.pack(pady=10)

    def efetuar_upgrade(self):
        database.atualizar_plano_pro(self.usuario_logado['email'])
        self.montar_dashboard_principal() 

    # ==========================================
    # VERIFICADOR DE COTA DE IA
    # ==========================================
    def tem_cota_ia(self):
        user = database.obter_usuario(self.usuario_logado['email'])
        self.usuario_logado = user
        if user['plano'] == 'pro':
            return True
        if user['usos_ia'] >= LIMITE_IA_BASIC:
            return False
        return True

    def consumir_cota_ia(self):
        if self.usuario_logado['plano'] == 'basic':
            database.registrar_uso_ia(self.usuario_logado['email'])
            self.usuario_logado = database.obter_usuario(self.usuario_logado['email'])
            if hasattr(self, 'lbl_uso_ia'):
                self.lbl_uso_ia.configure(text=f"Uso IA: {self.usuario_logado['usos_ia']}/{LIMITE_IA_BASIC}")

    # ==========================================
    # TELAS ORIGINAIS ADAPTADAS
    # ==========================================
    def mostrar_configuracoes(self):
        self.limpar_tela_main()
        ctk.CTkLabel(self.main_frame, text="Configurações do Escritório", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(10, 20))
        
        self.entry_escritorio = ctk.CTkEntry(self.main_frame, placeholder_text="Nome do Escritório", width=400)
        self.entry_escritorio.pack(pady=10)
        self.entry_advogado = ctk.CTkEntry(self.main_frame, placeholder_text="Nome do Advogado", width=400)
        self.entry_advogado.pack(pady=10)
        self.entry_oab = ctk.CTkEntry(self.main_frame, placeholder_text="Número da OAB", width=400)
        self.entry_oab.pack(pady=10)

        ctk.CTkLabel(self.main_frame, text="Pasta Padrão de Salvamento").pack(pady=(10, 0))
        frame_pasta = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        frame_pasta.pack(pady=5)
        
        self.entry_pasta = ctk.CTkEntry(frame_pasta, width=300)
        self.entry_pasta.pack(side="left", padx=5)
        
        btn_selecionar = ctk.CTkButton(frame_pasta, text="Procurar", width=80, command=self.selecionar_pasta)
        btn_selecionar.pack(side="left")
        
        self.lbl_status_config = ctk.CTkLabel(self.main_frame, text="")
        self.lbl_status_config.pack(pady=10)
        
        ctk.CTkButton(self.main_frame, text="Salvar Configurações", command=self.salvar_configuracoes).pack(pady=20)

        config = database.carregar_configuracoes()
        if config:
            self.entry_escritorio.insert(0, config[0] if config[0] else "")
            self.entry_advogado.insert(0, config[1] if config[1] else "")
            self.entry_oab.insert(0, config[2] if config[2] else "")
            self.entry_pasta.insert(0, config[3] if len(config) > 3 and config[3] else "")

    def selecionar_pasta(self):
        pasta = ctk.filedialog.askdirectory()
        if pasta:
            self.entry_pasta.delete(0, 'end')
            self.entry_pasta.insert(0, pasta)

    def salvar_configuracoes(self):
        if not self.entry_escritorio.get() or not self.entry_advogado.get():
            return self.lbl_status_config.configure(text="⚠️ Preencha os campos!", text_color="red")
        database.salvar_configuracoes(self.entry_escritorio.get(), self.entry_advogado.get(), self.entry_oab.get(), self.entry_pasta.get())
        self.lbl_status_config.configure(text="✅ Salvo com sucesso.", text_color="green")

    def mostrar_peticao(self, tipo):
        if tipo == "Nova Peça...": return
        self.combo_procuracoes.set("Nova Procuração...") 
        self.limpar_tela_main()

        scroll = ctk.CTkScrollableFrame(self.main_frame, width=800, height=600, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(scroll, text=f"Documento: {tipo}", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(10, 20))

        self.entry_autor = ctk.CTkEntry(scroll, placeholder_text="Nome do Autor/Requerente", width=500)
        self.entry_autor.pack(pady=5)
        self.entry_reu = ctk.CTkEntry(scroll, placeholder_text="Nome do Réu/Requerido", width=500)
        self.entry_reu.pack(pady=5)
        self.entry_processo = ctk.CTkEntry(scroll, placeholder_text="Número do Processo", width=500)
        self.entry_processo.pack(pady=5)
        self.entry_acao = ctk.CTkEntry(scroll, placeholder_text="Tipo de Ação", width=500)
        self.entry_acao.insert(0, tipo)
        self.entry_acao.pack(pady=5)

        ctk.CTkLabel(scroll, text="DOS FATOS:").pack(pady=(10, 0))
        self.entry_fatos = ctk.CTkTextbox(scroll, width=500, height=80)
        self.entry_fatos.pack()

        ctk.CTkLabel(scroll, text="DOS FUNDAMENTOS JURÍDICOS:").pack(pady=(10, 0))
        self.entry_fundamentos = ctk.CTkTextbox(scroll, width=500, height=80)
        self.entry_fundamentos.pack()

        ctk.CTkLabel(scroll, text="DOS PEDIDOS:").pack(pady=(10, 0))
        self.entry_pedidos = ctk.CTkTextbox(scroll, width=500, height=80)
        self.entry_pedidos.pack()

        self.entry_valor = ctk.CTkEntry(scroll, placeholder_text="Valor da Causa (R$)", width=500)
        self.entry_valor.pack(pady=15)

        btn_gerar = ctk.CTkButton(scroll, text="Gerar Documento (Word e PDF)", font=ctk.CTkFont(weight="bold"), height=40, 
                                  command=lambda: self.orquestrar_geracao_peticao(
                                      self.entry_autor.get(), self.entry_reu.get(), self.entry_processo.get(), self.entry_acao.get(), 
                                      self.entry_fatos.get("0.0", "end").strip(), self.entry_fundamentos.get("0.0", "end").strip(), 
                                      self.entry_pedidos.get("0.0", "end").strip(), self.entry_valor.get(), self.lbl_status_peticao
                                  ))
        btn_gerar.pack(pady=20)

        self.lbl_status_peticao = ctk.CTkLabel(scroll, text="")
        self.lbl_status_peticao.pack()

    def mostrar_procuracao(self, tipo):
        if tipo == "Nova Procuração...": return
        self.combo_pecas.set("Nova Peça...") 
        self.limpar_tela_main()

        scroll = ctk.CTkScrollableFrame(self.main_frame, width=800, height=600, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(scroll, text=f"Procuração: {tipo}", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(10, 20))

        config = database.carregar_configuracoes()
        adv_nome = config[1] if config and config[1] else ""

        self.entry_outorgante = ctk.CTkEntry(scroll, placeholder_text="Nome do Outorgante (Cliente)", width=500)
        self.entry_outorgante.pack(pady=5)
        self.entry_outorgado = ctk.CTkEntry(scroll, placeholder_text="Nome do Outorgado (Advogado)", width=500)
        self.entry_outorgado.insert(0, adv_nome)
        self.entry_outorgado.pack(pady=5)

        ctk.CTkLabel(scroll, text="Poderes Específicos:").pack(pady=(10, 0))
        self.entry_poderes = ctk.CTkTextbox(scroll, width=500, height=120)
        if "Ad Judicia" in tipo:
            self.entry_poderes.insert("0.0", "Amplos poderes para o foro em geral, com a cláusula ad judicia et extra...")
        self.entry_poderes.pack()

        btn_gerar = ctk.CTkButton(scroll, text="Gerar Procuração (Word e PDF)", font=ctk.CTkFont(weight="bold"), height=40, 
                                  command=lambda: self.orquestrar_geracao_procuracao(
                                      tipo, self.entry_outorgante.get(), self.entry_outorgado.get(), 
                                      self.entry_poderes.get("0.0", "end").strip(), self.lbl_status_proc
                                  ))
        btn_gerar.pack(pady=20)
        self.lbl_status_proc = ctk.CTkLabel(scroll, text="")
        self.lbl_status_proc.pack()

    def mostrar_ia(self, texto_inicial=""):
        self.limpar_tela_main()
        ctk.CTkLabel(self.main_frame, text="✨ Redação Mágica", font=ctk.CTkFont(size=24, weight="bold"), text_color="#8A2BE2").pack(pady=(10, 10))
        
        self.txt_anotacoes = ctk.CTkTextbox(self.main_frame, width=700, height=300)
        if texto_inicial: self.txt_anotacoes.insert("0.0", texto_inicial)
        self.txt_anotacoes.pack(pady=10)
        
        self.btn_processar_ia = ctk.CTkButton(self.main_frame, text="🤖 Analisar Contexto e Gerar Peça", font=ctk.CTkFont(weight="bold"), fg_color="#8A2BE2", command=self.iniciar_processamento_ia)
        self.btn_processar_ia.pack(pady=20)
        
        self.lbl_status_ia = ctk.CTkLabel(self.main_frame, text="")
        self.lbl_status_ia.pack()

    def iniciar_processamento_ia(self):
        if not self.tem_cota_ia():
            self.mostrar_upgrade()
            return
            
        texto = self.txt_anotacoes.get("0.0", "end").strip()
        if not texto: return
        
        self.lbl_status_ia.configure(text="🔄 IA redigindo a peça... Consumindo 1 crédito.", text_color="yellow")
        self.btn_processar_ia.configure(state="disabled")
        threading.Thread(target=self.processar_ia_background, args=(texto,)).start()

    def processar_ia_background(self, texto):
        try:
            self.consumir_cota_ia()
            dados = ia.analisar_relato_com_ia(texto, GEMINI_API_KEY)
            self.orquestrar_geracao_peticao(
                dados["autor"], dados["reu"], dados["processo"], dados["acao"], dados["fatos"], 
                dados["fundamentos"], dados["pedidos"], dados["valor"], self.lbl_status_ia
            )
        except Exception as e:
            self.lbl_status_ia.configure(text=f"❌ Erro: {str(e)}", text_color="red")
        finally:
            self.btn_processar_ia.configure(state="normal")

    def mostrar_analise(self):
        self.limpar_tela_main()
        ctk.CTkLabel(self.main_frame, text="🔍 Leitor de Contratos e Imagens", font=ctk.CTkFont(size=24, weight="bold"), text_color="#D2691E").pack(pady=(10, 10))
        
        frame_botoes = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        frame_botoes.pack(pady=10)
        
        self.btn_carregar = ctk.CTkButton(frame_botoes, text="📂 Arquivos (Máx 5)", command=self.carregar_arquivos)
        self.btn_carregar.pack(side="left", padx=5)

        self.btn_colar = ctk.CTkButton(frame_botoes, text="📋 Colar Print (Ctrl+V)", fg_color="#2E8B57", hover_color="#228B22", command=self.colar_print)
        self.btn_colar.pack(side="left", padx=5)

        self.lbl_arquivo = ctk.CTkLabel(self.main_frame, text="Nenhum arquivo/imagem selecionado.")
        self.lbl_arquivo.pack()

        self.btn_resumir = ctk.CTkButton(self.main_frame, text="🤖 Extrair Análise Jurídica", font=ctk.CTkFont(weight="bold"), fg_color="#D2691E", hover_color="#BA55D3", state="disabled", command=self.iniciar_analise_doc)
        self.btn_resumir.pack(pady=10)

        self.txt_resultado = ctk.CTkTextbox(self.main_frame, width=700, height=250)
        self.txt_resultado.pack(pady=5)
        
        self.btn_enviar_magica = ctk.CTkButton(self.main_frame, text="✨ Enviar Análise para Redação Mágica", font=ctk.CTkFont(weight="bold"), fg_color="#8A2BE2", state="disabled", command=self.enviar_para_redacao_magica)
        self.btn_enviar_magica.pack(pady=10)
        
        self.arquivos_carregados = []

    def evento_colar_teclado(self, event):
        if hasattr(self, 'btn_colar') and self.btn_colar.winfo_ismapped():
            self.colar_print()

    def colar_print(self):
        if len(self.arquivos_carregados) >= 5: return self.lbl_arquivo.configure(text="⚠️ Limite de 5 arquivos.", text_color="red")
        try:
            img = ImageGrab.grabclipboard()
            if img is None: return self.lbl_arquivo.configure(text="⚠️ Nenhuma imagem copiada!", text_color="red")
            
            temp_dir = tempfile.gettempdir()
            caminho_img = os.path.join(temp_dir, f"lexgen_print_{len(self.arquivos_carregados)}.png")
            img.save(caminho_img, 'PNG')
            
            self.arquivos_carregados.append(caminho_img)
            self.atualizar_label_arquivos()
            self.btn_resumir.configure(state="normal")
        except Exception as e:
            self.lbl_arquivo.configure(text=f"❌ Erro: {str(e)}", text_color="red")

    def carregar_arquivos(self):
        caminhos = filedialog.askopenfilenames(filetypes=[("Documentos e Imagens", "*.pdf *.docx *.txt *.png *.jpg *.jpeg")])
        if caminhos:
            if len(self.arquivos_carregados) + len(caminhos) > 5:
                self.lbl_arquivo.configure(text="⚠️ O limite total é de 5 arquivos.", text_color="red")
            else:
                self.arquivos_carregados.extend(list(caminhos))
                self.atualizar_label_arquivos()
                self.btn_resumir.configure(state="normal")

    def atualizar_label_arquivos(self):
        self.lbl_arquivo.configure(text=f"✅ {len(self.arquivos_carregados)} anexo(s)", text_color="green")

    def iniciar_analise_doc(self):
        if not self.tem_cota_ia():
            self.mostrar_upgrade()
            return
            
        self.txt_resultado.delete("0.0", "end")
        self.txt_resultado.insert("0.0", "🔄 IA extraindo dados... Consumindo 1 crédito.")
        self.btn_resumir.configure(state="disabled")
        threading.Thread(target=self.processar_analise_background).start()

    def processar_analise_background(self):
        try:
            self.consumir_cota_ia()
            resultado = ia.analisar_documentos_ia(self.arquivos_carregados, GEMINI_API_KEY)
            self.txt_resultado.delete("0.0", "end")
            self.txt_resultado.insert("0.0", resultado)
            self.btn_enviar_magica.configure(state="normal")
        except Exception as e:
            self.txt_resultado.delete("0.0", "end")
            self.txt_resultado.insert("0.0", f"❌ Erro na leitura: {str(e)}")
        finally:
            self.btn_resumir.configure(state="normal")

    def enviar_para_redacao_magica(self):
        analise = self.txt_resultado.get("0.0", "end").strip()
        if analise and not analise.startswith("🔄") and not analise.startswith("❌"):
            prompt_pronto = f"Com base na seguinte análise jurídica do caso, redija a peça processual cabível:\n\n{analise}"
            self.mostrar_ia(texto_inicial=prompt_pronto)

    # 
    # INTEGRADORES COM O MOTOR DE SALVAMENTO
    # 
    def orquestrar_geracao_peticao(self, autor, reu, processo, acao, fatos, fundamentos, pedidos, valor, label_status):
        config = database.carregar_configuracoes()
        if not config: return label_status.configure(text="⚠️ Cadastre o escritório primeiro!", text_color="red")
        
        docx_file, pdf_file = documentos.gerar_peticao_docx(autor, reu, processo, acao, fatos, fundamentos, pedidos, valor, config[0], config[1], config[2], config[3])
        caminho_final = pdf_file or docx_file
        label_status.configure(text=f"✨ Salvo com Sucesso em:\n{caminho_final}", text_color="green")

    def orquestrar_geracao_procuracao(self, tipo, outorgante, outorgado, poderes, label_status):
        config = database.carregar_configuracoes()
        if not config: return label_status.configure(text="⚠️ Cadastre o escritório primeiro!", text_color="red")

        docx_file, pdf_file = documentos.gerar_procuracao_docx(tipo, outorgante, outorgado, poderes, config[0], config[2], config[3])
        caminho_final = pdf_file or docx_file
        label_status.configure(text=f"✨ Procuração Salva em:\n{caminho_final}", text_color="green")

if __name__ == "__main__":
    app = AppJuridico()
    app.mainloop()