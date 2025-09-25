"""
Database models and operations for the Shopify WhatsApp Launcher app.
This is a simple file-based database for development. 
For production, replace with PostgreSQL, MySQL, or MongoDB.
"""

import json
import os
from typing import Dict, Optional
from datetime import datetime

class SimpleFileDB:
    def __init__(self, db_file: str = None):
        if db_file is None:
            # Use data directory for persistent storage on Render
            data_dir = os.getenv("DATA_DIR", "/app/data")
            if not os.path.exists(data_dir):
                os.makedirs(data_dir, exist_ok=True)
            self.db_file = os.path.join(data_dir, "app_data.json")
        else:
            self.db_file = db_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load data from JSON file"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        return {
            "installations": {},
            "whatsapp_configs": {},
            "analytics": {}
        }
    
    def _save_data(self):
        """Save data to JSON file"""
        try:
            with open(self.db_file, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def save_installation(self, shop: str, access_token: str):
        """Save app installation data"""
        self.data["installations"][shop] = {
            "access_token": access_token,
            "shop": shop,
            "installed_at": datetime.now().isoformat()
        }
        self._save_data()
    
    def get_installation(self, shop: str) -> Optional[Dict]:
        """Get installation data for a shop"""
        return self.data["installations"].get(shop)
    
    def remove_installation(self, shop: str):
        """Remove installation data"""
        if shop in self.data["installations"]:
            del self.data["installations"][shop]
        if shop in self.data["whatsapp_configs"]:
            del self.data["whatsapp_configs"][shop]
        self._save_data()
    
    def save_whatsapp_config(self, shop: str, phone_number: str, initial_message: str):
        """Save WhatsApp configuration"""
        self.data["whatsapp_configs"][shop] = {
            "phone_number": phone_number,
            "initial_message": initial_message,
            "updated_at": datetime.now().isoformat()
        }
        self._save_data()
    
    def get_whatsapp_config(self, shop: str) -> Optional[Dict]:
        """Get WhatsApp configuration for a shop"""
        return self.data["whatsapp_configs"].get(shop)
    
    def log_widget_click(self, shop: str):
        """Log widget click for analytics"""
        if shop not in self.data["analytics"]:
            self.data["analytics"][shop] = {
                "widget_clicks": 0,
                "first_click": None,
                "last_click": None
            }
        
        self.data["analytics"][shop]["widget_clicks"] += 1
        now = datetime.now().isoformat()
        
        if not self.data["analytics"][shop]["first_click"]:
            self.data["analytics"][shop]["first_click"] = now
        
        self.data["analytics"][shop]["last_click"] = now
        self._save_data()
    
    def get_analytics(self, shop: str) -> Optional[Dict]:
        """Get analytics data for a shop"""
        return self.data["analytics"].get(shop, {
            "widget_clicks": 0,
            "first_click": None,
            "last_click": None
        })
    
    def get_all_installations(self) -> Dict:
        """Get all installations"""
        return self.data["installations"]

# Global database instance
db = SimpleFileDB()