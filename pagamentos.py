import mercadopago
import os
from dotenv import load_dotenv

load_dotenv()
MP_ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")

def gerar_link_pagamento(email_usuario):
    """Gera um link de checkout dinâmico no Mercado Pago"""
    if not MP_ACCESS_TOKEN or MP_ACCESS_TOKEN == "SEU_TOKEN_DO_MERCADO_PAGO_AQUI":
        return None, "Token do Mercado Pago não configurado no .env"
    
    sdk = mercadopago.SDK(MP_ACCESS_TOKEN)
    
    preference_data = {
        "items": [
            {
                "title": "LexGen Studio PRO - Acesso Ilimitado",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": 97.00
            }
        ],
        "payer": {
            "email": email_usuario
        },
        # O segredo da arquitetura: usamos o e-mail como referência para achar o pagamento depois!
        "external_reference": email_usuario, 
    }
    
    try:
        preference_response = sdk.preference().create(preference_data)
        link = preference_response["response"]["init_point"]
        return link, None
    except Exception as e:
        return None, f"Erro na API: {str(e)}"

def verificar_pagamento_aprovado(email_usuario):
    """Consulta ativamente a API para ver se o pagamento deste e-mail foi aprovado"""
    if not MP_ACCESS_TOKEN or MP_ACCESS_TOKEN == "SEU_TOKEN_DO_MERCADO_PAGO_AQUI":
        return False
        
    sdk = mercadopago.SDK(MP_ACCESS_TOKEN)
    
    # Busca apenas os pagamentos aprovados daquele usuário específico
    filters = {
        "external_reference": email_usuario,
        "status": "approved"
    }
    
    try:
        payment_response = sdk.payment().search(filters)
        results = payment_response["response"]["results"]
        # Se a lista tiver pelo menos 1 item, o cara pagou!
        return len(results) > 0
    except:
        return False