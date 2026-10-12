"""
Módulo de Integração com WhatsApp via Playwright
Suporta:
1. Sessão persistente (login via QR Code salvo em data/whatsapp_session)
2. Envio automático de mensagens formatadas com a leitura e reflexão do dia
3. Geração de links diretos 'wa.me' para envio manual em 1 clique
4. Agendamento em segundo plano
"""

import os
import sys
import json
import time
import urllib.parse
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    sync_playwright = None
    PLAYWRIGHT_AVAILABLE = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_DIR = os.path.join(BASE_DIR, "data", "whatsapp_session")

def format_whatsapp_message(day_data, books_data=None, user_name="Irmão(ã)", bedside_book=None, pastoral_focus=None):
    """
    Formata uma mensagem rica com formatação do WhatsApp (*negrito*, _itálico_, emojis).
    """
    day = day_data.get("day", 1)
    reading = day_data.get("reading", "")
    testament = day_data.get("testament", "")
    category = day_data.get("category", "")
    theme = day_data.get("theme", "")
    verse_text = day_data.get("key_verse_text", "")
    verse_ref = day_data.get("key_verse_ref", "")
    reflection = day_data.get("reflection", "")
    tags = day_data.get("tags", [])

    msg_lines = [
        f"📖 *JORNADA BÍBLICA 365* 🕊️",
        f"━━━━━━━━━━━━━━━━━━",
        f"Olá, *{user_name}*! Aqui está o seu estudo bíblico de hoje:",
        f"",
        f"📅 *Dia {day} de 365* | *{reading}*",
        f"📌 *Seção:* {category} ({testament})",
        f"✨ *Tema Central:* _{theme}_",
        f"",
        f"📜 *Versículo em Destaque:*",
        f"_{verse_text}_",
        f"— *{verse_ref}*",
        f"",
        f"💡 *Reflexão para o seu Dia:*",
        f"{reflection}",
    ]

    # Livro de Cabeceira / Travesseiro
    if bedside_book:
        p_topic = (pastoral_focus or {}).get("topic", "Ministério e Prática Pastoral")
        p_quote = (pastoral_focus or {}).get("quote", "Crescimento contínuo no poder e sabedoria do Espírito Santo.")
        msg_lines.extend([
            "",
            "🛌 *Livro de Travesseiro:* _O Pastor Pentecostal_ (CPAD)",
            f"⚡ *Foco Pastoral:* _{p_topic}_",
            f"_{p_quote}_"
        ])

    # Recomendações da biblioteca
    if books_data and len(books_data) > 0:
        msg_lines.append("")
        msg_lines.append("📚 *Leitura Recomendada da sua Biblioteca:*")
        for b in books_data[:2]:
            msg_lines.append(f"• _{b.get('title')}_ ({b.get('author')})")

    msg_lines.extend([
        "",
        "🎯 *Perguntas para Fixação:*",
        "1. O que este texto revela sobre o caráter de Deus?",
        "2. Como posso aplicar este princípio hoje na minha rotina?",
        "",
        "✅ *Acesse seu Painel para registrar o estudo:*",
        "http://localhost:5000",
        "━━━━━━━━━━━━━━━━━━",
        "_“Lâmpada para os meus pés é a tua palavra.” (Sl 119:105)_"
    ])

    return "\n".join(msg_lines)


def get_direct_whatsapp_url(phone_number, message_text):
    """
    Gera uma URL direta no formato wa.me com texto codificado para envio rápido.
    """
    clean_phone = "".join(filter(str.isdigit, phone_number or ""))
    encoded_text = urllib.parse.quote(message_text)
    if clean_phone:
        return f"https://web.whatsapp.com/send?phone={clean_phone}&text={encoded_text}"
    return f"https://web.whatsapp.com/send?text={encoded_text}"


