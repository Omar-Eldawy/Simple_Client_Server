import argparse
import os


def read_file(file_name: str) -> list[str]:
    with open(file_name, 'r') as file:
        lines = [line.strip() for line in file]
    return lines


def validate_file(file_name: str) -> str:
    if not os.path.isfile(file_name):
        return "File does not exist"
    if os.path.splitext(file_name)[1] != ".txt":
        return "File is not a text file"
    if os.stat(file_name).st_size == 0:
        return "File is empty"
    return "File is valid"


def handle_command_parsing(command: str) -> list[str]:
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
