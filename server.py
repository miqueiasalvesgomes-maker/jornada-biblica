"""
Servidor Backend REST Multi-Usuário da Jornada Bíblica 365
Suporta múltiplos membros/usuários simultâneos, controle individual de leitura e anotações,
compartilhamento individual e em grupos no WhatsApp, e compatibilidade universal (Local e Nuvem).
"""

import http.server
import socketserver
import json
import os
import sqlite3
import urllib.parse
import threading
import sys
import traceback
from datetime import datetime, date

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(line_buffering=True, encoding='utf-8', errors='replace')

PORT = int(os.environ.get("PORT", 5000))
HOST = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "study.db")
JSON_PLAN_PATH = os.path.join(DATA_DIR, "bible_plan.json")

# Se os dados não existirem (ex: deploy na nuvem sem a pasta data), gera automaticamente
if not os.path.exists(JSON_PLAN_PATH) or not os.path.exists(DB_PATH):
    import generate_plan
    generate_plan.init_database_and_json()

with open(JSON_PLAN_PATH, "r", encoding="utf-8") as f:
    BIBLE_PLAN = json.load(f)

# Fallbacks resilientes para WhatsApp caso Playwright não esteja instalado
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
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_multiuser_db():
    """Migração automática para garantir suporte a múltiplos usuários no banco."""
    conn = get_db_connection()
    c = conn.cursor()

    # 1. Tabela de Usuários
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        avatar_icon TEXT DEFAULT '🕊️',
        current_day INTEGER DEFAULT 1,
        reminder_time TEXT DEFAULT '07:00',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Cria usuário inicial "Miqueias" se não houver nenhum
    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        c.execute("""
        INSERT INTO users (id, name, phone, avatar_icon, current_day)
        VALUES (1, 'Miqueias', '', '🕊️', 1)
        """)

    # 2. Adiciona user_id em study_journal se ainda não existir
    c.execute("PRAGMA table_info(study_journal)")
    columns = [row["name"] for row in c.fetchall()]
    if "user_id" not in columns:
        try:
            c.execute("ALTER TABLE study_journal ADD COLUMN user_id INTEGER DEFAULT 1")
        except Exception:
            pass

    conn.commit()
    conn.close()

