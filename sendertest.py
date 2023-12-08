import socket


def send_socket_command(command):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect(('localhost', 8089))
    clientsocket.send(command.encode())


if __name__ == "__main__":
    send_socket_command("Go!")
