import requests
import smtplib
from email.mime.text import MIMEText
import time

# ==================== ⚙️ কনফিগারেশন সেকশন ====================

# ⚠️ ১. image_f68bec.png ড্যাশবোর্ড থেকে আপনার সম্পূর্ণ অ্যাক্টিভ API Key-টি এখানে বসান
FOOTBALLDATA_IO_API_KEY = "fd_f07aea0676b3b130232009780b5326b42e441a2f39fb3804"  

# ⚠️ ২. আপনার জিমেইল এবং জিমেইলের ১৬ অক্ষরের অ্যাপ পাসওয়ার্ডটি এখানে বসান
SENDER_EMAIL = "flagcraft99@gmail.com"
SENDER_APP_PASSWORD = "mmul raqr eugc hspb" 

# আপনার বাংলালিংক নাম্বার (অলরেডি সেট করা আছে)
TARGET_NUMBER = "01916939746"

# ============================================================

def send_sms_via_email(message):
    """
    বাংলালিংক ইমেইল-টু-এসএমএস গেটওয়ে ব্যবহার করে সম্পূর্ণ ফ্রিতে SMS পাঠানোর ফাংশন।
    """
    try:
        sms_gateway = f"{TARGET_NUMBER}@sms.banglalink.net"
        
        msg = MIMEText(message)
        msg['From'] = SENDER_EMAIL
        msg['To'] = sms_gateway
        msg['Subject'] = "Match Alert"

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, sms_gateway, msg.as_string())
        server.quit()
        
        print(f"✅ SMS successfully sent to {TARGET_NUMBER}!")
        return True
    except Exception as e:
        print(f"❌ SMS Sending Failed: {e}")
        print(f"💬 [Backup Terminal Display]: {message}")
        return False


def get_live_matches():
    """
    Footballdata.io API থেকে সরাসরি আজকের লাইভ ম্যাচের ডাটা নিয়ে আসার ফাংশন।
    """
    try:
        url = "https://footballdata.io/api/v1/fixtures/today"
        headers = {
            "Authorization": f"Bearer {FOOTBALLDATA_IO_API_KEY}"
        }
        
        print("\n🔄 Fetching today's matches from Footballdata.io...")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            raw_matches = response.json()
            
            # API রেসপন্স ফরম্যাট হ্যান্ডেল করা
            if isinstance(raw_matches, dict):
                fixtures_list = raw_matches.get("fixtures", raw_matches.get("data", []))
            else:
                fixtures_list = raw_matches
            
            real_matches = []
            
            for match in fixtures_list:
                status = str(match.get("status", "")).lower()
                
                # শুধু লাইভ বা রানিং ম্যাচগুলো ফিল্টার করা
                if "live" in status or "play" in status or status == "live":
                    match_structure = {
                        "match_id": match.get("id") or match.get("fixture_id") or 999,
                        "home_team": match.get("home_team_name") or match.get("home_team", {}).get("name") or "Home",
                        "away_team": match.get("away_team_name") or match.get("away_team", {}).get("name") or "Away",
                        "home_score": match.get("home_score") if match.get("home_score") is not None else 0,
                        "away_score": match.get("away_score") if match.get("away_score") is not None else 0
                    }
                    real_matches.append(match_structure)
                    
            return real_matches
        else:
            print(f"⚠️ API Error. Status Code: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error fetching from Footballdata.io: {e}")
        return []


# লাইভ স্কোর ট্র্যাক করার জন্য মেমোরি ডিকশনারি
last_known_scores = {}

def monitor_matches():
    """
    ২৪/৭ ব্যাকগ্রাউন্ডে ম্যাচ মনিটর করার এবং গোল হলে ফ্রি SMS ট্রিগার করার মেইন লুপ।
    """
    print("\n🚀 Live Football SMS Bot started successfully on Cloud!")
    print(f"📱 Target Phone Number: {TARGET_NUMBER}")
    
    while True:
        live_matches = get_live_matches()
        
        if not live_matches:
            print("😴 No live matches running right now. Checking again in 1 minute...")
        
        for match in live_matches:
            m_id = match["match_id"]
            h_team = match["home_team"]
            a_team = match["away_team"]
            h_score = match["home_score"]
            a_score = match["away_score"]
            
            current_score_key = f"{h_score}-{a_score}"
            
            # যদি এই ম্যাচটি আগে ট্র্যাক করা না হয়ে থাকে (নতুন লাইভ ম্যাচ)
            if m_id not in last_known_scores:
                last_known_scores[m_id] = current_score_key
                # ম্যাচ শুরুর একটা অ্যালার্ট পাঠানো (ঐচ্ছিক)
                start_msg = f"Match Live: {h_team} vs {a_team}\nScore: {h_score}-{a_score}"
                send_sms_via_email(start_msg)
            
            # যদি স্কোর পরিবর্তন হয় (গোল হয়)
            elif last_known_scores[m_id] != current_score_key:
                last_known_scores[m_id] = current_score_key
                
                # গোলের কাস্টম SMS বডি তৈরি
                goal_msg = f"⚽ GOAL!!!\n{h_team} {h_score} - {a_score} {a_team}\nKeep watching!"
                send_sms_via_email(goal_msg)
                
        # প্রতি ৬০ সেকেন্ড পর পর চেক করবে (যাতে এপিআই লিমিট শেষ না হয়)
        time.sleep(60)

if __name__ == "__main__":
    monitor_matches()