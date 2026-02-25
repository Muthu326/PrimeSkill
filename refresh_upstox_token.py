import requests
import os
from dotenv import load_dotenv

# Use absolute path to ensure .env is found when run via Task Scheduler
ENV_PATH = os.path.join(os.getcwd(), ".env")
load_dotenv(ENV_PATH)

CLIENT_ID = os.getenv("UPSTOX_API_KEY")
CLIENT_SECRET = os.getenv("UPSTOX_API_SECRET")
REDIRECT_URI = "http://localhost:8501"

def save_token_to_env(new_token):
    """Saves the new access token back to the .env file."""
    if not os.path.exists(ENV_PATH):
        print("❌ .env file not found!")
        return False
        
    with open(ENV_PATH, 'r') as f:
        lines = f.readlines()
        
    with open(ENV_PATH, 'w') as f:
        found = False
        for line in lines:
            if line.startswith("UPSTOX_ACCESS_TOKEN="):
                f.write(f"UPSTOX_ACCESS_TOKEN={new_token}\n")
                found = True
            else:
                f.write(line)
        if not found:
            f.write(f"\nUPSTOX_ACCESS_TOKEN={new_token}\n")
            
    print("✅ .env file updated with new Access Token.")
    return True

def test_api_connection(access_token):
    """Tests if the current token is still valid."""
    if not access_token: return False
    url = "https://api.upstox.com/v2/user/profile"
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    try:
        response = requests.get(url, headers=headers)
        return response.status_code == 200
    except:
        return False

def generate_new_token():
    """Starts the handshake flow to get a new token."""
    login_url = f"https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
    print("\n🚀 UPSTOX TOKEN REFRESH REQUIRED")
    print("-" * 50)
    print(f"1. Login here: {login_url}")
    print("2. After login, copy the 'code' from the URL (e.g., ?code=XXXXXX)")
    print("-" * 50)
    
    auth_code = input("\nEnter the auth code: ").strip()
    if not auth_code:
        print("❌ No code entered.")
        return None

    # Exchange for token
    url = "https://api.upstox.com/v2/login/authorization/token"
    data = {
        "code": auth_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
    
    res = requests.post(url, data=data, headers=headers)
    if res.status_code == 200:
        new_token = res.json().get('access_token')
        if new_token:
            save_token_to_env(new_token)
            return new_token
    else:
        print(f"❌ Failed to get token: {res.status_code}")
        print(res.json())
    return None

def main():
    current_token = os.getenv("UPSTOX_ACCESS_TOKEN")
    if test_api_connection(current_token):
        print("🟢 Token is still VALID. No refresh needed.")
    else:
        print("🔴 Token is EXPIRED or MISSING.")
        generate_new_token()

if __name__ == "__main__":
    main()
