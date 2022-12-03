import socket
import sys

from Crypto import Random
from Crypto.Cipher import AES
import _thread

BACKLOG = 50
MAX_DATA_RECV = 999999
DEBUG = True  # set to True to see the debug msgs
BLOCKED = []  # just an example. Remove with [""] for no blocking at all.

server_address='127.0.0.1'
server_port=9999
key = b'this is a 16 key'
def encrypt(req:bytes)->bytes:
    # 密钥key必须为 16（AES-128）， 24（AES-192）， 32（AES-256）

    # 生成长度等于AES 块大小的不可重复的密钥向量
    iv = Random.new().read(AES.block_size)
    print(iv)
    # 使用 key 和iv 初始化AES 对象， 使用MODE_CFB模式
    mycipher = AES.new(key, AES.MODE_CFB, iv)
    print(mycipher)
    # 加密的明文长度必须为16的倍数， 如果长度不为16的倍数， 则需要补足为16的倍数
    # 将iv(密钥向量)加到加密的密钥开头， 一起传输
    ciptext = iv + mycipher.encrypt(req)
    # 解密的话需要用key 和iv 生成的AES对象
    print(ciptext)
    # 使用新生成的AES 对象， 将加密的密钥解密
    return ciptext
def proxy_thread(conn:socket.socket, client_addr):
    # get the request from browser
    request = conn.recv(MAX_DATA_RECV)
    print(str(request))

    send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    send_sock.connect((server_address,server_port))
    send_sock.send(encrypt(request))
    while True:
        data = send_sock.recv(MAX_DATA_RECV)

        if len(data) > 0:
            conn.send(data)
        else:
            break
    send_sock.close()
    conn.close()

def main():
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    recv_sock.bind(('127.0.0.1', 8088))
    recv_sock.listen(BACKLOG)
    while True:
        conn, client_addr = recv_sock.accept()
        print("accept connection from {}".format(client_addr))
        _thread.start_new_thread(proxy_thread, (conn, client_addr))

if __name__ == '__main__':
    main()