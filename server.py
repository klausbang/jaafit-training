import json, os, sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

sys.stdout.reconfigure(encoding='utf-8')

DATA_FILE = 'jaafit_userdata.json'
DEFAULT_DATA = {
    'users': {
        'Klaus': {'program_id': 'prog4', 'workouts': []},
        'Dorte': {'program_id': 'prog2', 'workouts': []}
    }
}

PERSONAL_FILE = 'jaafit_personaldata.json'
DEFAULT_PERSONAL = {
    'personal_exercises': [],
    'personal_programs': [],
    'exercise_descriptions': {}
}

def read_json(path, default):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return json.dumps(default, ensure_ascii=False, indent=2)

def write_json(path, body_bytes):
    parsed = json.loads(body_bytes.decode('utf-8'))
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(parsed, f, ensure_ascii=False, indent=2)

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/userdata':
            data = read_json(DATA_FILE, DEFAULT_DATA)
            self._json_response(200, data.encode('utf-8'))
        elif self.path == '/api/personaldata':
            data = read_json(PERSONAL_FILE, DEFAULT_PERSONAL)
            self._json_response(200, data.encode('utf-8'))
        else:
            super().do_GET()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        if self.path == '/api/userdata':
            write_json(DATA_FILE, body)
            print(f'Saved: {DATA_FILE}')
            self._json_response(200, b'{"ok":true}')
        elif self.path == '/api/personaldata':
            write_json(PERSONAL_FILE, body)
            print(f'Saved: {PERSONAL_FILE}')
            self._json_response(200, b'{"ok":true}')
        else:
            self.send_response(404)
            self.end_headers()

    def _json_response(self, status, body):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        if args and '/api/' in str(args[0]) and 'POST' in str(args[0]):
            pass  # already printed in do_POST

if __name__ == '__main__':
    port = 8080
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = HTTPServer(('localhost', port), Handler)
    print(f'JAAFIT server: http://localhost:{port}/')
    print(f'Brugerdata:    {DATA_FILE}')
    print(f'Personlig:     {PERSONAL_FILE}')
    server.serve_forever()
