import sys

import Utilities
from Client_Side import Client

if __name__ == '__main__':
    args = Utilities.parse_args()
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

            check_file_path = Utilities.validate_file(file_path)
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