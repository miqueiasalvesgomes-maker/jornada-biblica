"""
WSGI Application para PythonAnywhere e Servidores em Nuvem
Permite rodar a Jornada Bíblica 365 diretamente no PythonAnywhere sem precisar instalar nenhuma biblioteca adicional (100% biblioteca padrão do Python).
"""

import os
import sys
import json
import sqlite3
import urllib.parse
from datetime import datetime

# Garante que o diretório do projeto está no path do Python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

STATIC_DIR = os.path.join(BASE_DIR, "static")
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "study.db")
JSON_PLAN_PATH = os.path.join(DATA_DIR, "bible_plan.json")

# Se o banco ou json não existirem, inicializa
if not os.path.exists(JSON_PLAN_PATH) or not os.path.exists(DB_PATH):
    import generate_plan
    generate_plan.init_database_and_json()

with open(JSON_PLAN_PATH, "r", encoding="utf-8") as f:
    BIBLE_PLAN = json.load(f)

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


def application(environ, start_response):
    """Função WSGI padrão chamada pelo PythonAnywhere."""
    method = environ.get("REQUEST_METHOD", "GET").upper()
    path = environ.get("PATH_INFO", "/")

    # Helper para responder JSON
    def send_json(data, status="200 OK"):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        headers = [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(body))),
            ("Access-Control-Allow-Origin", "*"),
            ("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS"),
            ("Access-Control-Allow-Headers", "Content-Type")
        ]
        start_response(status, headers)
        return [body]

    # Preflight CORS
    if method == "OPTIONS":
        headers = [
            ("Content-Type", "text/plain"),
            ("Access-Control-Allow-Origin", "*"),
            ("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS"),
            ("Access-Control-Allow-Headers", "Content-Type")
        ]
        start_response("200 OK", headers)
        return [b""]

    # Leitura do body JSON em POST/PUT
    def get_json_body():
        try:
            content_length = int(environ.get("CONTENT_LENGTH", 0) or 0)
            if content_length > 0:
                raw = environ["wsgi.input"].read(content_length)
                return json.loads(raw.decode("utf-8"))
        except Exception:
            pass
        return {}

    # ================= ROTAS DE API =================
    if path.startswith("/api/"):
        conn = get_db_connection()
        c = conn.cursor()

        # GET /api/plan
        if path == "/api/plan" and method == "GET":
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
            return send_json(merged_plan)

        # GET /api/today
        if path == "/api/today" and method == "GET":
            settings = get_settings()
            current_day = int(settings.get("current_day", "1"))
            day_data = next((d for d in BIBLE_PLAN if d["day"] == current_day), BIBLE_PLAN[0])
            c.execute("SELECT * FROM study_journal WHERE day_number = ?", (current_day,))
            row = c.fetchone()
            progress = dict(row) if row else {"status": "pending", "personal_notes": "", "favorite_verse": ""}
            matched_books = get_matching_books(day_data.get("tags", []))
            conn.close()

            return send_json({
                "day_data": day_data,
                "progress": progress,
                "recommended_books": matched_books,
                "settings": settings
            })

        # GET /api/day/<id>
        if path.startswith("/api/day/") and not path.endswith("/complete") and not path.endswith("/notes") and method == "GET":
            try:
                day_num = int(path.split("/api/day/")[1])
                day_data = next((d for d in BIBLE_PLAN if d["day"] == day_num), None)
                if not day_data:
                    conn.close()
                    return send_json({"error": "Dia não encontrado"}, "404 Not Found")
                c.execute("SELECT * FROM study_journal WHERE day_number = ?", (day_num,))
                row = c.fetchone()
                progress = dict(row) if row else {"status": "pending", "personal_notes": "", "favorite_verse": ""}
                matched_books = get_matching_books(day_data.get("tags", []))
                conn.close()
                return send_json({
                    "day_data": day_data,
                    "progress": progress,
                    "recommended_books": matched_books
                })
            except Exception as e:
                conn.close()
                return send_json({"error": str(e)}, "400 Bad Request")

        # POST /api/day/<id>/complete
        if path.startswith("/api/day/") and path.endswith("/complete") and method == "POST":
            try:
                day_num = int(path.split("/")[3])
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

                if new_status == "completed":
                    next_day = min(day_num + 1, 365)
                    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('current_day', ?)", (str(next_day),))

                conn.commit()
                conn.close()
                return send_json({"success": True, "new_status": new_status, "completed_at": completed_at})
            except Exception as e:
                conn.close()
                return send_json({"error": str(e)}, "500 Internal Server Error")

        # POST /api/day/<id>/notes
        if path.startswith("/api/day/") and path.endswith("/notes") and method == "POST":
            try:
                day_num = int(path.split("/")[3])
                data = get_json_body()
                c.execute("""
                INSERT INTO study_journal (day_number, personal_notes, favorite_verse)
                VALUES (?, ?, ?)
                ON CONFLICT(day_number) DO UPDATE SET
                    personal_notes = excluded.personal_notes,
                    favorite_verse = excluded.favorite_verse
                """, (day_num, data.get("personal_notes", ""), data.get("favorite_verse", "")))
                conn.commit()
                conn.close()
                return send_json({"success": True, "message": "Anotações salvas com sucesso!"})
            except Exception as e:
                conn.close()
                return send_json({"error": str(e)}, "500 Internal Server Error")

        # /api/books
        if path == "/api/books":
            if method == "GET":
                c.execute("SELECT * FROM books ORDER BY id DESC")
                books = [dict(row) for row in c.fetchall()]
                conn.close()
                return send_json(books)
            elif method == "POST":
                data = get_json_body()
                title = data.get("title", "").strip()
                author = data.get("author", "").strip()
                if not title or not author:
                    conn.close()
                    return send_json({"error": "Título e autor obrigatórios"}, "400 Bad Request")
                c.execute("""
                INSERT INTO books (title, author, publisher, year, themes, summary, cover_color, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (title, author, data.get("publisher", ""), data.get("year"), data.get("themes", ""),
                      data.get("summary", ""), data.get("cover_color", "#1e3a8a"), data.get("notes", "")))
                new_id = c.lastrowid
                conn.commit()
                conn.close()
                return send_json({"success": True, "id": new_id, "message": "Livro cadastrado com sucesso!"})

        # PUT ou DELETE /api/books/<id>
        if path.startswith("/api/books/"):
            try:
                book_id = int(path.split("/api/books/")[1])
                if method == "PUT":
                    data = get_json_body()
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
                    return send_json({"success": True, "message": "Livro atualizado com sucesso!"})
                elif method == "DELETE":
                    c.execute("DELETE FROM books WHERE id = ?", (book_id,))
                    conn.commit()
                    conn.close()
                    return send_json({"success": True, "message": "Livro removido com sucesso!"})
            except Exception as e:
                conn.close()
                return send_json({"error": str(e)}, "500 Internal Server Error")

        # GET /api/stats
        if path == "/api/stats" and method == "GET":
            c.execute("SELECT day_number, status, completed_at FROM study_journal WHERE status = 'completed'")
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

            today_day = int(get_settings().get("current_day", "1"))
            streak = 0
            check_day = today_day
            while check_day in completed_day_nums and check_day > 0:
                streak += 1
                check_day -= 1

            c.execute("SELECT COUNT(*) FROM study_journal WHERE personal_notes IS NOT NULL AND length(personal_notes) > 0")
            notes_count = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM books")
            books_count = c.fetchone()[0]
            conn.close()

            return send_json({
                "completed_count": completed_count,
                "total_days": total_days,
                "percentage": percent,
                "streak": streak,
                "ot_completed": ot_completed,
                "nt_completed": nt_completed,
                "notes_count": notes_count,
                "books_count": books_count
            })

        # /api/settings
        if path == "/api/settings":
            if method == "GET":
                conn.close()
                return send_json(get_settings())
            elif method == "POST":
                data = get_json_body()
                for k, v in data.items():
                    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (str(k), str(v)))
                conn.commit()
                conn.close()
                return send_json({"success": True, "message": "Configurações salvas!"})

        # /api/whatsapp/preview
        if path == "/api/whatsapp/preview" and method == "GET":
            settings = get_settings()
            current_day = int(settings.get("current_day", "1"))
            day_data = next((d for d in BIBLE_PLAN if d["day"] == current_day), BIBLE_PLAN[0])
            matched_books = get_matching_books(day_data.get("tags", []))
            conn.close()

            user_name = settings.get("user_name", "Amado(a)")
            msg = format_whatsapp_message(day_data, matched_books, user_name)
            phone = settings.get("whatsapp_number", "")
            direct_url = get_direct_whatsapp_url(phone, msg)
            return send_json({
                "message": msg,
                "direct_url": direct_url,
                "is_logged_in": False
            })

        # /api/whatsapp/status
        if path == "/api/whatsapp/status" and method == "GET":
            conn.close()
            return send_json({"is_logged_in": False, "session_dir": ""})

        conn.close()
        return send_json({"error": "Endpoint não encontrado"}, "404 Not Found")

    # ================= ARQUIVOS ESTÁTICOS =================
    # Mapeamento do arquivo a servir
    file_map = {
        "/": ("index.html", "text/html; charset=utf-8"),
        "/index.html": ("index.html", "text/html; charset=utf-8"),
        "/style.css": ("style.css", "text/css; charset=utf-8"),
        "/app.js": ("app.js", "application/javascript; charset=utf-8"),
        "/manifest.json": ("manifest.json", "application/json; charset=utf-8"),
        "/sw.js": ("sw.js", "application/javascript; charset=utf-8")
    }

    if path in file_map:
        filename, content_type = file_map[path]
        filepath = os.path.join(STATIC_DIR, filename)
        if os.path.exists(filepath):
            with open(filepath, "rb") as f:
                content = f.read()
            headers = [
                ("Content-Type", content_type),
                ("Content-Length", str(len(content))),
                ("Cache-Control", "no-cache")
            ]
            start_response("200 OK", headers)
            return [content]

    # Se não encontrou, 404
    start_response("404 Not Found", [("Content-Type", "text/plain")])
    return [b"404 Not Found"]


# Permite testar localmente rodando py wsgi.py
if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    port = int(os.environ.get("PORT", 8000))
    print(f"Testando WSGI em http://localhost:{port}")
    httpd = make_server("0.0.0.0", port, application)
    httpd.serve_forever()
