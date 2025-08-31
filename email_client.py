import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import grpc
import demo_pb2
import demo_pb2_grpc

class EmailService(demo_pb2_grpc.EmailServiceServicer):
    def SendOrderConfirmation(self, request, context):
        try:
            sender = os.environ['EMAIL_SENDER']
            recipient = request.email

            subject = "Your Order is Complete!"
            html = f"""
            <html>
              <body style="font-family: Arial, sans-serif;">
                <h2>Your order is complete! 🎉</h2>
                <p>We've sent you a confirmation email.</p>
                <p><b>Confirmation #</b><br>{request.confirmation_id}</p>
                <p><b>Tracking #</b><br>{request.tracking_id}</p>
                <p><b>Total Paid</b><br>${request.total_paid}</p>
                <hr>
                <p>Thank you for shopping with us!</p>
              </body>
            </html>
            """

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = sender
            msg["To"] = recipient
            msg.attach(MIMEText(html, "html"))

            with smtplib.SMTP(os.environ['SMTP_HOST'], int(os.environ['SMTP_PORT'])) as server:
                server.starttls()
                server.login(os.environ['SMTP_USER'], os.environ['SMTP_PASS'])
                server.sendmail(sender, recipient, msg.as_string())

            return demo_pb2.SendOrderConfirmationResponse(success=True)
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return demo_pb2.SendOrderConfirmationResponse(success=False)
