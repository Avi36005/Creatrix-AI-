import os
import re
import sys
import http.server

class RangeRequestHandler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            return super().send_head()
        
        ctype = self.guess_type(path)
        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(404, "File not found")
            return None
        
        range_header = self.headers.get('Range')
        if not range_header:
            return super().send_head()
            
        match = re.match(r'bytes=(\d+)-(\d*)', range_header)
        if not match:
            return super().send_head()
            
        start, end = match.groups()
        try:
            size = os.path.getsize(path)
            start = int(start)
            end = int(end) if end else size - 1
        except ValueError:
            return super().send_head()
            
        if start >= size:
            self.send_error(416, "Requested range not satisfiable")
            f.close()
            return None
            
        self.send_response(206)
        self.send_header('Content-Type', ctype)
        self.send_header('Accept-Ranges', 'bytes')
        self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.send_header('Content-Length', str(end - start + 1))
        self.send_header('Last-Modified', self.date_time_string(os.path.getmtime(path)))
        self.end_headers()
        return f

    def copyfile(self, source, outputfile):
        range_header = self.headers.get('Range')
        if not range_header or self.wfile.closed:
            super().copyfile(source, outputfile)
            return

        match = re.match(r'bytes=(\d+)-(\d*)', range_header)
        if not match:
            super().copyfile(source, outputfile)
            return

        start, end = match.groups()
        try:
            size = os.fstat(source.fileno()).st_size
            start = int(start)
            end = int(end) if end else size - 1
        except Exception:
            super().copyfile(source, outputfile)
            return

        source.seek(start)
        to_read = end - start + 1
        BUFSIZE = 64 * 1024
        while to_read > 0:
            buf = source.read(min(to_read, BUFSIZE))
            if not buf:
                break
            outputfile.write(buf)
            to_read -= len(buf)

if __name__ == '__main__':
    port = 8000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    server_address = ('', port)
    httpd = http.server.ThreadingHTTPServer(server_address, RangeRequestHandler)
    print(f"Serving on port {port}...")
    httpd.serve_forever()
