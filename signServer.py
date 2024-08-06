from pyhanko import stamp
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import fields, signers, timestamps
import secrets, base64
from pyhanko.pdf_utils.reader import PdfFileReader
from cryptography.hazmat.backends import default_backend
from cryptography import x509

async def sign(signer, fname, num, i):
  ident = secrets.token_hex(16)
  padding = 5+(i-1)*5
  with open(fname, 'rb') as inf:
    w = IncrementalPdfFileWriter(inf)
    fields.append_signature_field(
      w, sig_field_spec=fields.SigFieldSpec(
        f'Signature{num}', box=(padding+150*(i-1), 5, padding+150*i, 35)
      )
    )
    tt_client = timestamps.HTTPTimeStamper('http://timestamp.sectigo.com')
    meta = signers.PdfSignatureMetadata(field_name=f'Signature{num}')
    pdf_signer = signers.PdfSigner(
      meta, signer=signer, stamp_style=stamp.QRStampStyle(
        border_width=1,
        timestamp_format='%d-%m-%Y %H:%M:%S %Z',
        stamp_text='%(signer)s\n%(ts)s',
      ),
      timestamper=tt_client
    )
    out = await pdf_signer.async_sign_pdf(
      w,
      appearance_text_params={'url': ident}
    )
  return out, ident

async def signPdf(pdf_path, certificate, private_key):
  key_path = "key.pem"
  cert_path = "cert.pem"
  with open (cert_path, "wb") as file:
    file.write(base64.b64decode(certificate))
  with open (key_path, "wb") as file:
    file.write(base64.b64decode(private_key))
  test = test_if_present(pdf_path)
  if test:
    return None, False
  cms_signer = signers.SimpleSigner.load(key_file=key_path, cert_file=cert_path) 
  with open(pdf_path, "rb") as doc:
    r = PdfFileReader(doc)
    num = len(r.embedded_signatures)
    i = len(r.embedded_regular_signatures)
  out, ident = await sign(cms_signer, pdf_path, num+1, i+1)
  with open(pdf_path, "wb") as file:
    file.write(out.getvalue())
  return ident, True

def test_if_present(pdf_path):
  with open('cert.pem', "rb") as file:  
    cert_der = file.read()
    cert_cryptography_test = x509.load_pem_x509_certificate(cert_der, default_backend())
  with open(pdf_path, 'rb') as doc:
    r = PdfFileReader(doc)
    sig = r.embedded_regular_signatures
  for s in sig:
    cert_der = s.signer_cert.dump()
    cert_cryptography = x509.load_der_x509_certificate(cert_der, default_backend())
    if cert_cryptography.subject == cert_cryptography_test.subject:
      return True
  return False