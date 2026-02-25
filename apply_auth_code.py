import requests
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("UPSTOX_API_KEY")
CLIENT_SECRET = os.getenv("UPSTOX_API_SECRET")
REDIRECT_URI = "http://localhost:8501"
AUTH_CODE = "6KU8B-" # As provided by user

def exchange_and_save():
    url = "https://api.upstox.com/v2/login/authorization/token"
    data = {
        "code": AUTH_CODE,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
    
    print(f"📡 Exchanging code {AUTH_CODE} for Access Token...")
    res = requests.post(url, data=data, headers=headers)
    
    if res.status_code == 200:
        token_data = res.json()
        new_token = token_data.get('access_token')
        if new_token:
            print("\n✅ SUCCESS: New Token Received!")
            update_env(new_token)
            return True
    else:
        print(f"\n❌ FAILED: {res.status_code}")
        print(res.json())
    return False

def update_env(token):
    env_path = ".env"
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    with open(env_path, 'w') as f:
        found = False
        for line in lines:
            if line.startswith("UPSTOX_ACCESS_TOKEN="):
                f.write(f"UPSTOX_ACCESS_TOKEN={token}\n")
                found = True
            else:
                f.write(line)
        if not found:
            f.write(f"\nUPSTOX_ACCESS_TOKEN={token}\n")
    print("📝 .env file updated.")

if __name__ == "__main__":
    exchange_and_save()
