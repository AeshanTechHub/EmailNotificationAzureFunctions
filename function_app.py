import azure.functions as func
import logging
import os
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail,Attachment, ContentId
from jinja2 import Environment, FileSystemLoader


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader('templates'))

@app.route(route="send_email")
def send_email(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function to send email processed a request.')

    email = req.params.get('email')
    subject = req.params.get('subject')
    recipient_name = req.params.get('recipient_name')
    body_content = req.params.get('body_content')
    if not email:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            email = req_body.get('email')
            subject = req_body.get('subject')
            recipient_name = req_body.get('recipient_name')
            body_content = req_body.get('body_content')

    if email:
        # Read and encode the image
        image_path = os.path.join(os.path.dirname(__file__), 'images', 'ath_logo.png')
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')

        # Create the attachment
        attachment = Attachment()
        attachment.file_content = image_base64
        attachment.file_type = 'image/png'
        attachment.file_name = 'ath_logo.png'
        attachment.disposition = 'inline'
        attachment.content_id = 'ath_logo'

        # Render the HTML content with the CID
        template = env.get_template('email_body.jinja')
        html_content = template.render(recipient_name=recipient_name, body_content=body_content, image_cid='ath_logo')

        message = Mail(
            from_email='shamen1209@gmail.com',
            to_emails=email,
            subject=subject,
            html_content=html_content
        )
        message.add_attachment(attachment)
        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_APIKEY'))
            response = sg.send(message)
            logging.info(response.status_code)
            logging.info(response.body)
            logging.info(response.headers)
            return func.HttpResponse(f"Email sent to {email}.", status_code=200)
        except Exception as e:
            logging.error(e)
            return func.HttpResponse(f"Failed to send email to {email}.", status_code=500)
    else:
        return func.HttpResponse(
             "Please pass an email in the query string or in the request body.",
             status_code=400
        )