import requests
import webbrowser
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("UPSTOX_API_KEY")
CLIENT_SECRET = os.getenv("UPSTOX_API_SECRET")
REDIRECT_URI = "http://localhost:8501"

def generate_login_url():
    """Step 1: Generate Login URL"""
    login_url = f"https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
    print("\n🚀 Step 1: Open this URL in your browser to login:")
    print("-" * 50)
    print(login_url)
    print("-" * 50)
    # webbrowser.open(login_url)

def exchange_code_for_token(auth_code):
    """Step 2: Exchange Authorization Code for Access Token"""
    url = "https://api.upstox.com/v2/login/authorization/token"
    data = {
        "code": auth_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
    
    response = requests.post(url, data=data, headers=headers)
    if response.status_code == 200:
        token_data = response.json()
        print("\n✅ SUCCESS: Token Received!")
        print(f"Access Token: {token_data.get('access_token')}")
        return token_data.get('access_token')
    else:
        print(f"\n❌ ERROR: {response.status_code}")
        print(response.json())
        return None

def test_api_connection(access_token):
    """Step 3: Test API Connection by fetching user profile"""
    url = "https://api.upstox.com/v2/user/profile"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        profile = response.json()
        print("\n🎉 CONNECTION SUCCESSFUL!")
        print(f"Welcome, {profile.get('data', {}).get('user_name')}!")
        print(f"User ID: {profile.get('data', {}).get('user_id')}")
        return True
    else:
        print(f"\n❌ API TEST FAILED: {response.status_code}")
        print(response.json())
        return False

if __name__ == "__main__":
    print("💎 UPSTOX API HANDSHAKE MODULE")
    print("=" * 30)
    
    current_token = os.getenv("UPSTOX_ACCESS_TOKEN")
    
    if current_token:
        print("🔍 Found existing token in .env. Testing connection...")
        if not test_api_connection(current_token):
            print("\n💡 Token might be expired. Let's generate a new one.")
            generate_login_url()
            code = input("\nEnter the 'code' from the redirected URL: ")
            if code:
                exchange_code_for_token(code)
    else:
        generate_login_url()
        code = input("\nEnter the 'code' from the redirected URL: ")
        if code:
            exchange_code_for_token(code)
