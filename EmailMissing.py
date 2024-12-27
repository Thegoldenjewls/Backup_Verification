from datetime import datetime, timedelta
from collections import defaultdict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Read the content of message.txt
file_path = 'message.txt'  
with open(file_path, 'r') as file:
    lines = file.readlines()
backups = defaultdict(list)
invalid_entries = []

for line in lines:
    line = line.strip()
    if not line:  # Skip blank lines
        continue
    parts = line.split('/')
    if len(parts) > 1:
        image_info = parts[-1]
        date_part = image_info[:6]
        if date_part.isdigit() and len(date_part) == 6:  # Check for valid 6-digit date
            try:
                date = datetime.strptime(date_part, "%y%m%d")  # Parse the date
                image_id = image_info.split('_')[-1]  # Extract image identifier 
                backups[image_id].append(date_part)
            except ValueError as e:
                print(f"Invalid date format: {date_part} in line {line} - Error: {e}")
                invalid_entries.append(line)
        else:
            print(f"Skipping invalid date: {date_part} in line {line}")
            invalid_entries.append(line)
    else:
        print(f"Invalid line format: {line}")
        invalid_entries.append(line)

# Write invalid entries to a log file for review
with open('invalid_entries.log', 'w') as log_file:
    for entry in invalid_entries:
        log_file.write(f"{entry}\n")
# Convert dates to datetime objects and sort for each image
for image_id in backups:
    backups[image_id] = sorted([datetime.strptime(date, "%y%m%d") for date in backups[image_id]])

# Verify backups (check for each image if there are backups in the last two days)
start_date = datetime.strptime("241016", "%y%m%d")
missing_backups = []

for image_id, dates in backups.items():
    for i, date in enumerate(dates):
        if date < start_date:
            continue
        # Check if there is at least one backup in the last two days
        previous_two_days = {date - timedelta(days=1), date - timedelta(days=2)}
        if not previous_two_days.intersection(dates[:i]):
            missing_backups.append((image_id, date.strftime("%y%m%d")))

# Generate the email body
email_body = "Backup Verification Report\n\n"
if missing_backups:
    email_body += "The following backups are missing coverage for the last two days:\n\n"
    for image_id, missing_date in missing_backups:
        email_body += f"- Image: {image_id}, Date: {missing_date}\n"
else:
    email_body += "All backups are verified and present."

# Email configuration
sender_email = "BFAlerts2024@gmail.com"  
receiver_email = ""
email_password = ""

# Compose email
subject = "Backup Verification Report"
msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = subject
msg.attach(MIMEText(email_body, 'plain'))

# Send email
try:
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, email_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
    print("Email sent successfully!")
except Exception as e:
    print(f"Error: {e}")
