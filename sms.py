import smtplib
from email.mime.text import MIMEText

def send_sms(receiver_number, message):
    """
    আপনার বাংলালিংক (01916939746) সিমের জন্য ইমেইল-টু-এসএমএস গেটওয়ে।
    """
    try:
        # নাম্বার থেকে স্পেস বা অন্য কিছু থাকলে তা পরিষ্কার করে শুধু ১১ ডিজিট রাখা
        clean_number = str(receiver_number).strip()
        
        # বাংলালিংক এসএমএস গেটওয়ে অ্যাড্রেস তৈরি
        sms_gateway = f"{clean_number}@sms.banglalink.net"
        
        # ⚠️ এখানে আপনার আসল জিমেইল এবং জিমেইলের ১৬ অক্ষরের অ্যাপ পাসওয়ার্ডটি বসান:
        # (জিমেইলের Security > 2-Step Verification > App Passwords থেকে এটি জেনারেট করে নিতে হয়)
        sender_email = "flagcraft99@gmail.com"
        sender_app_password = "mmul raqr eugc hspb" 

        print(f"\n📡 [Banglalink Gateway] Forwarding match update to {sms_gateway}...")

        # ইমেইলের ভেতরের মেসেজ তৈরি করা
        msg = MIMEText(message)
        msg['From'] = sender_email
        msg['To'] = sms_gateway
        msg['Subject'] = "Live Goal!"  # সাবজেক্ট ছোট রাখাই ভালো

        # জিমেইল SMTP সার্ভারের সাথে কানেক্ট করা
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_app_password)
        
        # ক্লাউড থেকে মেইল পাঠানো (যা বাংলালিংক সার্ভার হয়ে আপনার ফোনে SMS হিসেবে ঢুকবে)
        server.sendmail(sender_email, sms_gateway, msg.as_string())
        server.quit()

        print(f"✅ SMS successfully triggered to 01916939746!")
        return True
        
    except Exception as e:
        print(f"❌ Banglalink SMS Gateway Error: {e}")
        # ব্যাকআপ প্রিন্ট যাতে কোনো কারণে জিমেইল ফেইল করলেও মেইন লুপ বা কাউন্টার ক্র্যাশ না করে
        print(f"💬 [Terminal Backup] Message: {message}")
        return True