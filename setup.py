#!/usr/bin/env python3
"""
Setup script for Shopify WhatsApp Launcher App
This script helps you set up the app with proper configuration.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)

def setup_environment():
    """Set up environment variables"""
    print("\n🔧 Setting up environment...")
    
    env_file = Path(".env")
    if env_file.exists():
        print("⚠️  .env file already exists")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("Skipping environment setup")
            return
    
    print("\nPlease provide your Shopify app credentials:")
    print("(You can find these in your Shopify Partner Dashboard)")
    
    api_key = input("Shopify API Key: ").strip()
    api_secret = input("Shopify API Secret: ").strip()
    app_url = input("App URL (default: http://localhost:8000): ").strip() or "http://localhost:8000"
    
    env_content = f"""# Shopify App Configuration
SHOPIFY_API_KEY={api_key}
SHOPIFY_API_SECRET={api_secret}
APP_URL={app_url}

# For production, use your actual domain:
# APP_URL=https://yourdomain.com
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ Environment file created")

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = ["static", "templates"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Directories created")

def display_next_steps():
    """Display next steps for the user"""
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Create a Shopify app in your Partner Dashboard:")
    print("   - Go to https://partners.shopify.com/")
    print("   - Create a new app")
    print("   - Set App URL to: http://localhost:8000")
    print("   - Set Allowed redirection URL to: http://localhost:8000/auth/callback")
    print("   - Update your .env file with the actual API key and secret")
    print("\n2. Run the application:")
    print("   python main.py")
    print("\n3. Install the app on a development store:")
    print("   http://localhost:8000/install?shop=your-dev-store")
    print("\n4. Configure WhatsApp settings in the dashboard")
    print("\n📚 For more information, check the README.md file")

def main():
    """Main setup function"""
    print("🚀 Shopify WhatsApp Launcher App Setup")
    print("=" * 40)
    
    check_python_version()
    create_directories()
    install_dependencies()
    setup_environment()
    display_next_steps()

if __name__ == "__main__":
    main()