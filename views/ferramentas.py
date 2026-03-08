import customtkinter as ctk
from tkinter import filedialog
import threading
import os
import tempfile
import webbrowser
from PIL import ImageGrab
from dotenv import load_dotenv

import database
import ia
import documentos
import pagamentos

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class ConfigFrame(ctk.CTkFrame):
    def __init__(self, master, dashboard):
        super().__init__(master, fg_color="transparent")
        
        ctk.CTkLabel(self, text="Configurações do Escritório", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(10, 20))
        
        self.entry_escritorio = ctk.CTkEntry(self, placeholder_text="Nome do Escritório", width=400); self.entry_escritorio.pack(pady=10)
        self.entry_advogado = ctk.CTkEntry(self, placeholder_text="Nome do Advogado", width=400); self.entry_advogado.pack(pady=10)
        self.entry_oab = ctk.CTkEntry(self, placeholder_text="Número da OAB", width=400); self.entry_oab.pack(pady=10)

        frame_pasta = ctk.CTkFrame(self, fg_color="transparent"); frame_pasta.pack(pady=5)
        self.entry_pasta = ctk.CTkEntry(frame_pasta, width=300); self.entry_pasta.pack(side="left", padx=5)
        ctk.CTkButton(frame_pasta, text="Procurar", width=80, command=self.selecionar_pasta).pack(side="left")
        
        self.lbl_status = ctk.CTkLabel(self, text=""); self.lbl_status.pack(pady=10)
        ctk.CTkButton(self, text="Salvar Configurações", command=self.salvar).pack(pady=20)

        config = database.carregar_configuracoes()
        if config:
            self.entry_escritorio.insert(0, config[0] if config[0] else "")
            self.entry_advogado.insert(0, config[1] if config[1] else "")
            self.entry_oab.insert(0, config[2] if config[2] else "")
            self.entry_pasta.insert(0, config[3] if len(config)>3 and config[3] else "")

    def selecionar_pasta(self):
        pasta = filedialog.askdirectory()
        if pasta:
            self.entry_pasta.delete(0, 'end')
            self.entry_pasta.insert(0, pasta)

    def salvar(self):
        if not self.entry_escritorio.get() or not self.entry_advogado.get():
            return self.lbl_status.configure(text="⚠️ Preencha os campos!", text_color="red")
        database.salvar_configuracoes(self.entry_escritorio.get(), self.entry_advogado.get(), self.entry_oab.get(), self.entry_pasta.get())
        self.lbl_status.configure(text="✅ Salvo com sucesso.", text_color="green")

