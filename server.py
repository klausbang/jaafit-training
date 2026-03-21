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

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/userdata':
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = f.read()
            else:
                data = json.dumps(DEFAULT_DATA, ensure_ascii=False, indent=2)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(data.encode('utf-8'))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/userdata':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            # Pretty-print for readability
            parsed = json.loads(body.decode('utf-8'))
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(parsed, f, ensure_ascii=False, indent=2)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Only log API writes
        if args and '/api/userdata' in str(args[0]) and 'POST' in str(args[0]):
            print(f'Saved: {DATA_FILE}')

if __name__ == '__main__':
    port = 8080
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = HTTPServer(('localhost', port), Handler)
    print(f'JAAFIT server: http://localhost:{port}/')
    print(f'Brugerdata:    {DATA_FILE}')
    server.serve_forever()
