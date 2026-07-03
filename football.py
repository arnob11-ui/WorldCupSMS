import requests
import time
from sms import send_sms  # sms.py থেকে ফাংশন কল করা হচ্ছে

# ⚠️ আপনার আসল API Key-টি এখানে বসান
FOOTBALLDATA_IO_API_KEY = "fd_f07aea0676b3b130232009780b5326b42e441a2f39fb3804"  

def get_live_matches():
    try:
        url = "https://footballdata.io/api/v1/fixtures/today"
        headers = {
            "Authorization": f"Bearer {FOOTBALLDATA_IO_API_KEY}"
        }
        
        print("\n🔄 Fetching today's matches from Footballdata.io...")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # যদি এপিআই রেসপন্স টেক্সট বা স্ট্রিং হয়, তাকে জেসন-এ কনভার্ট করা
            try:
                raw_matches = response.json()
            except Exception:
                print("⚠️ API response is not a valid JSON string.")
                return []
            
            if not isinstance(raw_matches, (dict, list)):
                return []
                
            if isinstance(raw_matches, dict):
                fixtures_list = raw_matches.get("fixtures", raw_matches.get("data", []))
            else:
                fixtures_list = raw_matches
            
            real_matches = []
            for match in fixtures_list:
                if not isinstance(match, dict):
                    continue
                    
                status = str(match.get("status", "")).lower()
                
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

last_known_scores = {}

def monitor_matches():
    print("\n🚀 Live Football SMS Bot started successfully!")
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
            
            if m_id not in last_known_scores:
                last_known_scores[m_id] = current_score_key
                start_msg = f"Match Live: {h_team} vs {a_team}\nScore: {h_score}-{a_score}"
                send_sms("01916939746", start_msg)
            elif last_known_scores[m_id] != current_score_key:
                last_known_scores[m_id] = current_score_key
                goal_msg = f"⚽ GOAL!!!\n{h_team} {h_score} - {a_score} {a_team}"
                send_sms("01916939746", goal_msg)
                
        time.sleep(60)

if __name__ == "__main__":
    monitor_matches()