class WhatsAppBot:
    def __init__(self, session_dir=SESSION_DIR):
        self.session_dir = session_dir
        os.makedirs(self.session_dir, exist_ok=True)

    def is_logged_in(self):
        """Verifica se há indícios de sessão ativa no diretório."""
        if not os.path.exists(self.session_dir):
            return False
        # Se contiver arquivos de sessão do Chromium
        files = os.listdir(self.session_dir)
        return len(files) > 3

    def _launch_context(self, p, headless=False, viewport=None):
        """Inicializa o contexto usando o navegador nativo Edge ou Chrome."""
        for channel in ["msedge", "chrome", None]:
            try:
                kwargs = {
                    "headless": headless,
                    "args": ["--no-sandbox", "--disable-dev-shm-usage"]
                }
                if channel:
                    kwargs["channel"] = channel
                if viewport:
                    kwargs["viewport"] = viewport
                return p.chromium.launch_persistent_context(self.session_dir, **kwargs)
            except Exception as e:
                if channel is None:
                    raise e
                continue

    def open_for_login(self):
        """
        Abre o navegador visível para o usuário escanear o QR Code pela primeira vez.
        """
        if not PLAYWRIGHT_AVAILABLE:
            return {"success": False, "message": "Playwright não está instalado neste ambiente. No servidor em nuvem, utilize o envio em 1-clique pelo navegador do celular."}

        print("[WhatsApp] Abrindo navegador para conexão do WhatsApp Web...")
        print("[WhatsApp] Por favor, aponte a câmera do seu celular para o QR Code na tela.")
        with sync_playwright() as p:
            try:
                context = self._launch_context(p, headless=False, viewport={"width": 1000, "height": 800})
            except Exception as e:
                return {"success": False, "message": f"Erro ao iniciar navegador: {e}"}

            page = context.new_page()
            page.goto("https://web.whatsapp.com", wait_until="load")
            
            # Aguarda até que a barra de busca ou lista de chats apareça (sinal de login realizado)
            print("[WhatsApp] Aguardando autenticação...")
            try:
                # O elemento div[contenteditable='true'] ou pane de conversas indica login
                page.wait_for_selector("div[contenteditable='true'], div[id='side'], div[role='textbox']", timeout=120000)
                print("[WhatsApp] SUCESSO! Conectado e sessão salva permanentemente.")
                page.wait_for_timeout(3000)
                context.close()
                return {"success": True, "message": "WhatsApp conectado com sucesso!"}
            except Exception as e:
                print(f"[WhatsApp] Tempo limite esgotado ou janela fechada: {e}")
                try:
                    context.close()
                except Exception:
                    pass
                return {"success": False, "message": f"Tempo limite ou janela fechada: {str(e)}"}

    def send_message(self, phone_number, message_text, headless=False):
        """
        Envia uma mensagem para o número informado utilizando a sessão persistente.
        """
        clean_phone = "".join(filter(str.isdigit, phone_number or ""))
        if not clean_phone:
            return {"success": False, "message": "Número de telefone não informado."}

        # Garante DDI do Brasil (55) se o usuário digitou apenas DDD + número (10 ou 11 dígitos)
        if len(clean_phone) in [10, 11]:
            clean_phone = "55" + clean_phone

        encoded_text = urllib.parse.quote(message_text)
        url = f"https://web.whatsapp.com/send?phone={clean_phone}&text={encoded_text}"

        if not PLAYWRIGHT_AVAILABLE:
            return {"success": False, "message": "Playwright não está instalado neste ambiente. No servidor em nuvem, utilize o envio em 1-clique pelo navegador do celular."}

        with sync_playwright() as p:
            try:
                context = self._launch_context(p, headless=headless)
                page = context.new_page()
                page.goto(url, wait_until="load")

                # Aguarda o botão de envio ficar visível e habilitado
                # Seletores comuns do botão de enviar no WhatsApp Web
                send_button_selector = "button[aria-label='Enviar'], button[data-tab='11'], span[data-icon='send']"
                
                print("[WhatsApp] Aguardando carregamento da conversa...")
                try:
                    # Espera a caixa de mensagem ou botão de envio
                    page.wait_for_selector(send_button_selector, timeout=35000)
                    time.sleep(2)
                    
                    # Clica no botão de enviar
                    send_btn = page.query_selector(send_button_selector)
                    if send_btn:
                        send_btn.click()
                    else:
                        page.keyboard.press("Enter")
                    
                    print("[WhatsApp] Mensagem enviada! Aguardando confirmação do status...")
                    time.sleep(4)
                    context.close()
                    return {"success": True, "message": f"Mensagem enviada com sucesso para +{clean_phone}!"}
                except Exception as inner_e:
                    # Tentar pressionar Enter diretamente caso o botão não tenha o seletor exato
                    try:
                        time.sleep(3)
                        page.keyboard.press("Enter")
                        time.sleep(3)
                        context.close()
                        return {"success": True, "message": f"Mensagem enviada via Enter para +{clean_phone}!"}
                    except Exception:
                        context.close()
                        return {
                            "success": False, 
                            "message": f"Não foi possível enviar automaticamente. Verifique se o WhatsApp está logado. Erro: {inner_e}"
                        }
            except Exception as e:
                return {"success": False, "message": f"Erro ao abrir navegador: {str(e)}"}


if __name__ == "__main__":
    bot = WhatsAppBot()
    if len(sys.argv) > 1 and sys.argv[1] == "--login":
        res = bot.open_for_login()
        print(res)
    else:
        print("Uso:")
        print("  py whatsapp_bot.py --login  (para abrir e escanear o QR code)")
        print(f"Sessão ativa? {bot.is_logged_in()}")
