import smtplib
from email.mime.text import MIMEText

def send_sms(receiver_number, message):
    try:
        # নাম্বার থেকে স্পেস, ড্যাশ বা ফাঁকা জায়গা সম্পূর্ণ মুছে ফেলা
        clean_number = str(receiver_number).replace(" ", "").replace("-", "").strip()
        
        # যদি নাম্বারে +88 বা 88 থাকে, তা কেটে শুধু ১১ ডিজিট করা
        if clean_number.startswith("+88"):
            clean_number = clean_number[3:]
        elif clean_number.startswith("88"):
            clean_number = clean_number[2:]

        sms_gateway = f"{clean_number}@sms.banglalink.net"
        
        # ⚠️ আপনার সঠিক জিমেইল এবং জিমেইলের ১৬ অক্ষরের অ্যাপ পাসওয়ার্ডটি এখানে দিন (কোনো স্পেস রাখবেন না)
        sender_email = "flagcraft99@gmail.com"
        sender_app_password = "mmulraqreugchspb" 

        print(f"\n📡 [Banglalink Gateway] Forwarding match update to {sms_gateway}...")

        msg = MIMEText(message)
        msg['From'] = sender_email
        msg['To'] = sms_gateway
        msg['Subject'] = "Live Goal!"

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_app_password)
        server.sendmail(sender_email, sms_gateway, msg.as_string())
        server.quit()

        print(f"✅ SMS successfully sent to {clean_number}!")
        return True
        
    except Exception as e:
        print(f"❌ Banglalink SMS Gateway Error: {e}")
        print(f"💬 [Terminal Backup] Message: {message}")
        return True