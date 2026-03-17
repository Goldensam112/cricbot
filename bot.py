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
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Sabse pehla Match Card dhoondna (Videos ko skip karke)
        match_card = soup.find('div', class_='cb-mtch-lst')
        
        if match_card:
            # Team names nikalna (Header se)
            teams = match_card.find('h3').text if match_card.find('h3') else "Match Update"
            
            # Agar "Featured Videos" jaisa kuch mile toh use filter kar do
            if "VIDEO" in teams.upper():
                print("Video card detected, skipping...")
                return

            score = "0/0 (0.0)"
            score_element = match_card.find('div', class_='cb-scr-wkt-bat')
            if score_element:
                score = score_element.text

            status = "Match Details Loading..."
            status_element = match_card.find('div', class_='cb-text-live') or \
                             match_card.find('div', class_='cb-text-preview') or \
                             match_card.find('div', class_='cb-mtch-cptn')
            if status_element:
                status = status_element.text

            # Firebase Update
            ref = db.reference('matches/match_01/live_score')
            ref.update({
                'teams': teams,
                'runs': score,
                'status': status,
                'last_updated': "Live from Server"
            })
            print(f"Success: {teams} updated!")
        else:
            print("No valid match card found.")

    except Exception as e:
        print(f"Bot Error: {e}")

if __name__ == "__main__":
    run_bot()
