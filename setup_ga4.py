"""
Quick Setup Script for Google Analytics 4 Integration
Property ID: 503112581
"""

import os
import subprocess
import sys

def check_gcloud_installed():
    """Check if Google Cloud SDK is installed"""
    try:
        result = subprocess.run(['gcloud', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Google Cloud SDK is installed")
            return True
        else:
            print("❌ Google Cloud SDK not found")
            return False
    except FileNotFoundError:
        print("❌ Google Cloud SDK not found")
        return False

def authenticate_gcloud():
    """Authenticate with Google Cloud"""
    try:
        print("🔐 Starting Google Cloud authentication...")
        print("📝 This will open your browser to sign in with your Google account")
        print("📋 Make sure to use the same Google account that has access to your GA4 property")
        
        result = subprocess.run(['gcloud', 'auth', 'application-default', 'login'], 
                              capture_output=False)
        
        if result.returncode == 0:
            print("✅ Authentication successful!")
            return True
        else:
            print("❌ Authentication failed")
            return False
    except Exception as e:
        print(f"❌ Error during authentication: {e}")
        return False

def test_ga_connection():
    """Test the Google Analytics connection"""
    try:
        print("🧪 Testing Google Analytics connection...")
        from google_analytics import get_google_analytics_data
        
        data = get_google_analytics_data()
        
        if data['is_live_data']:
            print("🎉 SUCCESS! Google Analytics 4 is connected and working!")
            print(f"📊 Found {len(data['page_views'])} pages with data")
            print(f"👥 Active users: {data['metrics']['active_users']}")
            print(f"📈 Page views: {data['metrics']['page_views']}")
        else:
            print("⚠️ Still using demo data. Check authentication and permissions.")
            
        return data['is_live_data']
        
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Google Analytics 4 Setup for Property ID: 503112581")
    print("=" * 60)
    
    # Step 1: Check if gcloud is installed
    if not check_gcloud_installed():
        print("\n📥 Please install Google Cloud SDK:")
        print("🔗 https://cloud.google.com/sdk/docs/install")
        print("\nAfter installation, run this script again.")
        return
    
    # Step 2: Authenticate
    print("\n🔐 Step 1: Authenticate with Google Cloud")
    if not authenticate_gcloud():
        print("❌ Authentication failed. Please try again.")
        return
    
    # Step 3: Test connection
    print("\n🧪 Step 2: Testing Google Analytics connection...")
    if test_ga_connection():
        print("\n🎉 SETUP COMPLETE!")
        print("✅ Your dashboard will now show real Google Analytics data")
        print("🌐 Visit http://127.0.0.1:5000/dashboard to see live data")
    else:
        print("\n⚠️ Setup incomplete. Please check:")
        print("1. Your Google account has access to GA4 property 503112581")
        print("2. Google Analytics Reporting API is enabled")
        print("3. You have Viewer permissions in Google Analytics")

if __name__ == "__main__":
    main()
