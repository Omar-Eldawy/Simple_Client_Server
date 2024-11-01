import socket
import threading
import mimetypes
import os

file_size = 20_971_520  # 20MB

def parse_http_request(request):
    headers = {}
    header_lines = request.split("\r\n")
    # Get the file name from the first line of the request
    file_name = header_lines[0].split(" ")[1].lstrip("/")
    # Get the headers from the request and store them in a dictionary
    for line in header_lines[1:]:
        if line == "":
            break
        key, value = line.split(":", 1)
        headers[key.strip()] = value.strip()
    return headers, file_name


def handle_post_request(header, req_body, client_socket):
    headers, uploaded_file_name = parse_http_request(header)
    content_length = int(headers.get("Content-Length", 0))
    content_type = headers.get("Content-Type", "")

    if content_length == 0:
        response = "HTTP/1.1 411 Length Required\r\n\r\nContent-Length Required"
        client_socket.send(response.encode("utf-8"))
        return
    
    file_content = req_body
    
    # Receive the file content from the client in chunks of 4096 bytes
    while len(file_content) < content_length:
        data = client_socket.recv(4096)
        if not data:
            break
        file_content += data
    # Check if the file is an image or text file and write it to the server directory
    if content_type.startswith("image/"):
        # Write the file content as binary data
        with open(os.path.join('Server_Directory', uploaded_file_name), "wb") as write_file:
            write_file.write(file_content)
    else:
        # Write the file content as text data
        with open(os.path.join('Server_Directory', uploaded_file_name), "w") as write_file:
            write_file.write(file_content.decode("utf-8"))

    print("File uploaded successfully")
    response = "HTTP/1.1 200 OK\r\n\r\nRequest handled successfully"
    client_socket.send(response.encode("utf-8"))


def handle_get_request(header, client_socket):
    requested_file = header.split(" ")[1]
    print(f"Requested file: {requested_file}")
    if requested_file == '/':
        requested_file = '/index.html'

    file_path = requested_file.lstrip('/') # remove the leading forward slash to get the current directory

    try:
        # Determine the content type of the file
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'application/octet-stream'  # raw data(binary data)
        # Read the file content from the server directory and send it to the client
        with open(os.path.join('Server_Directory', file_path), 'rb') as read_file:
            file_content = read_file.read()
        response = f'HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\n\r\n'.encode("utf-8") + file_content

    except FileNotFoundError:
        print(f"File not found: {requested_file}")
        response = "HTTP/1.1 404 Not Found\r\n\r\nFile Not Found"
    print("File sent successfully")
    client_socket.send(response if isinstance(response, bytes) else response.encode("utf-8"))


def handle_client(client_socket, client_address):
    try:
        while True:
            request = client_socket.recv(file_size)
            if not request:  # Check for an empty request
                continue
            
            body_start_index = request.find(b"\r\n\r\n") + 4    # find the end of the header
            header = request[:body_start_index].decode("utf-8") # decode the bytes to string
            req_body = request[body_start_index:]               # get the request body (bytes)
            
            # Check if the client wants to close the connection
            if request.upper().strip() == "close":
                client_socket.send("closed".encode("utf-8"))  # encode the string to bytes before sending
                break

            print(f"Received from {client_address[0]}:{client_address[1]}: {request}")
            command = header.split(" ")[0]
            # Direct the request to the appropriate handler
            if command == "GET":
                handle_get_request(header, client_socket)
            elif command == "POST":
                pass
                handle_post_request(header, req_body, client_socket)
            else:
                response = "HTTP/1.1 400 Bad Request\r\n"
                client_socket.send(response.encode("utf-8"))
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client_socket.close()
        print(f"Connection to client {client_address[0]}:{client_address[1]} closed")



def run_server():
    server_ip = "127.0.0.1"
    port = 8080
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a TCP socket
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # allow the server to reuse the same address
        server.bind((server_ip, port))
        server.listen()
        print(f"Listening on {server_ip}:{port}")

        while True:
            client_socket, client_address = server.accept()
            print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
            thread = threading.Thread(target=handle_client, args=(client_socket, client_address)) # create a new thread to handle the client
            thread.start()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        server.close()

run_server()