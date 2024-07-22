from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

# B4guf8SaDE8v72B4guf8SaDE8v72

def sendEmail(to_address, digit):
  smtp_server = 'smtp.gmail.com'
  smtp_port = 587
  smtp_user = 'amstech.senegal@gmail.com'
  smtp_password = 'fhcw nipa qqsg lmwk'
  from_address = 'amstech.senegal@gmail.com'

  subject = 'SignAuth - Code secret'
  body = f"""
    <html>
      <body>
        <p>Ceci est votre code secret de signature: <b>{digit}</b>.</p>
      </body>
    </html>
  """

  msg = MIMEMultipart()
  msg['From'] = from_address
  msg['To'] = to_address
  msg['Subject'] = subject

  msg.attach(MIMEText(body, "html"))

  try:
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_user, smtp_password)
    server.sendmail(from_address, to_address, msg.as_string())

  except Exception as e:
    print(f'Failed to send email: {e}')

  finally:
    server.quit()