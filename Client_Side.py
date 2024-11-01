import socket
import os

class Client:
    def __init__(self, host: str, port: int):
        self.__host = host
        self.__port = port
        self.__client = None

    def action(self, command: str, path: str) -> None:
        if command == 'POST':
            self.__post_file(path)
        elif command == 'GET':
            self.__get_file(path)
        else:
            print('Invalid Command')

    def __post_file(self, path: str) -> None:
        file_name = os.path.basename(path)
        with open(path, 'rb') as file:
            file_data = file.read()
        request_header = f"POST /{file_name} HTTP/1.1\r\nContent-Length: {len(file_data)}\r\n\r\n"

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.__client:
            self.__client.connect((self.__host, self.__port))
            self.__client.sendall(request_header.encode('utf-8') + file_data)
            response = self.__client.recv(1024)
            print(response.decode())

    def __get_file(self, file_name: str) -> None:
        if not os.path.exists('Client_Directory'):
            os.makedirs('Client_Directory')

        request_header = f"GET /{file_name} HTTP/1.1\r\n\r\n"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.__client:
            self.__client.connect((self.__host, self.__port))
            self.__client.sendall(request_header.encode('utf-8'))
            response = self.__client.recv(1024)
            print(response.decode())

            header, body = response.decode().split('\r\n\r\n', 1)
            if '404 Not Found' in header:
                print('File not found on server')
                return
            else:
                with open(os.path.join('Client_Directory', file_name), 'wb') as file:
                    file.write(body.encode())
                    print('File downloaded successfully')

    def close(self) -> None:
        self.__client.close()

if __name__ == '__main__':
    server_ip = "127.0.0.1"
    server_port = 8080
    client = Client(server_ip, server_port)
    while True:
        client_command = input('Enter Command: ')
        if client_command == 'close':
            break
        file_path = input('Enter File Path: ')
        client.action(client_command, file_path)
    client.close()    