class UpgradeFrame(ctk.CTkFrame):
    def __init__(self, master, dashboard):
        super().__init__(master, fg_color="transparent")
        self.dashboard = dashboard
        
        ctk.CTkLabel(self, text="⭐ Atualize para o LexGen PRO", font=ctk.CTkFont(size=30, weight="bold"), text_color="#FFD700").pack(pady=(30, 10))
        
        card = ctk.CTkFrame(self, width=400, height=350, corner_radius=15, border_width=2, border_color="#FFD700")
        card.pack(padx=20, pady=20)
        card.pack_propagate(False)

        ctk.CTkLabel(card, text="Plano PRO Ilimitado", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        ctk.CTkLabel(card, text="✔️ Redação Mágica Ilimitada\n✔️ Análise de Documentos Ilimitada\n✔️ Suporte Prioritário", justify="left").pack(pady=10)
        ctk.CTkLabel(card, text="R$ 97,00 / mês", font=ctk.CTkFont(size=24, weight="bold"), text_color="#8A2BE2").pack(pady=10)

        self.btn_assinar = ctk.CTkButton(card, text="Gerar Link de Pagamento", font=ctk.CTkFont(weight="bold"), fg_color="#FFD700", text_color="black", command=self.iniciar)
        self.btn_assinar.pack(pady=10)
        self.lbl_status = ctk.CTkLabel(card, text=""); self.lbl_status.pack()

    def iniciar(self):
        self.lbl_status.configure(text="⏳ Gerando link...", text_color="yellow")
        self.btn_assinar.configure(state="disabled")
        threading.Thread(target=self._thread_gerar).start()

    def _thread_gerar(self):
        email = self.dashboard.app.usuario_logado['email']
        link, erro = pagamentos.gerar_link_pagamento(email)
        if link:
            webbrowser.open(link)
            self.lbl_status.configure(text="✅ Pague no navegador e valide abaixo.", text_color="green")
            self.btn_assinar.configure(state="normal", text="Validar Pagamento", command=self.validar)
        else:
            self.lbl_status.configure(text=f"❌ Erro: {erro}", text_color="red")
            self.btn_assinar.configure(state="normal")

    def validar(self):
        self.lbl_status.configure(text="⏳ Consultando...", text_color="yellow")
        self.btn_assinar.configure(state="disabled")
        threading.Thread(target=self._thread_validar).start()
        
    def _thread_validar(self):
        email = self.dashboard.app.usuario_logado['email']
        if pagamentos.verificar_pagamento_aprovado(email):
            database.atualizar_plano_pro(email)
            self.lbl_status.configure(text="🎉 Aprovado!", text_color="green")
            self.after(2000, lambda: self.dashboard.app.trocar_tela(self.dashboard.__class__))
        else:
            self.lbl_status.configure(text="⚠️ Não aprovado.", text_color="orange")
            self.btn_assinar.configure(state="normal")

class PeticaoFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, dashboard, tipo):
        super().__init__(master, width=800, height=600, fg_color="transparent")
        ctk.CTkLabel(self, text=f"Documento: {tipo}", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(10, 20))
        
        self.entry_autor = ctk.CTkEntry(self, placeholder_text="Autor", width=500); self.entry_autor.pack(pady=5)
        self.entry_reu = ctk.CTkEntry(self, placeholder_text="Réu", width=500); self.entry_reu.pack(pady=5)
        self.entry_processo = ctk.CTkEntry(self, placeholder_text="Processo", width=500); self.entry_processo.pack(pady=5)
        self.entry_acao = ctk.CTkEntry(self, width=500); self.entry_acao.insert(0, tipo); self.entry_acao.pack(pady=5)
        
        self.entry_fatos = ctk.CTkTextbox(self, width=500, height=80); self.entry_fatos.pack(pady=5)
        self.entry_fundamentos = ctk.CTkTextbox(self, width=500, height=80); self.entry_fundamentos.pack(pady=5)
        self.entry_pedidos = ctk.CTkTextbox(self, width=500, height=80); self.entry_pedidos.pack(pady=5)
        self.entry_valor = ctk.CTkEntry(self, placeholder_text="Valor", width=500); self.entry_valor.pack(pady=5)

        self.lbl_status = ctk.CTkLabel(self, text="")
        ctk.CTkButton(self, text="Gerar", command=self.gerar).pack(pady=20)
        self.lbl_status.pack()

    def gerar(self):
        config = database.carregar_configuracoes()
        if not config: return self.lbl_status.configure(text="⚠️ Cadastre o escritório!", text_color="red")
        d, p = documentos.gerar_peticao_docx(self.entry_autor.get(), self.entry_reu.get(), self.entry_processo.get(), self.entry_acao.get(), self.entry_fatos.get("0.0", "end"), self.entry_fundamentos.get("0.0", "end"), self.entry_pedidos.get("0.0", "end"), self.entry_valor.get(), config[0], config[1], config[2], config[3])
        self.lbl_status.configure(text=f"✨ Salvo: {p or d}", text_color="green")

class ProcuracaoFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, dashboard, tipo):
        super().__init__(master, width=800, height=600, fg_color="transparent")
        ctk.CTkLabel(self, text=f"Procuração: {tipo}", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(10, 20))
        
        config = database.carregar_configuracoes()
        self.entry_outorgante = ctk.CTkEntry(self, placeholder_text="Outorgante", width=500); self.entry_outorgante.pack(pady=5)
        self.entry_outorgado = ctk.CTkEntry(self, width=500); self.entry_outorgado.insert(0, config[1] if config else ""); self.entry_outorgado.pack(pady=5)
        self.entry_poderes = ctk.CTkTextbox(self, width=500, height=120); self.entry_poderes.pack(pady=5)

        self.lbl_status = ctk.CTkLabel(self, text="")
        ctk.CTkButton(self, text="Gerar", command=self.gerar).pack(pady=20)
        self.lbl_status.pack()

    def gerar(self):
        config = database.carregar_configuracoes()
        if not config: return self.lbl_status.configure(text="⚠️ Cadastre o escritório!", text_color="red")
        d, p = documentos.gerar_procuracao_docx("Geral", self.entry_outorgante.get(), self.entry_outorgado.get(), self.entry_poderes.get("0.0", "end"), config[0], config[2], config[3])
        self.lbl_status.configure(text=f"✨ Salva: {p or d}", text_color="green")

