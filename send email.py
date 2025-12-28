import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase 
from email import encoders            
import os


MY_EMAIL = "madzivakupakwashe12@gmail.com"
MY_PASSWORD = "qkki wcmz ghce ttjp"  
EXCEL_FILE = r"C:\Users\ministryofstreets\Desktop\AIpply\companies_sample.csv"
CV_FILENAME = r"C:\Users\ministryofstreets\Desktop\AIpply\Kupakwashe_Madziva_CV.pdf"  
name="Kupakwashe Madziva"
# --- LOAD DATA ---
df = pd.read_csv(EXCEL_FILE)

# --- CONNECT TO SERVER ---
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(MY_EMAIL, MY_PASSWORD)
    print("Login Success!")
except Exception as e:
    print(f"Login Failed: {e}")
    exit()

# --- SEND EMAILS ---
for index, row in df.iterrows():
    company = row['company_name']
    recipient_email = row['company_email']

    print(f"Preparing email for {company}...")

    msg = MIMEMultipart()
    msg['From'] = MY_EMAIL
    msg['To'] = recipient_email
    msg['Subject'] = f"Application for Actuarial Intern Role - Kupakwashe Madziva - {company}"

    # The Body Text
    body = f"""
    Dear Sir/Madam,

    My {name} is Kupakwashe Madziva. I am writing to express my interest in the Actuarial opportunities at {company}.
    
    With a strong background in Actuarial Science and Data Science, I believe I can contribute effectively to your team.
    
    Please find my CV attached for your review.

    Best regards,
    Kupakwashe Madziva
    """
    msg.attach(MIMEText(body, 'plain'))

    # --- ATTACHMENT LOGIC START ---
    try:
        # Open the file in binary mode
        with open(CV_FILENAME, "rb") as attachment:
            # Create a MIME base object
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        
        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)
        
        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {CV_FILENAME}",
        )
        
        # Attach the instance 'part' to instance 'msg'
        msg.attach(part)
    except FileNotFoundError:
        print(f"❌ Error: Could not find the file '{CV_FILENAME}'. Check the name/folder.")
        continue # Skip to next company if CV is missing
    # --- ATTACHMENT LOGIC END ---

    # Send
    try:
        server.send_message(msg)
        print(f"✅ Email sent successfully to {company}!")
    except Exception as e:
        print(f"❌ Failed to send to {company}. Error: {e}")

# --- CLEANUP ---
server.quit()
print("Batch complete.")