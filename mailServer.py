from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


def sendDigitEmail(to_address, digit):
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
    
def sendInvitEmail(to_address, person, doc, date):
  smtp_server = 'smtp.gmail.com'
  smtp_port = 587
  smtp_user = 'amstech.senegal@gmail.com'
  smtp_password = 'fhcw nipa qqsg lmwk'
  from_address = 'amstech.senegal@gmail.com'

  subject = 'SignAuth - Demande de signature'
  body = f"""
    <html>
      <body>
        <p>Vous avez une nouvelle demande de signature.</p>
        <br/>
        <p><b>{person}</b> vous invite à signer un document.</p>
        <p>La demande est effective depuis le {date.split(" ")[1]} à {date.split(" ")[0]}.</p>
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