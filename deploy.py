#!/usr/bin/env python3
"""
Deployment helper script for Shopify WhatsApp Launcher
This script helps prepare the app for deployment to Render.com
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def check_files():
    """Check if all required files exist"""
    required_files = [
        'main.py',
        'requirements.txt',
        'render.yaml',
        'runtime.txt',
        'database.py',
        'templates/embedded_dashboard.html',
        'templates/dashboard.html',
        'templates/install_embedded.html'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files present")
    return True

def check_environment():
    """Check environment configuration"""
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  .env file not found")
        return False
    
    with open('.env', 'r') as f:
        content = f.read()
    
    if 'your_shopify_api_key_here' in content:
        print("⚠️  Please update your Shopify API credentials in .env file")
        return False
    
    print("✅ Environment configuration looks good")
    return True

def check_git():
    """Check if git repository is initialized"""
    if not Path('.git').exists():
        print("⚠️  Git repository not initialized")
        print("   Run: git init")
        return False
    
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            print("⚠️  You have uncommitted changes")
            print("   Run: git add . && git commit -m 'Prepare for deployment'")
            return False
    except FileNotFoundError:
        print("⚠️  Git not found in PATH")
        return False
    
    print("✅ Git repository is ready")
    return True

def generate_render_config():
    """Generate render.yaml with current settings"""
    config = {
        'services': [{
            'type': 'web',
            'name': 'shopify-whatsapp-launcher',
            'env': 'python',
            'buildCommand': 'pip install -r requirements.txt',
            'startCommand': 'python main.py',
            'envVars': [
                {'key': 'SHOPIFY_API_KEY', 'sync': False},
                {'key': 'SHOPIFY_API_SECRET', 'sync': False},
                {'key': 'APP_URL', 'value': 'https://shopify-whatsapp-launcher.onrender.com'},
                {'key': 'PORT', 'value': '8000'}
            ],
            'healthCheckPath': '/health',
            'disk': {
                'name': 'app-data',
                'mountPath': '/app/data',
                'sizeGB': 1
            }
        }]
    }
    
    # Convert to YAML format (simple conversion)
    yaml_content = """services:
  - type: web
    name: shopify-whatsapp-launcher
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py
    envVars:
      - key: SHOPIFY_API_KEY
        sync: false
      - key: SHOPIFY_API_SECRET
        sync: false
      - key: APP_URL
        value: https://shopify-whatsapp-launcher.onrender.com
      - key: PORT
        value: 8000
    healthCheckPath: /health
    disk:
      name: app-data
      mountPath: /app/data
      sizeGB: 1"""
    
    with open('render.yaml', 'w') as f:
        f.write(yaml_content)
    
    print("✅ render.yaml updated")

def display_next_steps():
    """Display deployment instructions"""
    print("\n🚀 Ready for Render.com Deployment!")
    print("=" * 50)
    print("\n📋 Next Steps:")
    print("1. Push your code to GitHub:")
    print("   git add .")
    print("   git commit -m 'Prepare for deployment'")
    print("   git push origin main")
    print("\n2. Go to render.com and create a new Blueprint")
    print("3. Connect your GitHub repository")
    print("4. Set environment variables in Render dashboard:")
    print("   - SHOPIFY_API_KEY")
    print("   - SHOPIFY_API_SECRET")
    print("   - APP_URL (will be provided by Render)")
    print("\n5. Update your Shopify app settings with the new URLs")
    print("\n📚 For detailed instructions, see DEPLOYMENT.md")

def main():
    """Main deployment preparation function"""
    print("🔧 Shopify WhatsApp Launcher - Deployment Preparation")
    print("=" * 55)
    
    # Check all requirements
    checks_passed = True
    
    if not check_files():
        checks_passed = False
    
    if not check_environment():
        checks_passed = False
    
    if not check_git():
        checks_passed = False
    
    if not checks_passed:
        print("\n❌ Please fix the issues above before deploying")
        sys.exit(1)
    
    # Generate/update configuration
    generate_render_config()
    
    # Show next steps
    display_next_steps()

if __name__ == "__main__":
    main()