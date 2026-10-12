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
import mimetypes
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

def get_pastoral_focus_for_day(day_data):
    """Gera uma conexão pastoral devocional diária com o livro de cabeceira 'O Pastor Pentecostal' (CPAD)."""
    tags = [t.lower() for t in day_data.get("tags", [])]

    if any(k in tags for k in ["oração", "intercessão", "salmos", "intimidade"]):
        return {
            "topic": "A Vida Devocional e Oração do Líder",
            "quote": "O pastor e obreiro pentecostal deve ser, acima de tudo, uma pessoa de oração fervorosa e joelhos dobrados.",
            "chapter_ref": "Capítulo 4: O Pastor e a Vida de Oração Fervorosa"
        }
    elif any(k in tags for k in ["espírito santo", "unção", "dons", "pentecostes"]):
        return {
            "topic": "O Batismo e a Unção no Espírito Santo",
            "quote": "O ministério cristão só alcança autoridade duradoura quando exercido sob o revestimento de poder e os dons do Espírito Santo.",
            "chapter_ref": "Capítulo 2: A Teologia Pentecostal e a Unção Ministerial"
        }
    elif any(k in tags for k in ["liderança", "chamado", "vocação", "propósito"]):
        return {
            "topic": "O Chamado Divino e a Vocação Ministerial",
            "quote": "A vocação pastoral não é uma profissão secular, mas uma santa convocação divina para apascentar o povo com amor e zelo.",
            "chapter_ref": "Capítulo 1: O Chamado Divino e a Preparação do Ministro"
        }
    elif any(k in tags for k in ["integridade", "santidade", "lei moral"]):
        return {
            "topic": "Integridade Ética e Santidade no Ministério",
            "quote": "A integridade moral e espiritual na vida pessoal e familiar é o verdadeiro alicerce da autoridade espiritual.",
            "chapter_ref": "Capítulo 7: A Integridade do Obreiro e a Vida Familiar"
        }
    elif any(k in tags for k in ["cuidado", "rebanho", "aconselhamento", "família", "graça"]):
        return {
            "topic": "O Cuidado Compassivo do Rebanho",
            "quote": "Apascentar as ovelhas de Cristo exige um coração manso, acolhimento amoroso e paciência pastoral.",
            "chapter_ref": "Capítulo 9: O Aconselhamento Bíblico e o Cuidado das Ovelhas"
        }
    else:
        return {
            "topic": "A Prática Ministerial Fundamentada na Palavra",
            "quote": "Toda liderança e ensino devem fluir da autoridade inerrante das Sagradas Escrituras vivificadas pelo Espírito Santo.",
            "chapter_ref": "Capítulo 3: A Centralidade da Palavra de Deus no Ministério"
        }

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

    def format_whatsapp_message(day_data, books_data=None, user_name="Irmão(ã)", bedside_book=None, pastoral_focus=None):
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
        if bedside_book:
            p_topic = (pastoral_focus or {}).get("topic", "Ministério e Prática Pastoral")
            p_quote = (pastoral_focus or {}).get("quote", "Crescimento contínuo no poder e sabedoria do Espírito Santo.")
            msg_lines.extend([
                "",
                "🛌 *Livro de Travesseiro:* _O Pastor Pentecostal_ (CPAD)",
                f"⚡ *Foco Pastoral:* _{p_topic}_",
                f"_{p_quote}_"
            ])
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
    """Migração automática para garantir suporte a múltiplos usuários, status de leitura e catálogo de livros."""
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

    # 3. Garante colunas estendidas em books
    c.execute("PRAGMA table_info(books)")
    book_columns = [row["name"] for row in c.fetchall()]
    needed_cols = {
        "category": "TEXT DEFAULT 'Geral'",
        "plan_link": "TEXT DEFAULT ''",
        "plan_days": "TEXT DEFAULT ''",
        "cover_image": "TEXT DEFAULT ''",
        "is_bedside": "INTEGER DEFAULT 0"
    }
    for col, col_type in needed_cols.items():
        if col not in book_columns:
            try:
                c.execute(f"ALTER TABLE books ADD COLUMN {col} {col_type}")
            except Exception:
                pass

    # 4. Tabela de Status de Leitura por Usuário (Pendente, Em Andamento, Finalizado)
    c.execute("""
    CREATE TABLE IF NOT EXISTS user_book_status (
        user_id INTEGER NOT NULL,
        book_id INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'Pendente',
        personal_notes TEXT DEFAULT '',
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, book_id)
    )
    """)

    # 5. Sincroniza os 90 livros do catálogo oficial
    try:
        from catalog_data import ALL_BOOKS
        for b in ALL_BOOKS:
            c.execute("SELECT id FROM books WHERE title = ? OR (id = ? AND id <= 90)", (b["title"], b["id"]))
            row = c.fetchone()
            if row:
                book_id = row[0]
                c.execute("""
                UPDATE books SET
                    title = ?, author = ?, publisher = ?, year = ?,
                    category = ?, themes = ?, summary = ?,
                    plan_link = ?, plan_days = ?, cover_image = ?,
                    is_bedside = ?, notes = ?
                WHERE id = ?
                """, (
                    b["title"], b["author"], b["publisher"], b["year"],
                    b["category"], b["themes"], b["summary"],
                    b["plan_link"], b["plan_days"], b["cover_image"],
                    b["is_bedside"], b["notes"], book_id
                ))
            else:
                c.execute("""
                INSERT INTO books (
                    id, title, author, publisher, year, category, themes,
                    summary, plan_link, plan_days, cover_image, is_bedside, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    b["id"], b["title"], b["author"], b["publisher"], b["year"],
                    b["category"], b["themes"], b["summary"],
                    b["plan_link"], b["plan_days"], b["cover_image"],
                    b["is_bedside"], b["notes"]
                ))
        
        # Garante O Pastor Pentecostal em 'Em Andamento' para o usuário 1
        c.execute("SELECT id FROM books WHERE is_bedside = 1 LIMIT 1")
        bedside_row = c.fetchone()
        if bedside_row:
            c.execute("""
            INSERT INTO user_book_status (user_id, book_id, status)
            VALUES (1, ?, 'Em Andamento')
            ON CONFLICT(user_id, book_id) DO NOTHING
            """, (bedside_row[0],))
    except Exception as err:
        print(f"[Aviso] Sincronização do catálogo: {err}")

    conn.commit()
    conn.close()

# Executa migração
init_multiuser_db()


def get_matching_books(tags, user_id=1):
    """Retorna livros da biblioteca que compartilham tags ou temas com a leitura do dia, incluindo status do usuário."""
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
    SELECT b.*,
           COALESCE(ubs.status, 'Pendente') AS reading_status,
           COALESCE(ubs.personal_notes, '') AS user_notes
    FROM books b
    LEFT JOIN user_book_status ubs ON b.id = ubs.book_id AND ubs.user_id = ?
    ORDER BY b.is_bedside DESC, b.id ASC
    """, (user_id,))
    all_books = [dict(row) for row in c.fetchall()]
    conn.close()

    if not tags:
        return all_books[:3]

    matched = []
    tags_lower = [t.lower().strip() for t in tags]

    for book in all_books:
        book_themes = (book.get("themes") or "").lower()
        book_title = (book.get("title") or "").lower()
        book_cat = (book.get("category") or "").lower()
        score = 0
        for tag in tags_lower:
            if tag in book_themes or tag in book_title or tag in book_cat:
                score += 1
        if score > 0:
            matched.append((score, book))

    matched.sort(key=lambda x: x[0], reverse=True)
    results = [item[1] for item in matched]
    return results[:3] if results else all_books[:3]


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
            guessed_type, _ = mimetypes.guess_type(filename)

            if not filename or filename == "index.html":
                filename = "index.html"
                content_type = "text/html; charset=utf-8"
            elif filename.endswith(".css"):
                content_type = "text/css; charset=utf-8"
            elif filename.endswith(".js"):
                content_type = "application/javascript; charset=utf-8"
            elif filename.endswith(".json"):
                content_type = "application/json; charset=utf-8"
            elif guessed_type:
                content_type = guessed_type
            else:
                content_type = "application/octet-stream"

            possible_paths = [
                os.path.join(STATIC_DIR, filename),
                os.path.join(STATIC_DIR, filename.replace("static/", "")),
                os.path.join(BASE_DIR, filename),
                os.path.join(BASE_DIR, "static", filename)
            ]

            # Suporte especial para o livro de cabeceira "O Pastor Pentecostal"
            if "o_pastor_pentecostal" in filename or "pastor pentecostal" in filename:
                possible_paths.extend([
                    os.path.join(STATIC_DIR, "img", "o_pastor_pentecostal.jpg"),
                    os.path.join(BASE_DIR, "o pastor pentecostal.jpeg")
                ])

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
                if filename.endswith(".html") or filename.endswith(".js") or filename.endswith(".css"):
                    self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                    self.send_header("Pragma", "no-cache")
                    self.send_header("Expires", "0")
                else:
                    self.send_header("Cache-Control", "public, max-age=86400")
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
            matched_books = get_matching_books(day_data.get("tags", []), user_id=user_data["id"])

            # Livro de Cabeceira Oficial & Conexão Pastoral Diária
            c.execute("""
            SELECT b.*,
                   COALESCE(ubs.status, 'Em Andamento') AS reading_status,
                   COALESCE(ubs.personal_notes, '') AS user_notes
            FROM books b
            LEFT JOIN user_book_status ubs ON b.id = ubs.book_id AND ubs.user_id = ?
            WHERE b.is_bedside = 1 LIMIT 1
            """, (user_data["id"],))
            bedside_row = c.fetchone()
            if not bedside_row:
                c.execute("""
                SELECT b.*,
                       COALESCE(ubs.status, 'Em Andamento') AS reading_status,
                       COALESCE(ubs.personal_notes, '') AS user_notes
                FROM books b
                LEFT JOIN user_book_status ubs ON b.id = ubs.book_id AND ubs.user_id = ?
                WHERE b.title LIKE '%Pastor Pentecostal%' LIMIT 1
                """, (user_data["id"],))
                bedside_row = c.fetchone()
            bedside_book = dict(bedside_row) if bedside_row else None
            pastoral_focus = get_pastoral_focus_for_day(day_data)
            conn.close()

            self.send_json({
                "day_data": day_data,
                "progress": progress,
                "recommended_books": matched_books,
                "bedside_book": bedside_book,
                "pastoral_focus": pastoral_focus,
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
                matched_books = get_matching_books(day_data.get("tags", []), user_id=user_id)

                c.execute("""
                SELECT b.*,
                       COALESCE(ubs.status, 'Em Andamento') AS reading_status,
                       COALESCE(ubs.personal_notes, '') AS user_notes
                FROM books b
                LEFT JOIN user_book_status ubs ON b.id = ubs.book_id AND ubs.user_id = ?
                WHERE b.is_bedside = 1 LIMIT 1
                """, (user_id,))
                bedside_row = c.fetchone()
                if not bedside_row:
                    c.execute("""
                    SELECT b.*,
                           COALESCE(ubs.status, 'Em Andamento') AS reading_status,
                           COALESCE(ubs.personal_notes, '') AS user_notes
                    FROM books b
                    LEFT JOIN user_book_status ubs ON b.id = ubs.book_id AND ubs.user_id = ?
                    WHERE b.title LIKE '%Pastor Pentecostal%' LIMIT 1
                    """, (user_id,))
                    bedside_row = c.fetchone()
                bedside_book = dict(bedside_row) if bedside_row else None
                pastoral_focus = get_pastoral_focus_for_day(day_data)
                conn.close()

                self.send_json({
                    "day_data": day_data,
                    "progress": progress,
                    "recommended_books": matched_books,
                    "bedside_book": bedside_book,
                    "pastoral_focus": pastoral_focus
                })
                return
            except ValueError:
                conn.close()
                self.send_json({"error": "ID do dia inválido"}, 400)
                return

        # 5. /api/books?user_id=X&status=Y&category=Z -> Lista de livros com status de leitura
        if path == "/api/books":
            status_filter = query.get("status", [None])[0]
            cat_filter = query.get("category", [None])[0]

            sql = """
            SELECT b.*,
                   COALESCE(ubs.status, 'Pendente') AS reading_status,
                   COALESCE(ubs.personal_notes, '') AS user_notes,
                   ubs.updated_at AS status_updated_at
            FROM books b
            LEFT JOIN user_book_status ubs ON b.id = ubs.book_id AND ubs.user_id = ?
            """
            params = [user_id]
            conditions = []
            if status_filter and status_filter != 'all':
                conditions.append("COALESCE(ubs.status, 'Pendente') = ?")
                params.append(status_filter)
            if cat_filter and cat_filter != 'all':
                conditions.append("b.category = ?")
                params.append(cat_filter)

            if conditions:
                sql += " WHERE " + " AND ".join(conditions)

            sql += """
            ORDER BY b.is_bedside DESC,
                     CASE COALESCE(ubs.status, 'Pendente')
                         WHEN 'Em Andamento' THEN 1
                         WHEN 'Pendente' THEN 2
                         WHEN 'Finalizado' THEN 3
                         ELSE 4 END,
                     b.id ASC
            """
            c.execute(sql, params)
            books = [dict(row) for row in c.fetchall()]

            # Contadores de status do usuário ativo
            c.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN COALESCE(ubs.status, 'Pendente') = 'Em Andamento' THEN 1 ELSE 0 END) as in_progress,
                SUM(CASE WHEN COALESCE(ubs.status, 'Pendente') = 'Pendente' THEN 1 ELSE 0 END) as pending,
                SUM(CASE WHEN COALESCE(ubs.status, 'Pendente') = 'Finalizado' THEN 1 ELSE 0 END) as completed
            FROM books b
            LEFT JOIN user_book_status ubs ON b.id = ubs.book_id AND ubs.user_id = ?
            """, (user_id,))
            crow = c.fetchone()
            counts = {
                "total": crow["total"] if crow else 90,
                "in_progress": crow["in_progress"] or 0,
                "pending": crow["pending"] or 0,
                "completed": crow["completed"] or 0
            }

            conn.close()
            self.send_json({
                "books": books,
                "counts": counts
            })
            return

        # 5.1 /api/categories -> Categorias teológicas da biblioteca e seus vínculos com o plano
        if path == "/api/categories":
            c.execute("""
            SELECT category, COUNT(*) as book_count, MIN(plan_link) as plan_link, MIN(plan_days) as plan_days
            FROM books
            GROUP BY category
            ORDER BY 
                CASE category
                    WHEN 'Cabeceira & Ministério Pastoral' THEN 1
                    WHEN 'Antigo Testamento, Pentateuco & Arqueologia' THEN 2
                    WHEN 'Novo Testamento, Evangelhos & Vida de Cristo' THEN 3
                    WHEN 'Teologia Sistemática, Doutrina & Hermenêutica' THEN 4
                    WHEN 'Línguas Originais (Grego & Hebraico)' THEN 5
                    WHEN 'Comentários & Manuais Bíblicos Panorâmicos' THEN 6
                    WHEN 'História da Igreja Cristã' THEN 7
                    WHEN 'Vida Cristã, Oração, Avivamento & Família' THEN 8
                    WHEN 'Missões, Evangelização & Educação Cristã' THEN 9
                    WHEN 'Liderança, Desenvolvimento & Sociedade' THEN 10
                    ELSE 11 END ASC
            """)
            categories = [dict(row) for row in c.fetchall()]
            conn.close()
            self.send_json(categories)
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

            # Livro de cabeceira para mensagem
            c.execute("SELECT * FROM books WHERE is_bedside = 1 LIMIT 1")
            bedside_row = c.fetchone()
            if not bedside_row:
                c.execute("SELECT * FROM books WHERE title LIKE '%Pastor Pentecostal%' LIMIT 1")
                bedside_row = c.fetchone()
            bedside_book = dict(bedside_row) if bedside_row else None
            pastoral_focus = get_pastoral_focus_for_day(day_data)

            user_name = user_data.get("name", "Amado(a)")
            msg = format_whatsapp_message(day_data, matched_books, user_name, bedside_book, pastoral_focus)
            phone = user_data.get("phone", "")
            direct_url = get_direct_whatsapp_url(phone, msg)
            group_url = f"https://api.whatsapp.com/send?text={urllib.parse.quote(msg)}"

            # Lista de todos os membros cadastrados
            c.execute("SELECT id, name, phone, avatar_icon, current_day FROM users ORDER BY id ASC")
            members = []
            for m in c.fetchall():
                m_dict = dict(m)
                m_day = next((d for d in BIBLE_PLAN if d["day"] == m_dict["current_day"]), day_data)
                m_pfocus = get_pastoral_focus_for_day(m_day)
                m_msg = format_whatsapp_message(m_day, matched_books, m_dict["name"], bedside_book, m_pfocus)
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
                INSERT INTO books (title, author, publisher, year, themes, summary, cover_color, cover_image, is_bedside, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (title, author, data.get("publisher", ""), data.get("year"), data.get("themes", ""),
                      data.get("summary", ""), data.get("cover_color", "#1e3a8a"), data.get("cover_image"),
                      int(data.get("is_bedside", 0)), data.get("notes", "")))
                new_id = c.lastrowid
                conn.commit()
                conn.close()
                self.send_json({"success": True, "id": new_id, "message": "Livro cadastrado com sucesso!"})
                return
            except Exception as e:
                conn.close()
                self.send_json({"error": str(e)}, 500)
                return

        # 4.1 /api/books/<id>/bedside -> Definir como Livro de Cabeceira Oficial
        if path.startswith("/api/books/") and path.endswith("/bedside"):
            try:
                parts = path.split("/")
                book_id = int(parts[3])
                c.execute("UPDATE books SET is_bedside = 0")
                c.execute("UPDATE books SET is_bedside = 1 WHERE id = ?", (book_id,))
                conn.commit()
                conn.close()
                self.send_json({"success": True, "message": "Livro definido como Livro de Cabeceira Oficial!"})
                return
            except Exception as e:
                conn.close()
                self.send_json({"error": str(e)}, 500)
                return

        # 4.2 /api/books/<id>/status -> Alterar status de leitura do usuário (Pendente, Em Andamento, Finalizado)
        if path.startswith("/api/books/") and path.endswith("/status"):
            try:
                parts = path.split("/")
                book_id = int(parts[3])
                user_id = int(data.get("user_id", 1))
                new_status = data.get("status", "Pendente").strip()
                notes = data.get("notes")

                if new_status not in ["Pendente", "Em Andamento", "Finalizado"]:
                    new_status = "Pendente"

                c.execute("""
                INSERT INTO user_book_status (user_id, book_id, status, personal_notes, updated_at)
                VALUES (?, ?, ?, COALESCE(?, ''), CURRENT_TIMESTAMP)
                ON CONFLICT(user_id, book_id) DO UPDATE SET
                    status = excluded.status,
                    personal_notes = CASE WHEN ? IS NOT NULL THEN excluded.personal_notes ELSE user_book_status.personal_notes END,
                    updated_at = CURRENT_TIMESTAMP
                """, (user_id, book_id, new_status, notes, notes))
                conn.commit()
                conn.close()
                self.send_json({"success": True, "book_id": book_id, "status": new_status, "user_id": user_id})
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
                    themes = ?, summary = ?, cover_color = ?, cover_image = ?, is_bedside = ?, notes = ?
                WHERE id = ?
                """, (data.get("title", "").strip(), data.get("author", "").strip(), data.get("publisher", ""),
                      data.get("year"), data.get("themes", ""), data.get("summary", ""),
                      data.get("cover_color", "#1e3a8a"), data.get("cover_image"),
                      int(data.get("is_bedside", 0)), data.get("notes", ""), book_id))
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
