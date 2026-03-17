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

        # Cricbuzz Live Scores Page
        url = "https://www.cricbuzz.com/live-cricket-scores" 
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Match Card dhoondna
        match_card = soup.find('div', class_='cb-mtch-lst')
        
        if match_card:
            # 1. Team Names (e.g., RCB vs SRH)
            teams = match_card.find('h3').text if match_card.find('h3') else "Match Update"
            
            # 2. Score (Agar match shuru nahi hua toh ye empty hoga)
            score_box = match_card.find('div', class_='cb-scr-wkt-bat')
            score = score_box.text if score_box else "0/0 (0.0)"
            
            # 3. Status (Yahan "Toss" ki details milti hain)
            # Cricbuzz par 'cb-text-preview' ya 'cb-text-live' mein details hoti hain
            status = "Match Details Loading..."
            status_div = match_card.find('div', class_='cb-text-live') or \
                         match_card.find('div', class_='cb-text-preview') or \
                         match_card.find('div', class_='cb-mtch-cptn')
            
            if status_div:
                status = status_div.text

            # Firebase mein update karna
            ref = db.reference('matches/match_01/live_score')
            ref.update({
                'teams': teams,
                'runs': score,
                'status': status,
                'last_updated': "Toss/Live Update"
            })
            print(f"Success: {teams} | Status: {status}")
        else:
            print("No Match Card found. Shyad abhi koi match schedule nahi hai.")

    except Exception as e:
        print(f"Bot Error: {e}")

if __name__ == "__main__":
    run_bot()
