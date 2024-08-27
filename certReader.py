from cryptography.hazmat.primitives import hashes
from signServer import *


def compare_certificates(cert1, cert2):
  fingerprint1 = cert1.fingerprint(hashes.SHA256())
  fingerprint2 = cert2.fingerprint(hashes.SHA256())
  return fingerprint1 == fingerprint2

def extractCert(pdf_file, certs):
  with open(pdf_file, 'rb') as doc:
    r = PdfFileReader(doc)
    sig = r.embedded_regular_signatures
  cert_data = {}
  for s in sig:
    cert_der = s.signer_cert.dump()
    cert_cryptography = x509.load_der_x509_certificate(cert_der, default_backend())
    c = False
    for cert in certs:
      cert2 = x509.load_pem_x509_certificate(open(cert, 'rb').read(), default_backend())
      if compare_certificates(cert_cryptography, cert2):
        c = True
        break
    res = listCertAttribut(cert_cryptography)
    res = reformat(res)
    res.update({"confiance": c})
    cert_data[f"{res['commonNameSubject']} [{res['emailAddressSubject']}]"] = res
  return cert_data

def listCertAttribut(cert):
  result = {}
  for att in dir(cert):
    if att=="version" or att=="not_valid_before_utc" or att=="not_valid_after_utc":
      c = {att: getattr(cert, att)}
      result.update(c)
    if att=="issuer" or att=="subject":
      value = getattr(cert, att)
      for i in value:
        c = {f"{i.oid._name}{att.capitalize()}": i.value}
        result.update(c)
  return result

def reformat(data):
  result = {}
  test("commonNameSubject", data, result)
  test("emailAddressSubject", data, result)
  test("organizationNameSubject", data, result)
  test("countryNameSubject", data, result)
  test("organizationalUnitNameSubject", data, result)
  test("commonNameIssuer", data, result)
  test("countryNameIssuer", data, result)
  test("organizationalUnitNameIssuer", data, result)
  test("not_valid_before_utc", data, result)
  test("not_valid_after_utc", data, result)
  return result

def test(key, data, result):
  if key in data:
    result.update({key: data[key]})

def reformatIssuer(data):
  result = {}
  test("commonNameIssuer", data, result)
  test("organizationNameIssuer", data, result)
  test("countryNameIssuer", data, result)
  test("organizationalUnitNameIssuer", data, result)
  return result

def autorityFinder(pdf_file):
  with open(pdf_file, 'rb') as doc:
    r = PdfFileReader(doc)
    sig = r.embedded_regular_signatures
  if sig:
    cert_der = sig[0].signer_cert.dump()
    cert_cryptography = x509.load_der_x509_certificate(cert_der, default_backend())
    res = listCertAttribut(cert_cryptography)
    result = reformatIssuer(res)
    return result
  return None
