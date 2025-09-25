"""
Database models and operations for the Shopify WhatsApp Launcher app.
- For dev: uses JSON file storage
- For prod: uses PostgreSQL (Supabase) with SQLAlchemy
"""

import os
import json
from typing import Dict, Optional
from datetime import datetime

# SQLAlchemy imports
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

# ---------------------------
# File-based DB (SimpleFileDB)
# ---------------------------
class SimpleFileDB:
    def __init__(self, db_file: str = None):
        if db_file is None:
            data_dir = os.getenv("DATA_DIR", "/app/data")
            os.makedirs(data_dir, exist_ok=True)
            self.db_file = os.path.join(data_dir, "app_data.json")
        else:
            self.db_file = db_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        return {"installations": {}, "whatsapp_configs": {}, "analytics": {}}
    
    def _save_data(self):
        try:
            with open(self.db_file, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def save_installation(self, shop: str, access_token: str):
        self.data["installations"][shop] = {
            "access_token": access_token,
            "shop": shop,
            "installed_at": datetime.now().isoformat()
        }
        self._save_data()
    
    def get_installation(self, shop: str) -> Optional[Dict]:
        return self.data["installations"].get(shop)
    
    def remove_installation(self, shop: str):
        self.data["installations"].pop(shop, None)
        self.data["whatsapp_configs"].pop(shop, None)
        self.data["analytics"].pop(shop, None)
        self._save_data()
    
    def save_whatsapp_config(self, shop: str, phone_number: str, initial_message: str):
        self.data["whatsapp_configs"][shop] = {
            "phone_number": phone_number,
            "initial_message": initial_message,
            "updated_at": datetime.now().isoformat()
        }
        self._save_data()
    
    def get_whatsapp_config(self, shop: str) -> Optional[Dict]:
        return self.data["whatsapp_configs"].get(shop)
    
    def log_widget_click(self, shop: str):
        if shop not in self.data["analytics"]:
            self.data["analytics"][shop] = {"widget_clicks": 0, "first_click": None, "last_click": None}
        self.data["analytics"][shop]["widget_clicks"] += 1
        now = datetime.now().isoformat()
        if not self.data["analytics"][shop]["first_click"]:
            self.data["analytics"][shop]["first_click"] = now
        self.data["analytics"][shop]["last_click"] = now
        self._save_data()
    
    def get_analytics(self, shop: str) -> Optional[Dict]:
        return self.data["analytics"].get(shop, {"widget_clicks": 0, "first_click": None, "last_click": None})
    
    def get_all_installations(self) -> Dict:
        return self.data["installations"]


# ---------------------------
# SQLAlchemy DB (Postgres/Supabase)
# ---------------------------
Base = declarative_base()

class Installation(Base):
    __tablename__ = "installations"
    shop = Column(String, primary_key=True)
    access_token = Column(Text, nullable=False)
    installed_at = Column(DateTime, default=datetime.utcnow)

class WhatsAppConfig(Base):
    __tablename__ = "whatsapp_configs"
    shop = Column(String, primary_key=True)
    phone_number = Column(String, nullable=False)
    initial_message = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Analytics(Base):
    __tablename__ = "analytics"
    shop = Column(String, primary_key=True)
    widget_clicks = Column(Integer, default=0)
    first_click = Column(DateTime, nullable=True)
    last_click = Column(DateTime, nullable=True)


class SQLAlchemyDB:
    def __init__(self):
        db_url = os.getenv("DATABASE_URL")  # Supabase/Postgres connection string
        self.engine = create_engine(db_url, pool_pre_ping=True)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    @contextmanager
    def session(self):
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def save_installation(self, shop: str, access_token: str):
        with self.session() as db:
            obj = db.get(Installation, shop)
            if obj:
                obj.access_token = access_token
                obj.installed_at = datetime.utcnow()
            else:
                db.add(Installation(shop=shop, access_token=access_token))
    
    def get_installation(self, shop: str) -> Optional[Dict]:
        with self.session() as db:
            obj = db.get(Installation, shop)
            if obj:
                return {"shop": obj.shop, "access_token": obj.access_token, "installed_at": obj.installed_at.isoformat()}
        return None

    def remove_installation(self, shop: str):
        with self.session() as db:
            db.query(Installation).filter_by(shop=shop).delete()
            db.query(WhatsAppConfig).filter_by(shop=shop).delete()
            db.query(Analytics).filter_by(shop=shop).delete()
    
    def save_whatsapp_config(self, shop: str, phone_number: str, initial_message: str):
        with self.session() as db:
            obj = db.get(WhatsAppConfig, shop)
            if obj:
                obj.phone_number = phone_number
                obj.initial_message = initial_message
                obj.updated_at = datetime.utcnow()
            else:
                db.add(WhatsAppConfig(shop=shop, phone_number=phone_number, initial_message=initial_message))
    
    def get_whatsapp_config(self, shop: str) -> Optional[Dict]:
        with self.session() as db:
            obj = db.get(WhatsAppConfig, shop)
            if obj:
                return {"phone_number": obj.phone_number, "initial_message": obj.initial_message, "updated_at": obj.updated_at.isoformat()}
        return None

    def log_widget_click(self, shop: str):
        now = datetime.utcnow()
        with self.session() as db:
            obj = db.get(Analytics, shop)
            if obj:
                obj.widget_clicks += 1
                obj.last_click = now
                if not obj.first_click:
                    obj.first_click = now
            else:
                db.add(Analytics(shop=shop, widget_clicks=1, first_click=now, last_click=now))
    
    def get_analytics(self, shop: str) -> Optional[Dict]:
        with self.session() as db:
            obj = db.get(Analytics, shop)
            if obj:
                return {"widget_clicks": obj.widget_clicks, "first_click": obj.first_click.isoformat() if obj.first_click else None, "last_click": obj.last_click.isoformat() if obj.last_click else None}
        return {"widget_clicks": 0, "first_click": None, "last_click": None}

    def get_all_installations(self) -> Dict:
        with self.session() as db:
            objs = db.query(Installation).all()
            return {o.shop: {"shop": o.shop, "access_token": o.access_token, "installed_at": o.installed_at.isoformat()} for o in objs}


# ---------------------------
# Choose DB backend globally
# ---------------------------
if os.getenv("DB_BACKEND", "file") == "postgres":
    db = SQLAlchemyDB()
else:
    db = SimpleFileDB()