# Executa migração
init_multiuser_db()


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
    return results[:3] if results else all_books[:2]


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
        try:
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path

            if path.startswith("/api/"):
                self.handle_api_get(path, urllib.parse.parse_qs(parsed.query))
                return

            # Busca pelo arquivo estático em múltiplos locais possíveis (static/ ou raiz)
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
                self.send_error(404, f"Arquivo '{filename}' não encontrado.")
        except Exception as e:
            traceback.print_exc()
            self.send_json({"error": str(e)}, 500)

    def do_POST(self):
        try:
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path
            if path.startswith("/api/"):
                self.handle_api_post(path)
            else:
                self.send_error(404, "Endpoint não encontrado")
        except Exception as e:
            traceback.print_exc()
            self.send_json({"error": str(e)}, 500)

    def do_PUT(self):
        try:
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path
            if path.startswith("/api/"):
                self.handle_api_put(path)
            else:
                self.send_error(404, "Endpoint não encontrado")
        except Exception as e:
            traceback.print_exc()
            self.send_json({"error": str(e)}, 500)

    def do_DELETE(self):
        try:
            parsed = urllib.parse.urlparse(self.path)
            path = parsed.path
            if path.startswith("/api/"):
                self.handle_api_delete(path)
            else:
                self.send_error(404, "Endpoint não encontrado")
        except Exception as e:
            traceback.print_exc()
            self.send_json({"error": str(e)}, 500)

    # ================= ROTAS GET =================
    def handle_api_get(self, path, query):
        conn = get_db_connection()
        c = conn.cursor()
        user_id = int(query.get("user_id", ["1"])[0])

        # 1. /api/users -> Lista de todos os membros/usuários
        if path == "/api/users":
            c.execute("SELECT * FROM users ORDER BY id ASC")
            users = [dict(row) for row in c.fetchall()]
            for u in users:
                c.execute("SELECT COUNT(*) FROM study_journal WHERE user_id = ? AND status = 'completed'", (u["id"],))
                u["completed_count"] = c.fetchone()[0]
                u["percentage"] = round((u["completed_count"] / 365) * 100, 1)
            conn.close()
            self.send_json(users)
            return

        # 2. /api/plan?user_id=X -> Plano dos 365 dias para o usuário X
        if path == "/api/plan":
            c.execute("SELECT day_number, status, completed_at, personal_notes, favorite_verse FROM study_journal WHERE user_id = ?", (user_id,))
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

        # 3. /api/today?user_id=X -> Dados do dia atual do usuário X
        if path == "/api/today":
            c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user_row = c.fetchone()
            if not user_row:
                c.execute("SELECT * FROM users LIMIT 1")
                user_row = c.fetchone()
            user_data = dict(user_row) if user_row else {"id": 1, "name": "Miqueias", "current_day": 1}

            current_day = int(user_data.get("current_day", 1))
            day_data = next((d for d in BIBLE_PLAN if d["day"] == current_day), BIBLE_PLAN[0])

            c.execute("SELECT * FROM study_journal WHERE user_id = ? AND day_number = ?", (user_data["id"], current_day))
            row = c.fetchone()
            progress = dict(row) if row else {"status": "pending", "personal_notes": "", "favorite_verse": ""}
            matched_books = get_matching_books(day_data.get("tags", []))
            conn.close()

            self.send_json({
                "day_data": day_data,
                "progress": progress,
                "recommended_books": matched_books,
                "user": user_data
            })
            return

        # 4. /api/day/<id>?user_id=X -> Detalhes de um dia específico para usuário X
        if path.startswith("/api/day/"):
            try:
                day_num = int(path.split("/api/day/")[1])
                day_data = next((d for d in BIBLE_PLAN if d["day"] == day_num), None)
                if not day_data:
                    conn.close()
                    self.send_json({"error": "Dia não encontrado"}, 404)
                    return

                c.execute("SELECT * FROM study_journal WHERE user_id = ? AND day_number = ?", (user_id, day_num))
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

        # 5. /api/books -> Lista de livros da biblioteca
        if path == "/api/books":
            c.execute("SELECT * FROM books ORDER BY id DESC")
            books = [dict(row) for row in c.fetchall()]
            conn.close()
            self.send_json(books)
            return

        # 6. /api/stats?user_id=X -> Estatísticas de progresso do usuário X
        if path == "/api/stats":
            c.execute("SELECT day_number, status, completed_at FROM study_journal WHERE user_id = ? AND status = 'completed'", (user_id,))
            completed_days = [dict(row) for row in c.fetchall()]
            completed_count = len(completed_days)
            completed_day_nums = set(row["day_number"] for row in completed_days)

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

            c.execute("SELECT current_day FROM users WHERE id = ?", (user_id,))
            urow = c.fetchone()
            today_day = urow["current_day"] if urow else 1
            streak = 0
            check_day = today_day
            while check_day in completed_day_nums and check_day > 0:
                streak += 1
                check_day -= 1

            c.execute("SELECT COUNT(*) FROM study_journal WHERE user_id = ? AND personal_notes IS NOT NULL AND length(personal_notes) > 0", (user_id,))
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

        # 7. /api/whatsapp/preview?user_id=X -> Prévia individual + links de membros e grupos
        if path == "/api/whatsapp/preview":
            c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user_row = c.fetchone()
            if not user_row:
                c.execute("SELECT * FROM users LIMIT 1")
                user_row = c.fetchone()
            user_data = dict(user_row) if user_row else {"id": 1, "name": "Miqueias", "current_day": 1, "phone": ""}

            current_day = int(user_data.get("current_day", 1))
            day_data = next((d for d in BIBLE_PLAN if d["day"] == current_day), BIBLE_PLAN[0])
            matched_books = get_matching_books(day_data.get("tags", []))

            user_name = user_data.get("name", "Amado(a)")
            msg = format_whatsapp_message(day_data, matched_books, user_name)
            phone = user_data.get("phone", "")
            direct_url = get_direct_whatsapp_url(phone, msg)
            group_url = f"https://api.whatsapp.com/send?text={urllib.parse.quote(msg)}"

            # Lista de todos os membros cadastrados
            c.execute("SELECT id, name, phone, avatar_icon, current_day FROM users ORDER BY id ASC")
            members = []
            for m in c.fetchall():
                m_dict = dict(m)
                m_day = next((d for d in BIBLE_PLAN if d["day"] == m_dict["current_day"]), day_data)
                m_msg = format_whatsapp_message(m_day, matched_books, m_dict["name"])
                m_dict["individual_wa_url"] = get_direct_whatsapp_url(m_dict["phone"], m_msg)
                members.append(m_dict)

            conn.close()
            self.send_json({
                "message": msg,
                "direct_url": direct_url,
                "group_url": group_url,
                "members": members,
                "user": user_data,
                "is_logged_in": getattr(whatsapp_bot, 'is_logged_in', lambda: False)()
            })
            return

        # 8. /api/whatsapp/status
        if path == "/api/whatsapp/status":
            conn.close()
            self.send_json({
                "is_logged_in": getattr(whatsapp_bot, 'is_logged_in', lambda: False)(),
                "session_dir": getattr(whatsapp_bot, 'session_dir', '')
            })
            return

        # 9. /api/settings -> Configurações do sistema ou do usuário atual
        if path == "/api/settings":
            c.execute("SELECT key, value FROM settings")
            rows = c.fetchall()
            settings_dict = {row["key"]: row["value"] for row in rows}

            c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            u = c.fetchone()
            if u:
                settings_dict["user_name"] = u["name"]
                settings_dict["whatsapp_number"] = u["phone"] or ""
                settings_dict["current_day"] = str(u["current_day"])
                settings_dict["reminder_time"] = u["reminder_time"] or "07:00"

            conn.close()
            self.send_json(settings_dict)
            return

        conn.close()
        self.send_json({"error": "Rota não encontrada"}, 404)

    # ================= ROTAS POST =================
    def handle_api_post(self, path):
        conn = get_db_connection()
        c = conn.cursor()
        data = self.read_json_body()

        # 1. /api/users -> Cadastrar novo membro/usuário
        if path == "/api/users":
            try:
                name = data.get("name", "").strip()
                phone = data.get("phone", "").strip()
                email = data.get("email", "").strip()
                avatar = data.get("avatar_icon", "🕊️")
                current_day = int(data.get("current_day", 1))

                if not name:
                    conn.close()
                    self.send_json({"error": "Nome é obrigatório"}, 400)
                    return

                c.execute("""
                INSERT INTO users (name, phone, email, avatar_icon, current_day)
                VALUES (?, ?, ?, ?, ?)
                """, (name, phone, email, avatar, current_day))
                new_id = c.lastrowid
                conn.commit()
                conn.close()
                self.send_json({"success": True, "id": new_id, "message": f"Membro {name} cadastrado com sucesso!"})
                return
            except Exception as e:
                conn.close()
                self.send_json({"error": str(e)}, 500)
                return

        # 2. /api/day/<id>/complete -> Alternar status de conclusão do usuário X
        if path.startswith("/api/day/") and path.endswith("/complete"):
            try:
                user_id = int(data.get("user_id", 1))
                parts = path.split("/")
                day_num = int(parts[3])

                c.execute("SELECT status FROM study_journal WHERE user_id = ? AND day_number = ?", (user_id, day_num))
                row = c.fetchone()
                current_status = row["status"] if row else "pending"
                new_status = "pending" if current_status == "completed" else "completed"
                completed_at = datetime.now().isoformat() if new_status == "completed" else None

                c.execute("DELETE FROM study_journal WHERE user_id = ? AND day_number = ?", (user_id, day_num))
                c.execute("""
                INSERT INTO study_journal (user_id, day_number, status, completed_at)
                VALUES (?, ?, ?, ?)
                """, (user_id, day_num, new_status, completed_at))

                if new_status == "completed":
                    next_day = min(day_num + 1, 365)
                    c.execute("UPDATE users SET current_day = ? WHERE id = ?", (next_day, user_id))

                conn.commit()
                conn.close()
                self.send_json({"success": True, "new_status": new_status, "completed_at": completed_at})
                return
            except Exception as e:
                conn.close()
                self.send_json({"error": str(e)}, 500)
                return

        # 3. /api/day/<id>/notes -> Salvar anotações do estudo do usuário X
        if path.startswith("/api/day/") and path.endswith("/notes"):
            try:
                user_id = int(data.get("user_id", 1))
                parts = path.split("/")
                day_num = int(parts[3])
                notes = data.get("personal_notes", "")
                favorite_verse = data.get("favorite_verse", "")

                c.execute("SELECT id FROM study_journal WHERE user_id = ? AND day_number = ?", (user_id, day_num))
                row = c.fetchone()
                if row:
                    c.execute("""
                    UPDATE study_journal SET personal_notes = ?, favorite_verse = ?
                    WHERE user_id = ? AND day_number = ?
                    """, (notes, favorite_verse, user_id, day_num))
                else:
                    c.execute("""
                    INSERT INTO study_journal (user_id, day_number, personal_notes, favorite_verse)
                    VALUES (?, ?, ?, ?)
                    """, (user_id, day_num, notes, favorite_verse))

                conn.commit()
                conn.close()
                self.send_json({"success": True, "message": "Anotações salvas com sucesso!"})
                return
            except Exception as e:
                conn.close()
                self.send_json({"error": str(e)}, 500)
                return

        # 4. /api/books -> Adicionar livro
        if path == "/api/books":
            try:
                title = data.get("title", "").strip()
                author = data.get("author", "").strip()
                if not title or not author:
                    conn.close()
                    self.send_json({"error": "Título e autor são obrigatórios"}, 400)
                    return

                c.execute("""
                INSERT INTO books (title, author, publisher, year, themes, summary, cover_color, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (title, author, data.get("publisher", ""), data.get("year"), data.get("themes", ""),
                      data.get("summary", ""), data.get("cover_color", "#1e3a8a"), data.get("notes", "")))
                new_id = c.lastrowid
                conn.commit()
                conn.close()
                self.send_json({"success": True, "id": new_id, "message": "Livro cadastrado com sucesso!"})
                return
            except Exception as e:
                conn.close()
                self.send_json({"error": str(e)}, 500)
                return

        # 5. /api/whatsapp/broadcast -> Disparar envio para todos os membros
        if path == "/api/whatsapp/broadcast":
            c.execute("SELECT * FROM users WHERE phone IS NOT NULL AND length(phone) >= 8")
            users = [dict(r) for r in c.fetchall()]
            conn.close()

            if not users:
                self.send_json({"error": "Nenhum membro possui número de telefone cadastrado."}, 400)
                return

            def broadcast_thread():
                for u in users:
                    u_day = next((d for d in BIBLE_PLAN if d["day"] == u["current_day"]), BIBLE_PLAN[0])
                    u_books = get_matching_books(u_day.get("tags", []))
                    u_msg = format_whatsapp_message(u_day, u_books, u["name"])
                    try:
                        whatsapp_bot.send_message(u["phone"], u_msg, headless=True)
                    except Exception as err:
                        print(f"Erro ao enviar para {u['name']}: {err}")

            threading.Thread(target=broadcast_thread, daemon=True).start()
            self.send_json({"success": True, "message": f"Envio iniciado para {len(users)} membros!"})
            return

        # 6. /api/settings -> Salvar configurações
        if path == "/api/settings":
            for k, v in data.items():
                c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (str(k), str(v)))

            user_id = int(data.get("user_id", 1))
            name = data.get("user_name")
            phone = data.get("whatsapp_number")
            c_day = data.get("current_day")
            r_time = data.get("reminder_time")
            if name or phone is not None or c_day:
                c.execute("""
                UPDATE users SET 
                    name = COALESCE(?, name),
                    phone = COALESCE(?, phone),
                    current_day = COALESCE(?, current_day),
                    reminder_time = COALESCE(?, reminder_time)
                WHERE id = ?
                """, (name, phone, int(c_day) if c_day else None, r_time, user_id))

            conn.commit()
            conn.close()
            self.send_json({"success": True, "message": "Configurações salvas!"})
            return

        # 7. /api/whatsapp/login -> Abrir bot local para login
        if path == "/api/whatsapp/login":
            conn.close()
            def run_login():
                whatsapp_bot.open_for_login()
            threading.Thread(target=run_login, daemon=True).start()
            self.send_json({"success": True, "message": "Iniciando sessão do WhatsApp Web..."})
            return

        # 8. /api/whatsapp/send-now -> Disparar envio agora
        if path == "/api/whatsapp/send-now":
            user_id = int(data.get("user_id", 1))
            c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            u = c.fetchone()
            if not u or not u["phone"]:
                conn.close()
                self.send_json({"error": "Nenhum telefone cadastrado para o perfil ativo."}, 400)
                return
            u_day = next((d for d in BIBLE_PLAN if d["day"] == u["current_day"]), BIBLE_PLAN[0])
            u_books = get_matching_books(u_day.get("tags", []))
            u_msg = format_whatsapp_message(u_day, u_books, u["name"])
            conn.close()
            def run_send():
                whatsapp_bot.send_message(u["phone"], u_msg, headless=True)
            threading.Thread(target=run_send, daemon=True).start()
            self.send_json({"success": True, "message": f"Envio iniciado para {u['name']}!"})
            return

        conn.close()
        self.send_json({"error": "Endpoint não encontrado"}, 404)

    # ================= ROTAS PUT =================
    def handle_api_put(self, path):
        conn = get_db_connection()
        c = conn.cursor()
        data = self.read_json_body()

        # /api/users/<id> -> Atualizar membro/usuário
        if path.startswith("/api/users/"):
            try:
                user_id = int(path.split("/api/users/")[1])
                name = data.get("name", "").strip()
                phone = data.get("phone", "").strip()
                email = data.get("email", "").strip()
                avatar = data.get("avatar_icon", "🕊️")
                current_day = int(data.get("current_day", 1))

                c.execute("""
                UPDATE users SET name = ?, phone = ?, email = ?, avatar_icon = ?, current_day = ?
                WHERE id = ?
                """, (name, phone, email, avatar, current_day, user_id))
                conn.commit()
                conn.close()
                self.send_json({"success": True, "message": "Perfil atualizado com sucesso!"})
                return
            except Exception as e:
                conn.close()
                self.send_json({"error": str(e)}, 500)
                return

        # /api/books/<id> -> Atualizar livro
        if path.startswith("/api/books/"):
            try:
                book_id = int(path.split("/api/books/")[1])
                c.execute("""
                UPDATE books SET
                    title = ?, author = ?, publisher = ?, year = ?,
                    themes = ?, summary = ?, cover_color = ?, notes = ?
                WHERE id = ?
                """, (data.get("title", "").strip(), data.get("author", "").strip(), data.get("publisher", ""),
                      data.get("year"), data.get("themes", ""), data.get("summary", ""),
                      data.get("cover_color", "#1e3a8a"), data.get("notes", ""), book_id))
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

        # /api/users/<id> -> Remover membro
        if path.startswith("/api/users/"):
            try:
                user_id = int(path.split("/api/users/")[1])
                c.execute("SELECT COUNT(*) FROM users")
                if c.fetchone()[0] <= 1:
                    conn.close()
                    self.send_json({"error": "Não é possível excluir o único perfil existente."}, 400)
                    return
                c.execute("DELETE FROM users WHERE id = ?", (user_id,))
                c.execute("DELETE FROM study_journal WHERE user_id = ?", (user_id,))
                conn.commit()
                conn.close()
                self.send_json({"success": True, "message": "Membro removido!"})
                return
            except Exception as e:
                conn.close()
                self.send_json({"error": str(e)}, 500)
                return

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


class ThreadedHTTPServer(http.server.ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True

def run_server():
    os.chdir(BASE_DIR)
    with ThreadedHTTPServer((HOST, PORT), BibleStudyHandler) as httpd:
        print("=" * 60)
        print(f"📖 JORNADA BÍBLICA 365 MULTI-USUÁRIO - SERVIDOR ATIVO")
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
