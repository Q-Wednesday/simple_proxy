import socket
import sys
import _thread
import ssl
from ssl_connect import connectSSL

from Crypto.Cipher import AES

BACKLOG = 50
MAX_DATA_RECV = 999999
DEBUG = True  # set to True to see the debug msgs

users = ["test.user"]
user_password = {
    "test.user": "123456"
}
verified_user = {}


def get_common_name(subject) -> str:
    for field in subject:
        if field[0][0] == 'commonName':
            return str(field[0][1])
    return ''


def control_panel(conn: ssl.SSLSocket):
    conn.send(b"USER NAME:")
    user_name = conn.recv().decode()
    subject = conn.getpeercert()['subject']
    print("subject:", subject)
    if get_common_name(subject) != user_name:
        conn.send(b"USER NAME AND CERTIFICATE NOT MATCH, CLOSE")
        print(user_name, get_common_name(subject))
        conn.close()
        return
    conn.send(b"PASSWORD:")
    pass_word = conn.recv().decode()
    if pass_word != user_password[user_name]:
        conn.send(b"USER NAME AND PASSWORD NOT MATCH, CLOSE")
        conn.close()
        return
    verified_user[user_name] = True
    conn.send(b"VERIFIED")
    while True:
        message = conn.recv()
        if message.decode() == 'CLOSE':
            verified_user.pop(user_name)
            conn.send(b"CLOSE")
            conn.close()
            return
        else:
            conn.send(b"UNKNOWN COMMAND")
            continue


def proxy_handler(conn: ssl.SSLSocket, client_addr):
    # get the request from browser
    request = conn.recv(MAX_DATA_RECV)
    print(str(request))

    # parse the first line
    first_line = request.split(b'\n')[0]

    # get url
    url = first_line.split(b' ')[1]

    print("Request", first_line, client_addr)

    # find the webserver and port
    http_pos = url.find(b'://')  # find pos of ://
    if (http_pos == -1):
        temp = url
    else:
        temp = url[(http_pos + 3):]  # get the rest of url

    port_pos = temp.find(b':')  # find the port pos (if any)

    # find end of web server
    webserver_pos = temp.find(b'/')
    if webserver_pos == -1:
        webserver_pos = len(temp)

    webserver = ""
    port = -1
    if (port_pos == -1 or webserver_pos < port_pos):  # default port
        port = 80
        webserver = temp[:webserver_pos]
    else:  # specific port
        port = int((temp[(port_pos + 1):])[:webserver_pos - port_pos - 1])
        webserver = temp[:port_pos]

    try:
        # create a socket to connect to the web server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((webserver, port))
        s.send(request)  # send request to webserver

        while 1:
            # receive data from web server
            data = s.recv(MAX_DATA_RECV)

            if (len(data) > 0):
                # send to browser
                conn.send(data)
            else:
                break
        s.close()
        conn.close()
    except (socket.error):
        if s:
            s.close()
        if conn:
            conn.close()
        print("Peer Reset", first_line, client_addr)
        sys.exit(1)


def proxy_thread():
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk = ssl.wrap_socket(recv_sock, keyfile="private.key", certfile="cert.crt",
                         cert_reqs=ssl.CERT_REQUIRED, ca_certs="cert.crt")
    sk.bind(('0.0.0.0', 9999))
    sk.listen(BACKLOG)
    while True:
        conn, client_addr = sk.accept()
        subject = conn.getpeercert()['subject']

        if get_common_name(subject) not in verified_user:
            conn.close()
            print("reject connection from {}".format(client_addr))
            continue

        print("accept connection from {}".format(client_addr))
        _thread.start_new_thread(proxy_handler, (conn, client_addr))


def main():
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk = ssl.wrap_socket(recv_sock, keyfile="private.key", certfile="cert.crt",
                         cert_reqs=ssl.CERT_REQUIRED, ca_certs="cert.crt")
    sk.bind(('0.0.0.0', 8080))
    sk.listen(BACKLOG)
    _thread.start_new_thread(proxy_thread, ())
    while True:
        conn, client_addr = sk.accept()
        print("accept connection from {}".format(client_addr))
        _thread.start_new_thread(control_panel, (conn,))


if __name__ == '__main__':
    main()
