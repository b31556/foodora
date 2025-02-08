def start():
    import http.server
    import socketserver

    PORT = 8080
    DIRECTORY = "setup_helper/web_files"

    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/":
                self.path = "/index.html"
            return super().do_GET()

    Handler = CustomHandler
    Handler.directory = DIRECTORY

    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        httpd.serve_forever()
