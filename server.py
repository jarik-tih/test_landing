from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
from pathlib import Path
import json, re, sqlite3, time

ROOT = Path(__file__).parent
DB = ROOT / 'data' / 'leads.sqlite3'
PHONE_RE = re.compile(r'^(?:\+375|80)\s*\(?\d{2}\)?[\s-]*\d{3}[\s-]*\d{2}[\s-]*\d{2}$')

def init_db():
    with sqlite3.connect(DB) as con:
        con.execute('''CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, phone TEXT NOT NULL,
            interest TEXT NOT NULL, comment TEXT, source TEXT, ad_source TEXT, medium TEXT, campaign TEXT,
            content TEXT, term TEXT, landing TEXT, referrer TEXT, created_at INTEGER NOT NULL,
            phone_key TEXT NOT NULL)''')
        con.execute('CREATE INDEX IF NOT EXISTS leads_phone_time ON leads(phone_key, created_at)')
        columns = {row[1] for row in con.execute('PRAGMA table_info(leads)')}
        if 'ad_source' not in columns:
            con.execute('ALTER TABLE leads ADD COLUMN ad_source TEXT')

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_POST(self):
        if urlparse(self.path).path != '/api/lead':
            return self.reply(404, {'ok': False, 'message': 'Адрес не найден.'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if size > 20000: return self.reply(413, {'ok': False, 'message': 'Слишком большой запрос.'})
            body = json.loads(self.rfile.read(size))
            name = str(body.get('name', '')).strip()[:100]
            phone = re.sub(r'\s+', '', str(body.get('phone', '')))
            interest = str(body.get('interest', '')).strip()
            if not name: return self.reply(400, {'ok': False, 'field': 'name', 'message': 'Укажите, пожалуйста, имя.'})
            if not PHONE_RE.fullmatch(phone): return self.reply(400, {'ok': False, 'field': 'phone', 'message': 'Проверьте номер: нужен белорусский номер, например +375 29 123-45-67.'})
            if interest not in ('subscription', 'order', 'question'):
                return self.reply(400, {'ok': False, 'message': 'Выберите, что вас интересует.'})
            digits = re.sub(r'\D', '', phone)
            key = digits[-9:]
            now = int(time.time())
            with sqlite3.connect(DB, timeout=5) as con:
                recent = con.execute('SELECT id FROM leads WHERE phone_key=? AND created_at>? LIMIT 1', (key, now-600)).fetchone()
                if recent: return self.reply(409, {'ok': False, 'message': 'Мы уже получили заявку с этого номера. Скоро вам позвоним.'})
                con.execute('''INSERT INTO leads(name,phone,interest,comment,source,ad_source,medium,campaign,content,term,landing,referrer,created_at,phone_key)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (name, phone, interest, str(body.get('comment','')).strip()[:2000],
                    str(body.get('source','direct_form'))[:100], str(body.get('utm_source',''))[:200], str(body.get('utm_medium',''))[:200], str(body.get('utm_campaign',''))[:200],
                    str(body.get('utm_content',''))[:200], str(body.get('utm_term',''))[:200], str(body.get('landing',''))[:1000],
                    str(body.get('referrer',''))[:1000], now, key))
            return self.reply(201, {'ok': True, 'message': 'Заявка отправлена. Мы позвоним в ближайшее время.'})
        except (ValueError, json.JSONDecodeError):
            return self.reply(400, {'ok': False, 'message': 'Не удалось прочитать данные. Обновите страницу и попробуйте снова.'})
        except sqlite3.Error:
            return self.reply(503, {'ok': False, 'message': 'Сейчас не получается отправить заявку. Позвоните нам: +375 29 123-45-67.'})

    def reply(self, status, data):
        payload = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(payload))); self.send_header('Cache-Control','no-store'); self.end_headers(); self.wfile.write(payload)

if __name__ == '__main__':
    init_db()
    print('Кварта: http://localhost:8000')
    ThreadingHTTPServer(('0.0.0.0', 8000), Handler).serve_forever()
