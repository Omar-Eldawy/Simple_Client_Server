import socket
import os

class Client:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.client = None

    def action(self, command: str, path: str) -> None:
        if command == 'POST':
            self.post_file(path)
        elif command == 'GET':
            self.get_file(path)
        else:
            print('Invalid Command')

        self.client.close()

    def post_file(self, path: str) -> None:
        file_name = os.path.basename(path)
        with open(path, 'rb') as file:
            file_data = file.read()
        request_header = f"POST /{file_name} HTTP/1.1\r\nContent-Length: {len(file_data)}\r\n\r\n"

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.client:
            self.client.connect((self.host, self.port))
            self.client.sendall(request_header.encode('utf-8') + file_data)
            response = self.client.recv(1024)
            print(response.decode())

    def get_file(self, file_name: str) -> None:
        if not os.path.exists('Client_Directory'):
            os.makedirs('Client_Directory')

        request_header = f"GET /{file_name} HTTP/1.1\r\n\r\n"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.client:
            self.client.connect((self.host, self.port))
            self.client.sendall(request_header.encode('utf-8'))
            response = self.client.recv(1024)
            print(response.decode())

            header, body = response.decode().split('\r\n\r\n', 1)
            if '404 Not Found' in header:
                print('File not found on server')
                return
            else:
                with open(os.path.join('Client_Directory', file_name), 'wb') as file:
                    file.write(body.encode())
                    print('File downloaded successfully')

if __name__ == '__main__':
    server_port = 8080
    client = Client(socket.gethostbyname(socket.gethostname()), server_port)
    client.action('GET', 'index.html')
    client.action('GET', 'Adel.jpg')
    client.action('POST', 'Emam.jpeg')