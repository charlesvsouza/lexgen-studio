from google import genai
import PyPDF2
from docx import Document as DocxDocument
from PIL import Image
import os

def analisar_relato_com_ia(texto_bruto, api_key):
    """Gera peça inteligente a partir do relato."""
    client = genai.Client(api_key=api_key)
    prompt = f"""
    Atue como um advogado especialista. Analise o relato do cliente ou a análise prévia do caso e crie a peça jurídica cabível.
    Se for uma resposta (contestação, recurso, manifestação), extraia o número do processo se mencionado.
    Retorne EXATAMENTE neste formato (sem usar markdown de negrito e respeitando as tags abaixo):
    
    AUTOR: Nome do autor/requerente
    REU: Nome do réu/requerido
    PROCESSO: Número do processo (ou deixe em branco se não for mencionado)
    ACAO: Nome da ação ou peça jurídica correta
    FATOS: A história reescrita em linguagem jurídica formal.
    FUNDAMENTOS: Os artigos de lei que embasam a peça.
    PEDIDOS: A lista de pedidos.
    VALOR: O valor da causa em Reais (ou deixe em branco).

    Relato: {texto_bruto}
    """
    
    response = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
    texto_resposta = response.text
    linhas = texto_resposta.split('\n')
    
    dados = {"autor": "", "reu": "", "processo": "", "acao": "", "fatos": "", "fundamentos": "", "pedidos": "", "valor": ""}
    chave_atual = None

    for linha in linhas:
        linha_limpa = linha.strip()
        if linha_limpa.startswith("AUTOR:"): chave_atual = "autor"; dados[chave_atual] = linha_limpa.replace("AUTOR:", "").strip()
        elif linha_limpa.startswith("REU:"): chave_atual = "reu"; dados[chave_atual] = linha_limpa.replace("REU:", "").strip()
        elif linha_limpa.startswith("PROCESSO:"): chave_atual = "processo"; dados[chave_atual] = linha_limpa.replace("PROCESSO:", "").strip()
        elif linha_limpa.startswith("ACAO:"): chave_atual = "acao"; dados[chave_atual] = linha_limpa.replace("ACAO:", "").strip()
        elif linha_limpa.startswith("FATOS:"): chave_atual = "fatos"; dados[chave_atual] = linha_limpa.replace("FATOS:", "").strip()
        elif linha_limpa.startswith("FUNDAMENTOS:"): chave_atual = "fundamentos"; dados[chave_atual] = linha_limpa.replace("FUNDAMENTOS:", "").strip()
        elif linha_limpa.startswith("PEDIDOS:"): chave_atual = "pedidos"; dados[chave_atual] = linha_limpa.replace("PEDIDOS:", "").strip()
        elif linha_limpa.startswith("VALOR:"): chave_atual = "valor"; dados[chave_atual] = linha_limpa.replace("VALOR:", "").strip()
        elif chave_atual and linha_limpa:
            dados[chave_atual] += "\n" + linha_limpa
            
    return dados

def analisar_documentos_ia(caminhos_arquivos, api_key):
    """Lê até 5 arquivos mistos (PDF, Word, TXT, Imagens) e cruza as informações."""
    client = genai.Client(api_key=api_key)
    
    prompt = """
    Atue como um advogado sênior revisando os documentos e imagens anexadas. Forneça um resumo profundo contendo:
    1. Natureza da Ação / Tipo dos Documentos
    2. Resumo dos Fatos (O que aconteceu?)
    3. Pontos Críticos e Argumentos Legais
    4. Indicação da Peça Cabível (Qual peça devemos protocolar agora?)
    
    Mantenha o tom estritamente profissional e objetivo.
    """
    
    contents = [prompt]
    texto_combinado = ""
    
    for caminho in caminhos_arquivos:
        extensao = caminho.lower().split('.')[-1]
        nome_arq = os.path.basename(caminho)
        
        if extensao in ['pdf', 'docx', 'txt']:
            texto_combinado += f"\n--- Conteúdo do arquivo: {nome_arq} ---\n"
            try:
                if extensao == 'pdf':
                    with open(caminho, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        for page in reader.pages:
                            ext = page.extract_text()
                            if ext: texto_combinado += ext + "\n"
                elif extensao == 'docx':
                    doc = DocxDocument(caminho)
                    for para in doc.paragraphs:
                        texto_combinado += para.text + "\n"
                elif extensao == 'txt':
                    with open(caminho, 'r', encoding='utf-8') as f:
                        texto_combinado += f.read() + "\n"
            except Exception as e:
                texto_combinado += f"[Erro ao ler arquivo {nome_arq}: {e}]\n"
                
        elif extensao in ['png', 'jpg', 'jpeg']:
            try:
                img = Image.open(caminho)
                contents.append(f"\n--- Imagem anexada visualmente: {nome_arq} ---")
                contents.append(img)
            except Exception as e:
                texto_combinado += f"[Erro ao abrir imagem {nome_arq}: {e}]\n"

    if texto_combinado.strip():
        contents.append(f"\nTextos extraídos dos documentos:\n{texto_combinado[:60000]}") 

    response = client.models.generate_content(model='gemini-2.5-flash', contents=contents)
    return response.text