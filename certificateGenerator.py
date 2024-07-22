from cryptography.x509 import (
  Name, NameAttribute, CertificateBuilder, random_serial_number
)
from cryptography.hazmat.primitives.serialization import pkcs12, PrivateFormat
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.x509.oid import NameOID
import datetime, random, base64

def generate_certificate(EMAIL_ADDRESS, ORGANIZATION_NAME, COMMON_NAME):
  private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
  )
  public_key = private_key.public_key()

  digit = random.randint(0000, 9999)
  
  subject = Name([
    NameAttribute(NameOID.EMAIL_ADDRESS, EMAIL_ADDRESS),
    NameAttribute(NameOID.COUNTRY_NAME, "SN"),
    NameAttribute(NameOID.ORGANIZATION_NAME, ORGANIZATION_NAME),
    NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Confiance Numérique"),
    NameAttribute(NameOID.COMMON_NAME, COMMON_NAME),
  ])

  issuer = Name([
    NameAttribute(NameOID.COUNTRY_NAME, "SN"),
    NameAttribute(NameOID.ORGANIZATION_NAME, "AmsTech"),
    NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Confiance Numérique"),
    NameAttribute(NameOID.COMMON_NAME, "AmsTech SN"),
  ])

  certificate = (
    CertificateBuilder()
    .subject_name(subject)
    .issuer_name(issuer)
    .public_key(public_key)
    .serial_number(random_serial_number())
    .not_valid_before(datetime.datetime.now(datetime.UTC))
    .not_valid_after(datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=365*3))
    .sign(private_key, hashes.SHA256(), default_backend())
  )

  encryption = (
    PrivateFormat.PKCS12.encryption_builder().
    kdf_rounds(50000).
    key_cert_algorithm(pkcs12.PBES.PBESv1SHA1And3KeyTripleDESCBC).
    hmac_hash(hashes.SHA256()).build(f"{digit}".encode())
  )

  p12 = pkcs12.serialize_key_and_certificates(
    f"{COMMON_NAME}".encode(), private_key, certificate, None, encryption
  )

  return p12, base64.b64encode(
    certificate.public_bytes(
      serialization.Encoding.PEM)
    ).decode('utf-8') , base64.b64encode(
      private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
      )
    ).decode('utf-8'), base64.b64encode(
      public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
      )
    ).decode('utf-8'), digit