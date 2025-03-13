from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import pathlib
import mimetypes
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import os


class HttpHandler(BaseHTTPRequestHandler):

    env = Environment(loader=FileSystemLoader("template"))

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        print(data)

        data_parse = urllib.parse.unquote_plus(data.decode())
        print(data_parse)

        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        print(data_dict)

        # Шлях до файлу збереження
        storage_file = "storage/data.json"

        # Отримання поточного часу як ключа
        timestamp = datetime.now().isoformat()

        # Завантажуємо існуючі дані, якщо файл є
        try:
            with open(storage_file, "r", encoding="utf-8") as file:
                existing_data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = {}

        # Додаємо нове повідомлення
        existing_data[timestamp] = data_dict

        with open(storage_file, "w", encoding="utf-8") as file:
            json.dump(existing_data, file, ensure_ascii=False, indent=4)

        # Відповідь серверу
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            self.send_html_file("index.html")
        elif pr_url.path == "/message":
            self.send_html_file("message.html")
        elif pr_url.path == "/read":
            self.send_messages_page()
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("error.html", 404)

    def send_messages_page(self):
        storage_file = "storage/data.json"
        try:
            with open(storage_file, "r", encoding="utf-8") as file:
                messages = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            messages = {}

        template = self.env.get_template("read.html")
        html_content = template.render(data=messages)

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html_content.encode("utf-8"))

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(os.path.join("template", filename), "rb") as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ("", 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == "__main__":
    run()
