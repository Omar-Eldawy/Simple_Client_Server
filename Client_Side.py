import socket
import mimetypes
import os

# close isn't working

class Client:
    def __init__(self, host: str, port: int):
        self.__host = host
        self.__port = port
        self.__client = None
        self.__file_size = 20_971_520  # 20MB

    # directing the command to the appropriate function
    def action(self, command: str, path: str) -> None:
        if command == 'POST':
            self.__post_file(path)
        elif command == 'GET':
            self.__get_file(path)
        else:
            print('Invalid Command')

    def __post_file(self, path: str) -> None:
        # Check if the client directory exists, if not create it
        if not os.path.exists('Client_Directory'):
            os.makedirs('Client_Directory')

        file_name = os.path.basename(path)
        # Guess the content type of the file
        content_type, _ = mimetypes.guess_type(file_name)
        with open(os.path.join('Client_Directory', file_name), 'rb') as file:
            file_data = file.read()
        # Create the request header to send to the server
        request_header = f"POST /{file_name} HTTP/1.1\r\nContent-Length: {len(file_data)}\r\nContent-Type: {content_type}\r\n\r\n"

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.__client:
            self.__client.connect((self.__host, self.__port))
            # Send the request header and the file data to the server
            self.__client.sendall(request_header.encode('utf-8') + file_data)
            response = self.__client.recv(self.__file_size)
            print(response.decode('utf-8'))

    def __get_file(self, file_name: str) -> None:
        # Check if the client directory exists, if not create it
        if not os.path.exists('Client_Directory'):
            os.makedirs('Client_Directory')

        # Create the request header to send to the server
        request_header = f"GET /{file_name} HTTP/1.1\r\n\r\n"
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.__client:
            self.__client.connect((self.__host, self.__port))
            # Send the request header to the server to get the file/img
            self.__client.sendall(request_header.encode('utf-8'))
            response = self.__client.recv(self.__file_size)

            header_end = response.find(b'\r\n\r\n')
            if header_end == -1:
                print('Error in response format')
                return

            # Get the header and the body of the response separately
            header = response[:header_end].decode('utf-8')
            body = response[header_end + 4:]

            if '404 Not Found' in header:
                print('File not found on server')
                return
            else:
                with open(os.path.join('Client_Directory', file_name), 'wb') as file:
                    file.write(body)
                    print('File downloaded successfully')

    def close(self) -> None:
        self.__client.close()


if __name__ == '__main__':
    server_ip = "127.0.0.1"
    server_port = 8080
    client = Client(server_ip, server_port)
    while True:
        client_command = input('Enter Command: ').upper()
        if client_command == 'CLOSE':
            client.close()
            break
        if client_command not in ['POST', 'GET']:
            print('Invalid Command')
            continue
        file_path = input('Enter File Path: ')
        client.action(client_command, file_path)
    client.close()