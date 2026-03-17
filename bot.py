import os
import json
import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, db

def run_bot():
    try:
        firebase_key_raw = os.getenv('FIREBASE_KEY')
        firebase_url = os.getenv('FIREBASE_URL')

        if not firebase_admin._apps:
            key_dict = json.loads(firebase_key_raw)
            cred = credentials.Certificate(key_dict)
            firebase_admin.initialize_app(cred, {'databaseURL': firebase_url})

        url = "https://www.cricbuzz.com/cricket-match/live-scores"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Sabse pehla match header dhoondna
        match_header = soup.find('h3', class_='cb-lv-scr-mtch-hdr') or soup.find('h2')
        
        if match_header:
            teams = match_header.text
            
            # Score aur Status ke liye wide search
            status = "Check Cricbuzz for details"
            status_element = soup.find('div', class_='cb-text-live') or \
                             soup.find('div', class_='cb-text-preview') or \
                             soup.find('div', class_='cb-mtch-cptn')
            
            if status_element:
                status = status_element.text

            score = "Toss/Live Soon"
            score_element = soup.find('div', class_='cb-scr-wkt-bat')
            if score_element:
                score = score_element.text

            # Firebase Update
            ref = db.reference('matches/match_01/live_score')
            ref.update({
                'teams': teams,
                'runs': score,
                'status': status,
                'last_updated': "Live from Server"
            })
            print(f"Match Found: {teams} | Status: {status}")
        else:
            print("Still no match card found. Link is active but structure is different.")
            db.reference('matches/match_01/live_score').update({'status': 'Robot searching...'})

    except Exception as e:
        print(f"Bot Error: {e}")

if __name__ == "__main__":
    run_bot()
