import socket
import argparse
import _thread
import time

from ssl_connect import connectSSL

BACKLOG = 50
MAX_DATA_RECV = 999999
DEBUG = True  # set to True to see the debug msgs
BLOCKED = []  # just an example. Remove with [""] for no blocking at all.

server_address = '127.0.0.1'
server_port = 9999
control_port = 8080
verified = False


def control_panel():
    global verified
    print("connect proxy server:", server_address)
    ctl = connectSSL(server_address, control_port, "client_priv.key", "client_cert.crt", "cert.crt")
    while True:
        try:
            message = ctl.recv().decode()
            print(message)
            if message.startswith("VERIFIED"):
                verified = True
            cmd = input(">")
            ctl.send(cmd.encode())
        except Exception:
            verified = False
            print(Exception)
            print("Exit")


def proxy_sender(conn: socket.socket, client_addr):
    # get the request from browser
    request = conn.recv(MAX_DATA_RECV)
    print(str(request))

    # send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    send_sock = connectSSL(server_address, server_port, "client_priv.key", "client_cert.crt", "cert.crt")
    # send_sock.connect((server_address,server_port))
    send_sock.send(request)
    while True:
        data = send_sock.recv(MAX_DATA_RECV)

        if len(data) > 0:
            conn.send(data)
        else:
            break
    send_sock.close()
    conn.close()


def proxy_thread():
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    recv_sock.bind(('127.0.0.1', 8088))
    recv_sock.listen(BACKLOG)
    while not verified:
        time.sleep(0.5)

    print("verified")
    while verified:
        conn, client_addr = recv_sock.accept()
        print("accept connection from {}".format(client_addr))
        _thread.start_new_thread(proxy_sender, (conn, client_addr))


def main():
    _thread.start_new_thread(proxy_thread, ())
    control_panel()


parser = argparse.ArgumentParser(description='proxy server')

parser.add_argument('-a', dest='address', action='store',
                    help='proxy server address', default='127.0.0.1')

if __name__ == '__main__':
    args = parser.parse_args()
    server_address = args.address
    main()