class IaMagicaFrame(ctk.CTkFrame):
    def __init__(self, master, dashboard, texto_inicial=""):
        super().__init__(master, fg_color="transparent")
        self.dashboard = dashboard
        ctk.CTkLabel(self, text="✨ Redação Mágica", font=ctk.CTkFont(size=24, weight="bold"), text_color="#8A2BE2").pack(pady=10)
        self.txt = ctk.CTkTextbox(self, width=700, height=300)
        if texto_inicial: self.txt.insert("0.0", texto_inicial)
        self.txt.pack(pady=10)
        
        self.btn = ctk.CTkButton(self, text="🤖 Analisar e Gerar", fg_color="#8A2BE2", command=self.processar)
        self.btn.pack(pady=20)
        self.lbl = ctk.CTkLabel(self, text=""); self.lbl.pack()

    def processar(self):
        if not self.dashboard.tem_cota_ia(): return self.dashboard.mostrar_tela(UpgradeFrame)
        texto = self.txt.get("0.0", "end").strip()
        if not texto: return
        self.lbl.configure(text="🔄 IA redigindo...", text_color="yellow"); self.btn.configure(state="disabled")
        threading.Thread(target=self._thread, args=(texto,)).start()

    def _thread(self, texto):
        try:
            self.dashboard.consumir_cota_ia()
            dados = ia.analisar_relato_com_ia(texto, GEMINI_API_KEY)
            cfg = database.carregar_configuracoes()
            d, p = documentos.gerar_peticao_docx(dados["autor"], dados["reu"], dados["processo"], dados["acao"], dados["fatos"], dados["fundamentos"], dados["pedidos"], dados["valor"], cfg[0], cfg[1], cfg[2], cfg[3])
            self.lbl.configure(text=f"✅ Salvo: {p or d}", text_color="green")
        except Exception as e:
            self.lbl.configure(text=f"❌ Erro: {str(e)}", text_color="red")
        finally:
            self.btn.configure(state="normal")

class LeitorContratosFrame(ctk.CTkFrame):
    def __init__(self, master, dashboard):
        super().__init__(master, fg_color="transparent")
        self.dashboard = dashboard
        self.arquivos = []
        
        ctk.CTkLabel(self, text="🔍 Leitor de Contratos", font=ctk.CTkFont(size=24, weight="bold"), text_color="#D2691E").pack(pady=10)
        fb = ctk.CTkFrame(self, fg_color="transparent"); fb.pack(pady=10)
        ctk.CTkButton(fb, text="📂 Arquivos", command=self.carregar).pack(side="left", padx=5)
        ctk.CTkButton(fb, text="📋 Print (Ctrl+V)", fg_color="#2E8B57", command=self.colar_print).pack(side="left", padx=5)
        
        self.lbl_arq = ctk.CTkLabel(self, text="Nenhum anexo."); self.lbl_arq.pack()
        self.btn_res = ctk.CTkButton(self, text="🤖 Extrair Análise", fg_color="#D2691E", state="disabled", command=self.analisar)
        self.btn_res.pack(pady=10)
        self.txt_res = ctk.CTkTextbox(self, width=700, height=250); self.txt_res.pack()
        self.btn_env = ctk.CTkButton(self, text="✨ Enviar p/ Redação", fg_color="#8A2BE2", state="disabled", command=self.enviar)
        self.btn_env.pack(pady=10)

    def colar_print(self):
        try:
            img = ImageGrab.grabclipboard()
            if img:
                p = os.path.join(tempfile.gettempdir(), f"print_{len(self.arquivos)}.png")
                img.save(p, 'PNG'); self.arquivos.append(p)
                self.lbl_arq.configure(text=f"✅ {len(self.arquivos)} anexo(s)", text_color="green")
                self.btn_res.configure(state="normal")
        except: pass

    def carregar(self):
        c = filedialog.askopenfilenames()
        if c:
            self.arquivos.extend(list(c))
            self.lbl_arq.configure(text=f"✅ {len(self.arquivos)} anexo(s)", text_color="green")
            self.btn_res.configure(state="normal")

    def analisar(self):
        if not self.dashboard.tem_cota_ia(): return self.dashboard.mostrar_tela(UpgradeFrame)
        self.txt_res.delete("0.0", "end"); self.txt_res.insert("0.0", "🔄 Extraindo...")
        self.btn_res.configure(state="disabled")
        threading.Thread(target=self._thread).start()

    def _thread(self):
        try:
            self.dashboard.consumir_cota_ia()
            r = ia.analisar_documentos_ia(self.arquivos, GEMINI_API_KEY)
            self.txt_res.delete("0.0", "end"); self.txt_res.insert("0.0", r)
            self.btn_env.configure(state="normal")
        except Exception as e:
            self.txt_res.delete("0.0", "end"); self.txt_res.insert("0.0", f"❌ {e}")
        finally:
            self.btn_res.configure(state="normal")

    def enviar(self):
        self.dashboard.mostrar_tela(IaMagicaFrame, texto_inicial=f"Com base na análise:\n\n{self.txt_res.get('0.0', 'end')}")