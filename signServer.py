import chilkat2

def signPdf(pdf_path, p12, digit):
  pkcs_path = "pkcs.p12"
  with open (pkcs_path, "wb") as file:
    file.write(p12)
  pdf = chilkat2.Pdf()

  success = pdf.LoadFile(pdf_path)
  if (success == False):
    print(pdf.LastErrorText)
    return False

  json = chilkat2.JsonObject()
  json.UpdateInt("signingCertificateV2",1)
  json.UpdateInt("signingTime",1)
  json.UpdateInt("page",1)
  json.UpdateString("appearance.y","bottom")
  json.UpdateString("appearance.x","left")
  json.UpdateString("appearance.fontScale","10.0")
  json.UpdateString("appearance.text[0]","Signé par: cert_cn")
  json.UpdateString("appearance.text[1]","Le  current_dt")

  cert = chilkat2.Cert()
  success = cert.LoadPfxFile(pkcs_path, digit)

  if (success == False):
    return False

  success = pdf.SetSigningCert(cert)
  if (success == False):
    return False

  success = pdf.SignPdf(json, "res.pdf")
  if (success == False):
    return False

  success = pdf.SignPdf(json, "res.pdf")
  if (success == False):
    print(pdf.LastErrorText)
    return False
  
  return True