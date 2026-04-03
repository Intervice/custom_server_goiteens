from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import pathlib
import mimetypes
import logging
import os

BASE_DIR = pathlib.Path(__file__).parent


logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(BASE_DIR.joinpath("logger.log"), mode="w", encoding="utf-8"),
        logging.StreamHandler()],
)

class MyServerHandler(BaseHTTPRequestHandler):
    
    """Перевизначаємо метод do_GET для обробки запитів"""
    def do_GET(self):
        """
        Тут ви обровляєте всі запити (коли користувач заходить на сайт це теж запит)
        Код нижче розбиває посилання лише на сторінку сайта. Наприклад:
        http://site.com/search_song -> /search_song
        /search_song буде зберігатись в request_link
        
        Також в коді є перевірка, чи не сервер не шукає файл за межами проєкту.
        
        В блоках if-elif-else програма вирішує, яку відповідь дати.
        """
        
        req = self.path
        request_link = urllib.parse.urlparse(req).path
        logging.info(f"Request link: {request_link}")
        current_file_path = pathlib.Path(".").joinpath(request_link[1:])
        logging.info(f"Current file path: {current_file_path}")
        
        root_dir = os.path.realpath(BASE_DIR)
        requested_path = os.path.realpath(os.path.join(root_dir, request_link.lstrip('/')))

        if not requested_path.startswith(root_dir):
            logging.warning(f"ATTACK DETECTED: User tried to access {requested_path}")
            self.send_error(403, "Forbidden: You don't have access to this directory")
            return
        
        
        if request_link == "/" or request_link == "":
            """Показуємо головну сторінку"""
            self.send_html_page("index.html")
        elif request_link == "/search":
            """Показуємо сторінку пошуку"""
            self.send_html_page("search.html")
        elif request_link.startswith('/static/'): 
            self.send_static_file()
        else:
            """Показуємо сторінку з помилкою (сторінки не знайдено)"""
            self.send_html_page("error.html", status=404)
        
    def send_html_page(self, filename, status=200):
        """
        Функція, яка буде передавати сторінки (html-файли) в залежності в запиту
        Параметри: 
            filename: ім'я/адреса html-файлу
            status: код відповіді, за замовч 200 (успішно), при потребі можна
                передати інший код при виклику, але щоб менше писати коду треба так
        
        self - це об'єкт класу, який обробляє всі запити на сервер. 
        Аналогічно до @dp (Dispatcher) в aiogram.
        Об'єкт має методи:
            send_response() -> показує браузеру код відповіді
            send_header() -> вказує який тип даних передається як відповідь
            end_headers() -> вказує, що завершилась передача інформації про відповідь
                після чого буде передано саму відповідь - сторінку (html-файл)
               
        та атрибут:
            wfile -> тут зберігається код сторінки в бінарному вигляді
        Далі відбувається зчитування html-файлу в режимі rb (Read Binary) і 
        відправляє їх в об'єкт self.wfile
        
        Якщо файлу не буде знайдено, означає на сайті такої сторінки немає,
        відповідь буде сторінка (передається рекурсивно) де: Page not Found
        
        """
        logging.info(f"send_html_page received file: {filename}, status: {status}")
        
        try:
            file_path = BASE_DIR.joinpath('pages', filename)
            with open(file_path, "rb") as page_file:
                self.send_response(status)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(page_file.read())
        except FileNotFoundError:
            if filename == 'error.html':
                self.send_error(404, "Page Not Found")
            else:
                self.send_html_page('error.html', 404)
        
    def send_static_file(self):
        """
        Функція, що призначеня для відкриття статичних файлів, зчитування і
        передачі з них інформації у відповідь на запит.
        
        Виконується додаткова перевірка, чи файл який шукає сервер не знаходиться
        поза проєктом.
        
        Тип файлу автоматично розпізнається і надсилається у відповідь, якщо тип
        не визначено, результат надсилається як звичайний текст
        """

        try:
            file_path = BASE_DIR / self.path.lstrip('/')
        
            logging.info(f"Looking for static file by path: {file_path}")
                
            with open(file_path, 'rb') as file:
                self.send_response(200)
                
                file_type = mimetypes.guess_type(self.path)
                if file_type and file_type[0]:
                    self.send_header("Content-type", file_type[0])
                else:
                    self.send_header("Content-type", "text/plain")
                    
                self.end_headers()
                self.wfile.write(file.read())
                
        except FileNotFoundError:
            logging.error(f"File not found: {file_path}")
            self.send_error(404, "Static file not found")
    

def run_server(server_class=HTTPServer, handler_class=MyServerHandler):
    """
    Функція, яка здійснює запуск сервера використовуючи клас вище 
    як хендлер (обробник) запитів
    Опис:
    server_address -> просто робимо лінк і порт на якому буде працювати сервер
    handle_class -> клас, який ми зробили вище
    server_class -> змінна, яка є класом, вже ГОТОВИМ класом для серверу HTTPServer,
        тобто коли пишемо server_class(), створюється об'єкт сервері в змінну 
    http_server -> змінна сервера. Використовуємо методи:
        .serve_forever() - служити вічно, запускає сервер, буде працювати до зупинки
        .server_close() - зупинка сервера
        
    В коді зупинка серверу буде при KeyboardInterrupt (Ctrl + C в терміналі) або при
    непередбачуваному винятку
    """
    server_address = ("", 1488)
    http_server = server_class(server_address, handler_class)
    try:
        logging.info("Server launching.")
        http_server.serve_forever()
    except KeyboardInterrupt:
        logging.info("Server stopped.")
        http_server.server_close()
    except Exception as e:
        logging.info(f"Error: {e}")
        http_server.server_close()



if __name__ == "__main__":
    run_server()
    
