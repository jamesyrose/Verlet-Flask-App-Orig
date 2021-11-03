import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_mail(target, subject, content): 
    from_addr = 'do-not-reply@verlet.io'
    to_addrs = [target]
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = target
    msg['Subject'] = subject
    msg.attach(MIMEText(content, 'plain'))

    password = "donotreply"


    try:
        s = smtplib.SMTP('localhost')
        s.login(from_addr, password)
        s.sendmail(from_addr, to_addrs,  msg.as_string())
        s.quit()
    except smtplib.SMTPException:
        print("Error:", sys.exc_info()[0])


if __name__ == "__main__": 
    send_mail("2bengr@gmail.com", "HEYYYYYYYYYYYYYYYY", "DERP DERP DERP")
