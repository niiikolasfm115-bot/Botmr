from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    ff_uid = Column(String, unique=True, index=True)
    username = Column(String)
    telegram_id = Column(String, unique=True, index=True)
    is_admin = Column(Boolean, default=False)
    is_whitelisted = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used = Column(DateTime(timezone=True), onupdate=func.now())

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    ff_uid = Column(String, unique=True, index=True)
    ff_username = Column(String)
    ff_password = Column(String)
    region = Column(String, default="PK")
    is_active = Column(Boolean, default=True)
    is_banned = Column(Boolean, default=False)
    access_token = Column(Text)
    jwt_token = Column(Text)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class CommandLog(Base):
    __tablename__ = "command_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    command = Column(String)
    target_uid = Column(String)
    status = Column(String)  # success, failed, error
    details = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SessionLog(Base):
    __tablename__ = "session_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String)
    status = Column(String)  # connected, disconnected, error
    details = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    duration = Column(Float)  # in seconds

class BanHistory(Base):
    __tablename__ = "ban_history"
    
    id = Column(Integer, primary_key=True, index=True)
    ff_uid = Column(String, index=True)
    reason = Column(String)
    ban_date = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text)
