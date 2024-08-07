from signServer import *

def extractCert(pdf_file):
  with open(pdf_file, 'rb') as doc:
    r = PdfFileReader(doc)
    sig = r.embedded_regular_signatures
  cert_data = {}
  for s in sig:
    cert_der = s.signer_cert.dump()
    cert_cryptography = x509.load_der_x509_certificate(cert_der, default_backend())
    res = listCertAttribut(cert_cryptography)
    cert_data[f"Signature of {res['commonNameSubject']} [{res['emailAddressSubject']}] "] = reformat(res)
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

def test(string, data, result):
  if string in data:
    result.update({string: data[string]})

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
