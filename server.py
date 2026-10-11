"""
Servidor Backend REST da Jornada Bíblica 365
Executa servidor HTTP na porta 5000 servindo a aplicação web estática e as rotas de API.
Totalmente construído sobre a biblioteca padrão do Python.
"""

import http.server
import socketserver
import json
import os
import sqlite3
import urllib.parse
import threading
import sys
from datetime import datetime, date

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

PORT = int(os.environ.get("PORT", 5000))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "study.db")
JSON_PLAN_PATH = os.path.join(DATA_DIR, "bible_plan.json")

# Se os dados não existirem (ex: não subiu a pasta data no GitHub), gera automaticamente
if not os.path.exists(JSON_PLAN_PATH) or not os.path.exists(DB_PATH):
    import generate_plan
    generate_plan.init_database_and_json()

with open(JSON_PLAN_PATH, "r", encoding="utf-8") as f:
    BIBLE_PLAN = json.load(f)

try:
    from whatsapp_bot import WhatsAppBot, format_whatsapp_message, get_direct_whatsapp_url
    whatsapp_bot = WhatsAppBot()
except Exception:
    class DummyBot:
        session_dir = ""
        def is_logged_in(self): return False
        def open_for_login(self): return {"success": False, "message": "Bot local não disponível em nuvem."}
        def send_message(self, *a, **kw): return {"success": False, "message": "Use o link direto pelo celular."}
    whatsapp_bot = DummyBot()

    def format_whatsapp_message(day_data, books_data=None, user_name="Irmão(ã)"):
        day = day_data.get("day", 1)
        reading = day_data.get("reading", "")
        testament = day_data.get("testament", "")
        category = day_data.get("category", "")
        theme = day_data.get("theme", "")
        verse_text = day_data.get("key_verse_text", "")
        verse_ref = day_data.get("key_verse_ref", "")
        reflection = day_data.get("reflection", "")
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
            "━━━━━━━━━━━━━━━━━━",
            "_“Lâmpada para os meus pés é a tua palavra.” (Sl 119:105)_"
        ])
        return "\n".join(msg_lines)

    def get_direct_whatsapp_url(phone_number, message_text):
        clean_phone = "".join(filter(str.isdigit, phone_number or ""))
        encoded_text = urllib.parse.quote(message_text)
        if clean_phone:
            return f"https://web.whatsapp.com/send?phone={clean_phone}&text={encoded_text}"
        return f"https://web.whatsapp.com/send?text={encoded_text}"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_settings():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT key, value FROM settings")
    rows = c.fetchall()
    conn.close()
    return {row["key"]: row["value"] for row in rows}


