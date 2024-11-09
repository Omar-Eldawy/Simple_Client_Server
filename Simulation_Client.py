import Utilities
from Client_Side import Client

if __name__ == "__main__":
    client = Client('127.0.0.1', 8080)
    commands = Utilities.read_file('Simulation\\Simulation_Commands.txt')
    for command in commands:
        client_command = Utilities.handle_command_parsing(command)
        client.action(client_command[0].upper(), client_command[1])
    client.send_close_message()
    client.close()