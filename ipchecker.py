import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time


#Variables
ip_history = ['000.000.000.000']


#Request Function
#Requesting my IP from ipify
def get_external_ip():
    try:
        #Getting IP from ipify API
        responce = requests.get('https://api64.ipify.org?format=json')
        data = responce.json()
        external_ip = data['ip']
        return external_ip
    
    except requests.RequestException as e:
        print(f'Error: {e}')
        return None

#Check IP Function
#Takes the collected IP and checks it against the previous IP for changes
def check_external_ip(get_external_ip, ip_history):
    external_ip = get_external_ip()
    if external_ip:
        if external_ip != ip_history[0]:
            print(f'Your external IP is now {external_ip}')
            ip_history.clear()
            ip_history.append(external_ip)
            return external_ip
        else:
            print(f'Your external IP is still {ip_history}')
            return None
    else:
        print('IP check failure')

#SMTP 
def email_ip(external_ip):
    brevo_smtp_server = 'YOUR SERVER'
    brevo_smtp_port = YOUR PORT NUMBER
    brevo_username = 'YOUR USERNAME'
    brevo_password = 'YOUR PASSWORD'
    sender_email = 'YOUR EMAIL'
    recipient_email = 'YOUR EMAIL'

    subject = 'Server IP Change'
    body = f'Your routers IP has changed to: {external_ip}'

    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(brevo_smtp_server, brevo_smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(brevo_username, brevo_password)
            server.sendmail(sender_email, recipient_email, message.as_string())
            print('Email was sucessful')
    except smtplib.SMTPException as e:
        print(f'Error: {e}')


while True:
    external_ip = check_external_ip(get_external_ip, ip_history)
    if external_ip == None:
        print('No Change')
    else:
        email_ip(external_ip)
        print(f'Email {external_ip} sent')
    time.sleep(10)