def get_matching_books(tags):
    """Retorna livros da biblioteca que compartilham tags ou temas com a leitura do dia."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM books")
    all_books = [dict(row) for row in c.fetchall()]
    conn.close()

    if not tags:
        return all_books[:2]

    matched = []
    tags_lower = [t.lower().strip() for t in tags]

    for book in all_books:
        book_themes = (book.get("themes") or "").lower()
        book_title = (book.get("title") or "").lower()
        score = 0
        for tag in tags_lower:
            if tag in book_themes or tag in book_title:
                score += 1
        if score > 0:
            matched.append((score, book))

    matched.sort(key=lambda x: x[0], reverse=True)
    results = [item[1] for item in matched]
    # Se nenhum der match exato, retorna livros gerais
    if not results and all_books:
        return all_books[:2]
    return results[:3]


class BibleStudyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def send_json(self, data, status_code=200):
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def read_json_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            body = self.rfile.read(content_length)
            return json.loads(body.decode("utf-8"))
        return {}

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/"):
            self.handle_api_get(path, urllib.parse.parse_qs(parsed.query))
            return

        # Servir arquivos estáticos (index.html, style.css, app.js, manifest.json, sw.js)
        filename = path.lstrip("/")
        if not filename or filename == "index.html":
            filename = "index.html"
            content_type = "text/html; charset=utf-8"
        elif filename == "style.css":
            content_type = "text/css; charset=utf-8"
        elif filename == "app.js":
            content_type = "application/javascript; charset=utf-8"
        elif filename == "manifest.json":
            content_type = "application/json; charset=utf-8"
        elif filename == "sw.js":
            content_type = "application/javascript; charset=utf-8"
        else:
            content_type = "application/octet-stream"

        possible_paths = [
            os.path.join(STATIC_DIR, filename),
            os.path.join(BASE_DIR, filename),
            os.path.join(BASE_DIR, "static", filename)
        ]

        found_path = None
        for p in possible_paths:
            if os.path.exists(p) and os.path.isfile(p):
                found_path = p
                break

        if found_path:
            with open(found_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_error(404, f"Arquivo '{filename}' não encontrado no servidor.")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path.startswith("/api/"):
            self.handle_api_post(path)
        else:
            self.send_error(404, "Endpoint não encontrado")

    def do_PUT(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path.startswith("/api/"):
            self.handle_api_put(path)
        else:
            self.send_error(404, "Endpoint não encontrado")

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path.startswith("/api/"):
            self.handle_api_delete(path)
        else:
            self.send_error(404, "Endpoint não encontrado")

    # ================= ROTAS GET =================
    def handle_api_get(self, path, query):
        conn = get_db_connection()
        c = conn.cursor()

        # 1. /api/plan -> Lista dos 365 dias mesclada com o progresso do usuário
        if path == "/api/plan":
            c.execute("SELECT day_number, status, completed_at, personal_notes, favorite_verse FROM study_journal")
            progress_map = {row["day_number"]: dict(row) for row in c.fetchall()}
            conn.close()

            merged_plan = []
            for item in BIBLE_PLAN:
                d = dict(item)
                prog = progress_map.get(d["day"], {})
                d["status"] = prog.get("status", "pending")
                d["completed_at"] = prog.get("completed_at")
                d["has_notes"] = bool(prog.get("personal_notes"))
                merged_plan.append(d)

            self.send_json(merged_plan)
            return

        # 2. /api/today -> Dados do dia atual calculado ou configurado
        if path == "/api/today":
            settings = get_settings()
            current_day = int(settings.get("current_day", "1"))
            
            # Localiza o dia
            day_data = next((d for d in BIBLE_PLAN if d["day"] == current_day), BIBLE_PLAN[0])
            c.execute("SELECT * FROM study_journal WHERE day_number = ?", (current_day,))
            row = c.fetchone()
            progress = dict(row) if row else {"status": "pending", "personal_notes": "", "favorite_verse": ""}

            matched_books = get_matching_books(day_data.get("tags", []))
            conn.close()

            response = {
                "day_data": day_data,
                "progress": progress,
                "recommended_books": matched_books,
                "settings": settings
            }
            self.send_json(response)
            return

        # 3. /api/day/<id> -> Detalhes específicos de um dia
        if path.startswith("/api/day/"):
            try:
                day_num = int(path.split("/api/day/")[1])
                day_data = next((d for d in BIBLE_PLAN if d["day"] == day_num), None)
                if not day_data:
                    conn.close()
                    self.send_json({"error": "Dia não encontrado"}, 404)
                    return

                c.execute("SELECT * FROM study_journal WHERE day_number = ?", (day_num,))
                row = c.fetchone()
                progress = dict(row) if row else {"status": "pending", "personal_notes": "", "favorite_verse": ""}
                matched_books = get_matching_books(day_data.get("tags", []))
                conn.close()

                self.send_json({
                    "day_data": day_data,
                    "progress": progress,
                    "recommended_books": matched_books
                })
                return
            except ValueError:
                conn.close()
                self.send_json({"error": "ID do dia inválido"}, 400)
                return

        # 4. /api/books -> Lista de livros da biblioteca
        if path == "/api/books":
            c.execute("SELECT * FROM books ORDER BY id DESC")
            books = [dict(row) for row in c.fetchall()]
            conn.close()
            self.send_json(books)
            return

        # 5. /api/stats -> Estatísticas de progresso
        if path == "/api/stats":
            c.execute("SELECT day_number, status, completed_at FROM study_journal WHERE status = 'completed'")
            completed_days = [dict(row) for row in c.fetchall()]
            completed_count = len(completed_days)
            completed_day_nums = set(row["day_number"] for row in completed_days)

            # Progresso por testamento
            ot_completed = 0
            nt_completed = 0
            for item in BIBLE_PLAN:
                if item["day"] in completed_day_nums:
                    if item["testament"] == "Antigo Testamento":
                        ot_completed += 1
                    else:
                        nt_completed += 1

            total_days = len(BIBLE_PLAN)
            percent = round((completed_count / total_days) * 100, 1)

            # Cálculo de sequência (streak)
            streak = 0
            today_day = int(get_settings().get("current_day", "1"))
            check_day = today_day
            while check_day in completed_day_nums and check_day > 0:
                streak += 1
                check_day -= 1

            c.execute("SELECT COUNT(*) FROM study_journal WHERE personal_notes IS NOT NULL AND length(personal_notes) > 0")
            notes_count = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM books")
            books_count = c.fetchone()[0]

            conn.close()
            self.send_json({
                "completed_count": completed_count,
                "total_days": total_days,
                "percentage": percent,
                "streak": streak,
                "ot_completed": ot_completed,
                "nt_completed": nt_completed,
                "notes_count": notes_count,
                "books_count": books_count
            })
            return

        # 6. /api/settings -> Configurações
        if path == "/api/settings":
            conn.close()
            self.send_json(get_settings())
            return

        # 7. /api/whatsapp/preview -> Mensagem formatada e link direto
        if path == "/api/whatsapp/preview":
            settings = get_settings()
            current_day = int(settings.get("current_day", "1"))
            day_data = next((d for d in BIBLE_PLAN if d["day"] == current_day), BIBLE_PLAN[0])
            matched_books = get_matching_books(day_data.get("tags", []))
            conn.close()

            user_name = settings.get("user_name", "Amado(a)")
            msg = format_whatsapp_message(day_data, matched_books, user_name)
            phone = settings.get("whatsapp_number", "")
            direct_url = get_direct_whatsapp_url(phone, msg)

            self.send_json({
                "message": msg,
                "direct_url": direct_url,
                "is_logged_in": whatsapp_bot.is_logged_in()
            })
            return

        # 8. /api/whatsapp/status -> Status do bot
        if path == "/api/whatsapp/status":
            conn.close()
            self.send_json({
                "is_logged_in": whatsapp_bot.is_logged_in(),
                "session_dir": whatsapp_bot.session_dir
            })
            return

        conn.close()
        self.send_json({"error": "Rota não encontrada"}, 404)

    # ================= ROTAS POST =================
    def handle_api_post(self, path):
        conn = get_db_connection()
        c = conn.cursor()
        data = self.read_json_body()

        # 1. /api/day/<id>/complete -> Alternar status de conclusão
        if path.startswith("/api/day/") and path.endswith("/complete"):
            try:
                parts = path.split("/")
                day_num = int(parts[3])
                c.execute("SELECT status FROM study_journal WHERE day_number = ?", (day_num,))
                row = c.fetchone()
                current_status = row["status"] if row else "pending"
                new_status = "pending" if current_status == "completed" else "completed"
                completed_at = datetime.now().isoformat() if new_status == "completed" else None

                c.execute("""
                INSERT INTO study_journal (day_number, status, completed_at)
                VALUES (?, ?, ?)
                ON CONFLICT(day_number) DO UPDATE SET
                    status = excluded.status,
                    completed_at = excluded.completed_at
                """, (day_num, new_status, completed_at))

                # Atualiza também o current_day para o próximo se concluiu hoje
                if new_status == "completed":
                    next_day = min(day_num + 1, 365)
                    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('current_day', ?)", (str(next_day),))

                conn.commit()
                conn.close()
                self.send_json({"success": True, "new_status": new_status, "completed_at": completed_at})
                return
            except Exception as e:
                conn.close()
                self.send_json({"error": str(e)}, 500)
                return

        # 2. /api/day/<id>/notes -> Salvar anotações do estudo
        if path.startswith("/api/day/") and path.endswith("/notes"):
            try:
                parts = path.split("/")
                day_num = int(parts[3])
                notes = data.get("personal_notes", "")
                favorite_verse = data.get("favorite_verse", "")

                c.execute("""
                INSERT INTO study_journal (day_number, personal_notes, favorite_verse)
                VALUES (?, ?, ?)
                ON CONFLICT(day_number) DO UPDATE SET
                    personal_notes = excluded.personal_notes,
                    favorite_verse = excluded.favorite_verse
                """, (day_num, notes, favorite_verse))
                conn.commit()
                conn.close()
                self.send_json({"success": True, "message": "Anotações salvas com sucesso!"})
                return
            except Exception as e:
                conn.close()
                self.send_json({"error": str(e)}, 500)
                return

        # 3. /api/books -> Adicionar novo livro na biblioteca
        if path == "/api/books":
            try:
                title = data.get("title", "").strip()
                author = data.get("author", "").strip()
                publisher = data.get("publisher", "").strip()
                year = data.get("year")
                themes = data.get("themes", "").strip()
                summary = data.get("summary", "").strip()
                cover_color = data.get("cover_color", "#1e3a8a")
                notes = data.get("notes", "").strip()

                if not title or not author:
                    conn.close()
                    self.send_json({"error": "Título e autor são obrigatórios"}, 400)
                    return

                c.execute("""
                INSERT INTO books (title, author, publisher, year, themes, summary, cover_color, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (title, author, publisher, year, themes, summary, cover_color, notes))
                new_id = c.lastrowid
                conn.commit()
                conn.close()
                self.send_json({"success": True, "id": new_id, "message": "Livro cadastrado com sucesso!"})
                return
            except Exception as e:
                conn.close()
                self.send_json({"error": str(e)}, 500)
                return

        # 4. /api/settings -> Salvar configurações
        if path == "/api/settings":
            try:
                for k, v in data.items():
                    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (str(k), str(v)))
                conn.commit()
                conn.close()
                self.send_json({"success": True, "message": "Configurações salvas!"})
                return
            except Exception as e:
                conn.close()
                self.send_json({"error": str(e)}, 500)
                return

        # 5. /api/whatsapp/login -> Abrir janela do Chromium para escanear QR Code
        if path == "/api/whatsapp/login":
            conn.close()
            def login_thread():
                whatsapp_bot.open_for_login()
            threading.Thread(target=login_thread, daemon=True).start()
            self.send_json({"success": True, "message": "Janela do WhatsApp Web aberta para escanear QR Code!"})
            return

        # 6. /api/whatsapp/send-now -> Enviar mensagem hoje via bot
        if path == "/api/whatsapp/send-now":
            settings = get_settings()
            phone = settings.get("whatsapp_number", "").strip()
            current_day = int(settings.get("current_day", "1"))
            day_data = next((d for d in BIBLE_PLAN if d["day"] == current_day), BIBLE_PLAN[0])
            matched_books = get_matching_books(day_data.get("tags", []))
            conn.close()

            if not phone:
                self.send_json({"error": "Cadastre seu número de WhatsApp nas configurações primeiro!"}, 400)
                return

            user_name = settings.get("user_name", "Irmão(ã)")
            msg = format_whatsapp_message(day_data, matched_books, user_name)

            def send_thread():
                whatsapp_bot.send_message(phone, msg, headless=False)
            threading.Thread(target=send_thread, daemon=True).start()

            self.send_json({"success": True, "message": f"Envio iniciado para o número {phone}!"})
            return

        conn.close()
        self.send_json({"error": "Endpoint não encontrado"}, 404)

    # ================= ROTAS PUT =================
    def handle_api_put(self, path):
        conn = get_db_connection()
        c = conn.cursor()
        data = self.read_json_body()

        # /api/books/<id> -> Atualizar livro
        if path.startswith("/api/books/"):
            try:
                book_id = int(path.split("/api/books/")[1])
                title = data.get("title", "").strip()
                author = data.get("author", "").strip()
                publisher = data.get("publisher", "").strip()
                year = data.get("year")
                themes = data.get("themes", "").strip()
                summary = data.get("summary", "").strip()
                cover_color = data.get("cover_color", "#1e3a8a")
                notes = data.get("notes", "").strip()

                c.execute("""
                UPDATE books SET
                    title = ?, author = ?, publisher = ?, year = ?,
                    themes = ?, summary = ?, cover_color = ?, notes = ?
                WHERE id = ?
                """, (title, author, publisher, year, themes, summary, cover_color, notes, book_id))
                conn.commit()
                conn.close()
                self.send_json({"success": True, "message": "Livro atualizado com sucesso!"})
                return
            except Exception as e:
                conn.close()
                self.send_json({"error": str(e)}, 500)
                return

        conn.close()
        self.send_json({"error": "Endpoint não encontrado"}, 404)

    # ================= ROTAS DELETE =================
    def handle_api_delete(self, path):
        conn = get_db_connection()
        c = conn.cursor()

        # /api/books/<id> -> Excluir livro
        if path.startswith("/api/books/"):
            try:
                book_id = int(path.split("/api/books/")[1])
                c.execute("DELETE FROM books WHERE id = ?", (book_id,))
                conn.commit()
                conn.close()
                self.send_json({"success": True, "message": "Livro removido da biblioteca!"})
                return
            except Exception as e:
                conn.close()
                self.send_json({"error": str(e)}, 500)
                return

        conn.close()
        self.send_json({"error": "Endpoint não encontrado"}, 404)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True

def run_server():
    os.chdir(BASE_DIR)
    with ThreadedTCPServer(("0.0.0.0", PORT), BibleStudyHandler) as httpd:
        print("=" * 60)
        print(f"📖 JORNADA BÍBLICA 365 - SERVIDOR ATIVO")
        print(f"Acesse no seu navegador: http://localhost:{PORT}")
        print("Pressione Ctrl+C para encerrar o servidor.")
        print("=" * 60)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nEncerrando servidor...")
            httpd.server_close()


if __name__ == "__main__":
    run_server()
