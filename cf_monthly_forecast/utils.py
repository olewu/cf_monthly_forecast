import smtplib
from cf_monthly_forecast.config import email_address 

def send_email(SUBJECT,TEXT,TO=[email_address],FROM = email_address):
    """
    send an email from email address defined in config.py to TO (must be list) with subject SUBJECT and message TEXT, both strings.
    """
    # Prepare actual message
    message = '''From: {0:s}
To: {1:s}
Subject: {2:s}

{3:s}
    '''.format(FROM, ', '.join(TO), SUBJECT, TEXT)

    # Send the mail
    server = smtplib.SMTP('localhost')
    server.sendmail(FROM, TO, message)
    server.quit()