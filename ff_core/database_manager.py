from typing import Optional, List
from sqlalchemy.orm import Session
from database.models import User, Account, CommandLog, BanHistory
from logger_config import logger
from datetime import datetime

class DatabaseManager:
    """Manages database operations"""
    
    @staticmethod
    def add_user(db: Session, ff_uid: str, username: str, telegram_id: str, is_admin: bool = False) -> Optional[User]:
        """Add new user"""
        try:
            # Check if user exists
            user = db.query(User).filter(User.ff_uid == ff_uid).first()
            if user:
                return user
            
            user = User(
                ff_uid=ff_uid,
                username=username,
                telegram_id=telegram_id,
                is_admin=is_admin
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"✅ User added: {username} ({ff_uid})")
            return user
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def add_account(db: Session, ff_uid: str, ff_username: str, ff_password: str, 
                    region: str = "PK", access_token: str = "", jwt_token: str = "") -> Optional[Account]:
        """Add Free Fire account"""
        try:
            # Check if account exists
            account = db.query(Account).filter(Account.ff_uid == ff_uid).first()
            if account:
                account.ff_password = ff_password
                account.access_token = access_token
                account.jwt_token = jwt_token
                db.commit()
                return account
            
            account = Account(
                ff_uid=ff_uid,
                ff_username=ff_username,
                ff_password=ff_password,
                region=region,
                access_token=access_token,
                jwt_token=jwt_token,
                last_login=datetime.utcnow()
            )
            db.add(account)
            db.commit()
            db.refresh(account)
            logger.info(f"✅ Account added: {ff_username} ({ff_uid})")
            return account
        except Exception as e:
            logger.error(f"Error adding account: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def log_command(db: Session, user_id: str, command: str, target_uid: str = None,
                    status: str = "success", details: dict = None) -> Optional[CommandLog]:
        """Log command execution"""
        try:
            log = CommandLog(
                user_id=user_id,
                command=command,
                target_uid=target_uid,
                status=status,
                details=details or {}
            )
            db.add(log)
            db.commit()
            db.refresh(log)
            return log
        except Exception as e:
            logger.error(f"Error logging command: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def log_ban(db: Session, ff_uid: str, reason: str = "Unknown", notes: str = ""):
        """Log account ban"""
        try:
            ban = BanHistory(
                ff_uid=ff_uid,
                reason=reason,
                notes=notes
            )
            db.add(ban)
            
            # Mark account as banned
            account = db.query(Account).filter(Account.ff_uid == ff_uid).first()
            if account:
                account.is_banned = True
            
            db.commit()
            logger.warning(f"⚠️ Ban logged for {ff_uid}: {reason}")
            return ban
        except Exception as e:
            logger.error(f"Error logging ban: {e}")
            db.rollback()
            return None
    
    @staticmethod
    def get_active_accounts(db: Session, limit: int = 10) -> List[Account]:
        """Get active accounts"""
        try:
            accounts = db.query(Account).filter(
                Account.is_active == True,
                Account.is_banned == False
            ).limit(limit).all()
            return accounts
        except Exception as e:
            logger.error(f"Error getting accounts: {e}")
            return []
    
    @staticmethod
    def get_command_logs(db: Session, user_id: str = None, limit: int = 50):
        """Get command logs"""
        try:
            query = db.query(CommandLog)
            if user_id:
                query = query.filter(CommandLog.user_id == user_id)
            
            logs = query.order_by(CommandLog.created_at.desc()).limit(limit).all()
            return logs
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return []
    
    @staticmethod
    def is_user_banned(db: Session, ff_uid: str) -> bool:
        """Check if user is banned"""
        try:
            ban = db.query(BanHistory).filter(BanHistory.ff_uid == ff_uid).first()
            return ban is not None
        except Exception as e:
            logger.error(f"Error checking ban status: {e}")
            return False
    
    @staticmethod
    def is_user_admin(db: Session, ff_uid: str) -> bool:
        """Check if user is admin"""
        try:
            user = db.query(User).filter(User.ff_uid == ff_uid).first()
            return user and user.is_admin
        except Exception as e:
            logger.error(f"Error checking admin status: {e}")
            return False
