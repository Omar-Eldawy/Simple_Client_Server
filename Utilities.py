import argparse


def read_file(file_name: str) -> list[str]:
    lines = []
    with open(file_name, 'r') as file:
        lines = [line.strip() for line in file]
    return lines


def handle_command_parsing(command: str)-> list[str]:
    parsing = command.split(' ')
    if len(parsing) == 4:
        return parsing
    else:
        parsing.append('80')
        return parsing


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('server_ip', type=str, default='127.0.0.1')
    parser.add_argument('port_number', type=int, default=80)
    return parser.parse_args()


def parse_args_port():
    parser = argparse.ArgumentParser()
    parser.add_argument('port_number', type=int, default=80)
    return parser.parse_args()