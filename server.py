from http.server import SimpleHTTPRequestHandler, HTTPServer

import json

from base_controller import TaskBase


class MyHandler(SimpleHTTPRequestHandler):

    BASE = TaskBase('tasks.txt')

    def do_GET(self):
        if self.path == '/tasks':
            try:
                self.send_tasks()
            except FileNotFoundError:
                self.send_404()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/tasks':
            try:
                data = self.parse_POST_body()
                new_task = data.get('task')
                if not new_task:
                    raise ValueError('Пустое поле task')

                self.BASE.append_task(new_task)
                tasks = self.BASE.json(as_bytes=True)
                self.send_json_answer(tasks)

            except FileNotFoundError:
                self.send_404()

            except (json.JSONDecodeError, ValueError) as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

    def do_DELETE(self):
        if self.path == '/tasks':
            self.BASE.clear_all()
            self.send_json_answer(code=204)

        elif self.path.startswith('/tasks'):
            self.BASE.delete_by_id(self.parse_path()[-1])
            self.send_tasks()

    def do_PUT(self):
        if self.path.startswith('/tasks'):
            if self.parse_path()[-1] == 'status':
                self.BASE.change_status_by_id(self.parse_path()[-2])
                self.send_tasks()

    def parse_POST_body(self):
        if self.command != 'POST':
            raise ValueError('Метод parse_POST_body должен использоваться только для POST-запросов')

        content_length = self.headers.get('Content-Length', 0)
        content = self.rfile.read(int(content_length)).decode()

        return json.loads(content)

    def parse_path(self):
        return self.path.split('/')

    def send_json_answer(self, content=None, code=204):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        if content:
            self.wfile.write(content)

    def send_tasks(self):
        tasks = self.BASE.json(as_bytes=True)
        self.send_json_answer(tasks, code=200)

    def send_404(self):
        self.send_response(404)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(
            json.dumps({"error": "Resource not found"}).encode('utf-8')
            )


if __name__ == "__main__":
    server = HTTPServer(('localhost', 8000), MyHandler)
    server.serve_forever()
