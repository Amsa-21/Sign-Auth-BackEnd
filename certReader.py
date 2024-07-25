from signServer import *

def extractCert(pdf_file):
  if pdf_file.endswith(".pdf")==False:
    return None
  pdf = chilkat2.Pdf()
  success = pdf.LoadFile(pdf_file)
  if success == False:
    return None
  sigInfo = chilkat2.JsonObject()
  numSignatures = pdf.NumSignatures
  cert = chilkat2.Cert()
  i = 0
  cert_data = {}
  while i < numSignatures :
    pdf.VerifySignature(i,sigInfo)
    success = pdf.GetSignerCert(i,cert)
    if (success != False):
      cert_data["Signature of " + cert.SubjectCN] = reformat(listCertAttribut(cert))
    i = i + 1
  return cert_data

def listCertAttribut(certif):
  result = {}
  for attr_name in dir(certif):
    if not attr_name.startswith('_') and not callable(getattr(certif, attr_name)) and not attr_name.startswith('LastError') and not attr_name == 'Version':
      attr_value = getattr(certif, attr_name)
      if attr_value is not None and not attr_value == "" and not isinstance(attr_value, bool):
        c = {attr_name: attr_value}
        result.update(c)
  return result   

def reformat(data):
  result = {}
  test("SubjectCN", data, result)
  test("SubjectE", data, result)
  test("SubjectO", data, result)
  test("SubjectC", data, result)
  test("SubjectOU", data, result)
  test("Rfc822Name", data, result)
  test("IssuerCN", data, result)
  test("IssuerO", data, result)
  test("IssuerC", data, result)
  test("IssuerOU", data, result)
  test("CertVersion", data, result)
  test("ValidFromStr", data, result)
  test("ValidToStr", data, result)
  test("SubjectKeyId", data, result)
  test("SubjectDN", data, result)
  test("AuthorityKeyId", data, result)
  test("IssuerDN", data, result)
  test("SerialNumber", data, result)
  test("SerialDecimal", data, result)
  test("Sha1Thumbprint", data, result)
  return result

def test(string, data, result):
  if string in data:
    result.update({string: data[string]})

def reformatIssuer(data):
  result = {}
  test("IssuerCN", data, result)
  test("IssuerO", data, result)
  test("IssuerC", data, result)
  test("IssuerOU", data, result)
  return result

def autorityFinder(pdf_file):
  pdf = chilkat2.Pdf()
  success = pdf.LoadFile(pdf_file)
  if success == False:
    return None
  sigInfo = chilkat2.JsonObject()
  cert = chilkat2.Cert()
  pdf.VerifySignature(0, sigInfo)
  success = pdf.GetSignerCert(0, cert)
  if success:
    result = reformatIssuer(listCertAttribut(cert))
    return result
  return None
