from flask import Flask, render_template, jsonify, request
import threading
import time
import sqlite3
from football import get_live_matches
from sms import send_sms
import database

app = Flask(__name__)

# গ্লোবাল ভ্যারিয়েবল ও ক্যাশ
live_games_cache = []
previous_scores = {}
sms_sent_counter = 0  # রান টাইম-এ মোট কতটি SMS ট্রিগার হলো তার হিসাব রাখবে

def background_match_tracker():
    """ব্যাকগ্রাউন্ডে প্রতি ৩০ সেকেন্ড পর পর ম্যাচ ট্র্যাক করবে এবং ডাটাবেজ থেকে নাম্বার নিয়ে SMS পাঠাবে"""
    global live_games_cache, previous_scores, sms_sent_counter
    print("🔄 Background Live Tracking Thread Started...")
    
    while True:
        live_games = get_live_matches()
        live_games_cache = live_games
        
        current_scores = {}
        for match in live_games:
            match_id = match.get('match_id')
            home_name = match.get('home_team', {}).get('team_name', 'Home')
            away_name = match.get('away_team', {}).get('team_name', 'Away')
            home_score = match.get('home_score', 0)
            away_score = match.get('away_score', 0)
            
            current_scores[match_id] = {'home': home_score, 'away': away_score}
            
            if match_id in previous_scores:
                prev = previous_scores[match_id]
                msg = ""
                
                if home_score > prev['home']:
                    msg = f"🚨 GOAL!!! {home_name} scored!\nScore: {home_name} {home_score} - {away_score} {away_name}"
                elif away_score > prev['away']:
                    msg = f"🚨 GOAL!!! {away_name} scored!\nScore: {home_name} {home_score} - {away_score} {away_name}"
                
                # যদি গোল হয়, তবে ডাটাবেজ থেকে সাবস্ক্রাইবার নিয়ে SMS পাঠাবে
                if msg:
                    print(msg)
                    subscribers = database.get_subscribers_for_match(match_id)
                    print(f"👥 Found {len(subscribers)} subscribers for match ID {match_id}")
                    
                    for phone in subscribers:
                        if send_sms(phone, msg):
                            sms_sent_counter += 1  # সফলভাবে গেটওয়েতে হিট হলে কাউন্টার ১ বাড়বে

        previous_scores = current_scores
        time.sleep(30)

# ---- FLASK WEB ROUTES ----

@app.route('/')
def dashboard():
    """মেইন ড্যাশবোর্ড লোড করবে"""
    return render_template('index.html')

@app.route('/api/live-matches')
def api_live_matches():
    """লাইভ ম্যাচের ডেটা ফ্রন্টএন্ডে পাঠাবে"""
    return jsonify(live_games_cache)

@app.route('/api/subscribe', methods=['POST'])
def api_subscribe():
    """ফোন নাম্বার ও ম্যাচ আইডি ডাটাবেজে সেভ করবে"""
    data = request.json
    phone_number = data.get('phone_number')
    match_id = data.get('match_id')
    
    if not phone_number or not match_id:
        return jsonify({"error": "Missing phone number or match ID"}), 400
        
    success = database.add_subscription(phone_number, match_id)
    if success:
        return jsonify({"message": "Subscribed successfully!"}), 200
    else:
        return jsonify({"error": "You are already subscribed to this match!"}), 400

@app.route('/api/stats')
def api_stats():
    """টপ বার-এর Tracked Matches এবং SMS Sent বক্স ডাইনামিক করার API"""
    global sms_sent_counter
    try:
        conn = sqlite3.connect(database.DB_NAME)
        cursor = conn.cursor()
        
        # ইউনিক কয়টি ম্যাচ মানুষ এই পর্যন্ত সাবস্ক্রাইব করেছে
        cursor.execute("SELECT COUNT(DISTINCT match_id) FROM subscriptions")
        tracked_matches = cursor.fetchone()[0]
        
        conn.close()
        return jsonify({
            "tracked_matches": tracked_matches,
            "sms_sent": sms_sent_counter
        })
    except Exception as e:
        print(f"❌ Stats API Error: {e}")
        return jsonify({"tracked_matches": 0, "sms_sent": 0})

if __name__ == '__main__':
    # ডাটাবেজ টেবিল ক্রিয়েট করা নিশ্চিত করছি
    database.init_db()
    
    # ব্যাকগ্রাউন্ড প্রসেস চালু করা
    tracker_thread = threading.Thread(target=background_match_tracker, daemon=True)
    tracker_thread.start()
    
    # ৫০00 পোর্টে সার্ভার রান করা
    app.run(debug=True, port=5000)