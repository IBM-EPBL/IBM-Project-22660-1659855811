from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_mail(to, msg):
    message = Mail(
        from_email='asokankamalesh@gmail.com',
        to_emails= to,
        subject='Your password',
        html_content=f'<strong>Your password is {msg}</strong>')
    try:
        sg = SendGridAPIClient('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')
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)
