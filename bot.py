import os
import json
import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, db

def run_bot():
    try:
        # 1. GitHub Secrets se Firebase ki Details nikalna
        firebase_key_raw = os.getenv('FIREBASE_KEY')
        firebase_url = os.getenv('FIREBASE_URL')

        if not firebase_key_raw or not firebase_url:
            print("Error: Firebase Secrets nahi mile!")
            return

        # 2. Firebase Initialize karna
        key_dict = json.loads(firebase_key_raw)
        if not firebase_admin._apps:
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred, {'databaseURL': firebase_url})

        # 3. Live Score Scrape karna (Example: Cricbuzz Live Match Page)
        # Note: Match ke din ye URL asli live match link se badal dena
        url = "https://www.cricbuzz.com/cricket-match/live-scores" 
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 4. Score nikalne ka logic
        # Hum pehle match ka score utha rahe hain example ke liye
        match_card = soup.find('div', class_='cb-mtch-lst cb-col cb-col-100 cb-tms-itm')
        
        if match_card:
            teams = match_card.find('h3', class_='cb-lv-scr-mtch-hdr').text
            score = match_card.find('div', class_='cb-scr-wkt-bat').text
            status = match_card.find('div', class_='cb-text-live').text if match_card.find('div', class_='cb-text-live') else "Match Finished"

            # 5. Firebase mein Data Update karna
            ref = db.reference('matches/match_01/live_score')
            ref.update({
                'teams': teams,
                'runs': score,
                'status': status
            })
            print(f"Success: Updated {teams} - {score}")
        else:
            print("No live match found on the page.")

    except Exception as e:
        print(f"Bot Error: {e}")

if __name__ == "__main__":
    run_bot()
