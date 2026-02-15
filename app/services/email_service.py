import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_confirmation_email(patient_email, patient_name, appt_details):
    # Load settings from .env
    smtp_user = os.getenv("MAILTRAP_USER")
    smtp_pass = os.getenv("MAILTRAP_PASS")
    smtp_host = os.getenv("MAILTRAP_HOST")
    smtp_port = os.getenv("MAILTRAP_PORT")

    # Create the email object
    message = MIMEMultipart()
    message["From"] = "clinic@smart-care.com"  
    message["To"] = patient_email
    message["Subject"] = "Appointment Confirmed!"

    
    html = f"""
    <html>
      <body>
        <h3>Hello {patient_name},</h3>
        <p>Your appointment has been <b>Confirmed</b>.</p>
        <p>Details: {appt_details}</p>
        <br/>
        <p>Best regards,<br/>The SmartCare Team</p>
      </body>
    </html>
    """
    message.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(message["From"], [patient_email], message.as_string())
        print(f"✅ SUCCESS: Email sent to {patient_email}") 
    except Exception as e:
        print(f"❌ EMAIL ERROR: {str(e)}") 