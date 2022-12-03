import random

from OpenSSL import crypto, SSL


def generate_root_cert(
        email_address="somebody@mails.tsinghua.edu.cn",
        common_name="simple.proxy.root.com",
        country_name="CN",
        locality_name="localityName",
        province_name="Beijing",
        organization_name="Tsinghua",
        organization_unit_name="Software",
        serial_number=0,
        validity_end_in_seconds=10 * 365 * 24 * 60 * 60,
        key_file="private.key",
        cert_file="cert.crt"):
    # create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 4096)
    # create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().C = country_name
    cert.get_subject().ST = province_name
    cert.get_subject().L = locality_name
    cert.get_subject().O = organization_name
    cert.get_subject().OU = organization_unit_name
    cert.get_subject().CN = common_name
    cert.get_subject().emailAddress = email_address
    cert.set_serial_number(serial_number)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(validity_end_in_seconds)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha512')
    with open(cert_file, "wt") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8"))
    with open(key_file, "wt") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode("utf-8"))
    return cert, k


def generate_client_cert(parent_cert: crypto.X509, parent_key: crypto.PKey,
                         emailAddress="somebody@mails.tsinghua.edu.cn",
                         commonName="simple.proxy.root.com",
                         countryName="CN",
                         localityName="localityName",
                         stateOrProvinceName="Beijing",
                         organizationName="Tsinghua",
                         organizationUnitName="Software",
                         validityEndInSeconds=10 * 365 * 24 * 60 * 60,
                         KEY_FILE="private.key",
                         CERT_FILE="cert.crt"):
    # create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 4096)
    # create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().C = countryName
    cert.get_subject().ST = stateOrProvinceName
    cert.get_subject().L = localityName
    cert.get_subject().O = organizationName
    cert.get_subject().OU = organizationUnitName
    cert.get_subject().CN = commonName
    cert.get_subject().emailAddress = emailAddress
    serial_number = random.getrandbits(32)
    cert.set_serial_number(serial_number)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(validityEndInSeconds)
    cert.set_issuer(parent_cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(parent_key, 'sha512')
    with open(CERT_FILE, "wt") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8"))
    with open(KEY_FILE, "wt") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k).decode("utf-8"))


if __name__ == '__main__':
    parent_cert, parent_key = generate_root_cert()
    generate_client_cert(parent_cert, parent_key, commonName="test.user", KEY_FILE="client_priv.key",
                         CERT_FILE="client_cert.crt")
