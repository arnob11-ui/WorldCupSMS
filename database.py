import sqlite3

DB_NAME = "worldcup_bot.db"

def init_db():
    """ডাটাবেজ এবং টেবিল তৈরি করার ফাংশন"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # ইউজারদের সাবস্ক্রিপশন টেবিল (id, phone_number, match_id)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT NOT NULL,
            match_id INTEGER NOT NULL,
            UNIQUE(phone_number, match_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("💾 Database Initialized Successfully!")

def add_subscription(phone_number, match_id):
    """নতুন কোনো ফোন নাম্বারকে নির্দিষ্ট ম্যাচের জন্য সাবস্ক্রাইব করানো"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO subscriptions (phone_number, match_id) VALUES (?, ?)",
            (phone_number, match_id)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        # অলরেডি সাবস্ক্রাইব করা থাকলে এরর এড়াতে False দেবে
        return False

def get_subscribers_for_match(match_id):
    """একটি নির্দিষ্ট ম্যাচের জন্য কোন কোন নাম্বারে SMS পাঠাতে হবে তা বের করা"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT phone_number FROM subscriptions WHERE match_id = ?", (match_id,))
    rows = cursor.fetchall()
    conn.close()
    
    # [('01711...',), ('01822...',)] থেকে শুধু নাম্বারের লিস্ট ['01711...', '01822...'] বানাবে
    return [r[0] for r in rows]

# ফাইলটি সরাসরি রান করলে ডাটাবেজ টেবিল তৈরি হবে
if __name__ == "__main__":
    init_db()