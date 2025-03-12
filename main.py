from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import pathlib
import mimetypes
import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader


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
        with open(filename, "rb") as fd:
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

# from http.server import HTTPServer, BaseHTTPRequestHandler
# import urllib.parse
# import pathlib
# import mimetypes
# import os
# import json
# from datetime import datetime


# class HttpHandler(BaseHTTPRequestHandler):
#     def do_POST(self):
#         if self.path != "/message":
#             self.send_response(404)
#             self.end_headers()
#             return

#         data = self.rfile.read(int(self.headers["Content-Length"]))
#         print(data)

#         data_parse = urllib.parse.unquote_plus(data.decode())
#         print(data_parse)

#         data_dict = {
#             key: value for key, value in [el.split("=") for el in data_parse.split("&")]
#         }
#         print(data_dict)

#         storage_dir = "storage"
#         storage_file = os.path.join(storage_dir, "data.json")

#         if not os.path.exists(storage_dir):
#             os.makedirs(storage_dir)

#         timestamp = datetime.now().isoformat()

#         try:
#             with open(storage_file, "r", encoding="utf-8") as file:
#                 existing_data = json.load(file)
#         except (FileNotFoundError, json.JSONDecodeError):
#             existing_data = {}

#         existing_data[timestamp] = data_dict

#         with open(storage_file, "w", encoding="utf-8") as file:
#             json.dump(existing_data, file, ensure_ascii=False, indent=4)

#         self.send_response(302)
#         self.send_header("Location", "/")
#         self.end_headers()

#     def do_GET(self):
#         pr_url = urllib.parse.urlparse(self.path)
#         if pr_url.path == "/":
#             self.send_html_file("index.html")
#         elif pr_url.path == "/message":
#             self.send_html_file("message.html")
#         else:
#             file_path = pathlib.Path(pr_url.path[1:])
#             if file_path.exists():
#                 self.send_static()
#             else:
#                 self.send_html_file("error.html", 404)

#     def send_html_file(self, filename, status=200):
#         self.send_response(status)
#         self.send_header("Content-type", "text/html")
#         self.end_headers()
#         try:
#             with open(filename, "rb") as fd:
#                 self.wfile.write(fd.read())
#         except FileNotFoundError:
#             self.send_error(404, "File not found")

#     def send_static(self):
#         file_path = f".{self.path}"
#         self.send_response(200)
#         mt = mimetypes.guess_type(file_path)
#         self.send_header("Content-type", mt[0] if mt else "application/octet-stream")
#         self.end_headers()
#         with open(file_path, "rb") as file:
#             self.wfile.write(file.read())


# def run(server_class=HTTPServer, handler_class=HttpHandler):
#     server_address = ("", 3000)
#     http = server_class(server_address, handler_class)
#     print("Starting server on port 3000...")
#     try:
#         http.serve_forever()
#     except KeyboardInterrupt:
#         print("\nShutting down server.")
#         http.server_close()


# if __name__ == "__main__":
#     run()
