import socket
import mimetypes
import os
import sys

import Utilities
from Utilities import parse_args, validate_file


class Client:
    def __init__(self, host: str, port: int):
        self.__host = host
        self.__port = port
        self.__client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__client.connect((self.__host, self.__port))
        self.__file_size = 20_971_520  # 20MB

    # directing the command to the appropriate function
    def action(self, user_command: str, path: str) -> bool:
        try:
            if user_command == 'POST':
                self.__post_file(path)
            elif user_command == 'GET':
                self.__get_file(path)
            else:
                print('Invalid Command', end='\n\n')
            return True

        except ConnectionRefusedError:
            print("Connection refused: The server is not listening on the specified IP and port.", end='\n\n')
            return False

        except socket.gaierror:
            print("Address-related error: The hostname or IP address could not be resolved.", end='\n\n')
            return False

        except BrokenPipeError:
            print("Broken pipe: The connection was closed by the server unexpectedly.", end='\n\n')
            return False

        except TimeoutError:
            print("Timeout: The connection attempt or send operation timed out.", end='\n\n')
            return False

        except OSError as e:
            print(f"OS error: {e}", end='\n\n')
            return False

    def __post_file(self, path: str) -> None:
        # Check if the client directory exists, if not create it
        if not os.path.exists('Client_Directory'):
            os.makedirs('Client_Directory')

        file_name = os.path.basename(path)
        if not os.path.exists(os.path.join('Client_Directory', file_name)):
            print(f"Error: File '{file_name}' does not exist.", end='\n\n')
            return

        # Guess the content type of the file
        content_type, _ = mimetypes.guess_type(file_name)
        with open(os.path.join('Client_Directory', file_name), 'rb') as file:
            file_data = file.read()
        # Create the request header to send to the server
        request_header = f"POST /{file_name} HTTP/1.1\r\nContent-Length: {len(file_data)}\r\nContent-Type: {content_type}\r\n\r\n"

        # Send the request header and the file data to the server
        self.__client.sendall(request_header.encode('utf-8') + file_data)
        response = self.__client.recv(self.__file_size)
        print(response.decode('utf-8'), end='\n\n')

    def __get_file(self, file_name: str) -> None:
        # Check if the client directory exists, if not create it
        if not os.path.exists('Client_Directory'):
            os.makedirs('Client_Directory')

        # Create the request header to send to the server
        request_header = f"GET /{file_name} HTTP/1.1\r\n\r\n"

        # Send the request header to the server to get the file
        self.__client.sendall(request_header.encode('utf-8'))
        response = self.__client.recv(self.__file_size)
        header_end = response.find(b'\r\n\r\n')
        if header_end == -1:
            print('Error in response format', end='\n\n')
            return

        # Get the header and the body of the response separately
        header = response[:header_end].decode('utf-8')
        body = response[header_end + 4:]

        if '404 Not Found' in header:
            print(header)
            print('File not found on server', end='\n\n')
            return
        elif '200 OK' in header:
            print(header)
            with open(os.path.join('Client_Directory', file_name), 'wb') as file:
                file.write(body)
                print('File downloaded successfully', end='\n\n')
        else:
            print(header, end='\n\n')

    def close(self) -> None:
        self.__client.close()

    def send_close_message(self):
        self.__client.send("CLOSE".encode('utf-8'))


if __name__ == '__main__':
    args = parse_args()
    client = Client(args.server_ip, args.port_number)
    reconnecting_flag = False
    commands = None
    while True:
        if not reconnecting_flag:
            file_path = input('Enter commands file path or Close to terminate:')

            if file_path.upper() == 'CLOSE':
                client.send_close_message()
                client.close()
                print('Connection closed')
                sys.exit(0)

            check_file_path = validate_file(file_path)
            if check_file_path != 'File is valid':
                print(check_file_path)
                continue

            commands = Utilities.read_file(file_path)

        reconnecting_flag = False
        for command in commands:
            client_command = Utilities.handle_command_parsing(command)
            if client_command[0].upper() == 'CLOSE':
                client.send_close_message()
                client.close()
                print('Connection closed')
                sys.exit(0)
            if client_command[0].upper() not in ['POST', 'GET']:
                print('Invalid Command')
                continue
            if not client.action(client_command[0].upper(), client_command[1]):
                client = Client(args.server_ip, args.port_number)
                reconnecting_flag = True
                print('Reconnecting...', end='\n\n')
                break

