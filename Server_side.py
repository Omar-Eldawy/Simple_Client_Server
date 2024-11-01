import socket
import threading
import mimetypes
import os


def handle_post_request(headers, client_socket):
    content_length = 0
    content_type = ""
    
    for header in headers:
        if "Content-Length" in header:
            content_length = int(header.split(":")[1].strip())
        elif "Content-Type" in header:
            content_type = header.split(":")[1].strip()
            
    if content_length == 0:
        response = "HTTP/1.1 411 Length Required\r\n\r\nContent-Length Required"
        client_socket.send(response.encode("utf-8"))
        return
    
    request_body = client_socket.recv(content_length)
    print(f"Received POST request: {request_body}")
    
    if content_type == "image/png":
        uploaded_file_name = "uploaded_image.png"
        with open(os.path.join('Server_Directory', uploaded_file_name), "wb") as write_file:
            write_file.write(request_body)
    else:
        uploaded_file_name = headers[0].split(" ")[1].lstrip("/")
        lines = request_body.decode("utf-8").splitlines()
        uploaded_file_content = "\n".join(lines[1:])
        
        with open(os.path.join('Server_Directory', uploaded_file_name), "wb") as write_file:
            write_file.write(uploaded_file_content)
    
    response = "HTTP/1.1 200 OK\r\n\r\nRequest handled successfully"
    client_socket.send(response.encode("utf-8"))


def handle_get_request(headers, client_socket):
    requested_file = headers[0].split(" ")[1]
    print(f"Requested file: {requested_file}")
    if requested_file == '/':
        requested_file = '/index.html'
    
    file_path = requested_file.lstrip('/') # remove the leading forward slash to get the current directory
    
    try:
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'application/octet-stream'  # raw data(binary data)
        with open(os.path.join('Server_Directory', file_path), 'rb') as read_file:
            file_content = read_file.read()
        response = f'HTTP/1.1 200 OK\r\nContent-Type: {content_type}\r\n\r\n'.encode("utf-8") + file_content
        
    except FileNotFoundError:
        print(f"File not found: {requested_file}")
        response = "HTTP/1.1 404 Not Found\r\n\r\nFile Not Found"
    
    client_socket.send(response if isinstance(response, bytes) else response.encode("utf-8"))
    

def handle_client(client_socket, client_address):
    try:
        while True:
            request = client_socket.recv(1024).decode("utf-8") # decode the bytes to string
            if request.lower().strip() == "close":
                client_socket.send("closed".encode("utf-8"))  # encode the string to bytes before sending
                break
            
            print(f"Received from {client_address[0]}:{client_address[1]}: {request}")
            headers = request.splitlines()
            command = headers[0].split(" ")[0]
            if command == "GET":
                handle_get_request(headers, client_socket)
            elif command == "POST":
                handle_post_request(headers, client_socket)
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