import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def send_report_email(sender_email, sender_password, recipient_email, report_path, folder_path):
    """
    Sends the generated report via Email using SMTP.
    """
    try:
        # 1. Setup the Email Content
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"📊 Analysis Report: {os.path.basename(folder_path)}"

        body = f"""
        Hello,

        Attached is the folder analysis report for:
        📂 {folder_path}

        This is an automated message from your Data Folder Analyzer.
        """
        msg.attach(MIMEText(body, 'plain'))

        # 2. Attach the Report File
        if os.path.exists(report_path):
            with open(report_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            
            # Encode file in ASCII characters to send by email
            encoders.encode_base64(part)
            
            # Add header as key/value pair to attachment part
            filename = os.path.basename(report_path)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )
            
            msg.attach(part)
        else:
            print(f"⚠️ Warning: Report file not found at {report_path}. Sending email without attachment.")

        # 3. Connect to Gmail SMTP Server (Securely)
        # Using port 587 for TLS (Transport Layer Security)
        print("📨 Connecting to Email Server...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls() # Secure the connection
        
        # 4. Login
        server.login(sender_email, sender_password)
        
        # 5. Send Email
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        
        print(f"✅ Email sent successfully to: {recipient_email}")
        return True

    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False