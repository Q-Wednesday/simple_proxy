import socket
import ssl
def connectSSL(_tcp_ip='192.168.1.100', _tcp_port=10000, _keyfile='user.key', _certfile='user.pem',
               _ca_certs='ca.crt')->ssl.SSLSocket:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sk = ssl.wrap_socket(s, keyfile=_keyfile, certfile=_certfile, cert_reqs=ssl.CERT_REQUIRED, ca_certs=_ca_certs)

    try:
        sk.connect((_tcp_ip, _tcp_port))
        print("cert type: ", sk.getpeercert())
        return sk
    except Exception as e:
        print(e)
        exit(1)

