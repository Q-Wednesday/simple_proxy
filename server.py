import socket
import sys
import _thread

from Crypto.Cipher import AES

BACKLOG = 50
MAX_DATA_RECV = 999999
DEBUG = True  # set to True to see the debug msgs
BLOCKED = []  # just an example. Remove with [""] for no blocking at all.

key = b'this is a 16 key'
def decrypt(ciptext:bytes)->bytes:
    mydecrypt = AES.new(key, AES.MODE_CFB, ciptext[:16])
    return mydecrypt.decrypt(ciptext)
def proxy_thread(conn, client_addr):
    # get the request from browser
    request = conn.recv(MAX_DATA_RECV)
    request = decrypt(request)
    print(str(request))

    # parse the first line
    first_line = request.split(b'\n')[0]

    # get url
    url = first_line.split(b' ')[1]

    for i in range(0, len(BLOCKED)):
        if BLOCKED[i] in url:
            print("Blacklisted", first_line, client_addr)
            conn.close()
            sys.exit(1)

    print("Request", first_line, client_addr)
    # print "URL:",url
    # print

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


def main():
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    recv_sock.bind(('127.0.0.1', 9999))
    recv_sock.listen(BACKLOG)
    while True:
        conn, client_addr = recv_sock.accept()
        print("accept connection from {}".format(client_addr))
        _thread.start_new_thread(proxy_thread, (conn, client_addr))

if __name__ == '__main__':
    main()