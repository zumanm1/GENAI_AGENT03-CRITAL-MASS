"""
Database Manager
Handles database connections and operations for the Network Automation AI Agent
"""

import logging
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from contextlib import contextmanager

from .models import Base, User, Device, Document, AuditResult, ChatMessage
from .config import config


class DatabaseManager:
    """Database manager for SQLAlchemy operations"""

    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.session = None
        self.logger = logging.getLogger(__name__)
        self._initialize_database()

    def _initialize_database(self):
        """Initialize database connection and create tables"""
        try:
            # Create database engine
            database_url = f"sqlite:///{config.database['SQLITE_DB']}"
            self.engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False},
                echo=config.is_development()
            )

            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            self.session = scoped_session(self.SessionLocal)

            # Create tables
            Base.metadata.create_all(bind=self.engine)

            self.logger.info("Database initialized successfully")

        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise

    @contextmanager
    def get_session(self):
        """Get database session with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def get_db(self) -> Session:
        """Get database session (for dependency injection)"""
        return self.SessionLocal()

    def get_user(
        self, user_id: int = None, username: str = None
    ) -> Optional[User]:
        """Get a user by their ID or username."""
        with self.get_session() as session:
            if user_id:
                return session.query(User).filter(User.id == user_id).first()
            if username:
                return (
                    session.query(User).filter(
                        User.username == username).first()
                )
            return None

    def get_device_count(self, status: str = None) -> int:
        """Get the total number of devices, optionally filtered by status."""
        with self.get_session() as session:
            if status:
                return (
                    session.query(Device).filter(
                        Device.status == status).count()
                )
            return session.query(Device).count()

    def get_document_count(self) -> int:
        """Get the total number of documents."""
        with self.get_session() as session:
            return session.query(Document).count()

    def get_last_audit_timestamp(self) -> Optional[str]:
        """Get the timestamp of the last audit."""
        with self.get_session() as session:
            latest_audit = session.query(AuditResult).order_by(
                AuditResult.timestamp.desc()).first()
            if latest_audit:
                return latest_audit.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            return None

    # Device operations
    def create_device(self, device_data: Dict[str, Any]) -> Device:
        """Create a new device"""
        with self.get_session() as session:
            device = Device(**device_data)
            session.add(device)
            session.flush()
            session.refresh(device)
            return device

    def get_device(self, device_id: int) -> Optional[Device]:
        """Get device by ID"""
        with self.get_session() as session:
            device = session.query(Device).filter(
                Device.id == device_id).first()
            return device

    def get_device_by_name(self, name: str) -> Optional[Device]:
        """Get device by name"""
        with self.get_session() as session:
            device = session.query(Device).filter(Device.name == name).first()
            return device

    def get_device_by_host(self, host: str) -> Optional[Device]:
        """Get device by host IP"""
        with self.get_session() as session:
            return session.query(Device).filter(Device.host == host).first()

    def get_all_devices(self) -> List[Device]:
        """Get all devices"""
        with self.get_session() as session:
            devices = session.query(Device).all()
            return devices

    def update_device(
        self, device_id: int, update_data: Dict[str, Any]
    ) -> Optional[Device]:
        """Update device"""
        with self.get_session() as session:
            device = session.query(Device).filter(
                Device.id == device_id).first()
            if device:
                for key, value in update_data.items():
                    if hasattr(device, key):
                        setattr(device, key, value)
                session.flush()
                session.refresh(device)
                return device
            return None

    def delete_device(self, device_id: int) -> bool:
        """Delete device"""
        with self.get_session() as session:
            device = session.query(Device).filter(
                Device.id == device_id).first()
            if device:
                session.delete(device)
                return True
            return False

    def get_devices_by_status(self, status: str) -> List[Device]:
        """Get devices by status"""
        with self.get_session() as session:
            return session.query(Device).filter(Device.status == status).all()

    # Document operations
    def create_document(self, document_data: Dict[str, Any]) -> Document:
        """Create a new document"""
        with self.get_session() as session:
            document = Document(**document_data)
            session.add(document)
            session.flush()
            session.refresh(document)
            return document

    def get_document(self, document_id: int) -> Optional[Document]:
        """Get document by ID"""
        with self.get_session() as session:
            return (
                session.query(Document).filter(
                    Document.id == document_id).first()
            )

    def get_all_documents(self) -> List[Document]:
        """Get all documents"""
        with self.get_session() as session:
            documents = session.query(Document).all()
            return documents

    def update_document(
        self, document_id: int, update_data: Dict[str, Any]
    ) -> Optional[Document]:
        """Update document"""
        with self.get_session() as session:
            document = session.query(Document).filter(
                Document.id == document_id).first()
            if document:
                for key, value in update_data.items():
                    if hasattr(document, key):
                        setattr(document, key, value)
                session.flush()
                session.refresh(document)
                return document
            return None

    def delete_document(self, document_id: int) -> bool:
        """Delete document"""
        with self.get_session() as session:
            document = session.query(Document).filter(
                Document.id == document_id).first()
            if document:
                session.delete(document)
                return True
            return False

    def get_documents_by_status(self, status: str) -> List[Document]:
        """Get documents by processing status"""
        with self.get_session() as session:
            return (
                session.query(Document).filter(Document.status == status).all()
            )

    # Audit result operations
    def create_audit_result(self, audit_data: Dict[str, Any]) -> AuditResult:
        """Create a new audit result"""
        with self.get_session() as session:
            audit_result = AuditResult(**audit_data)
            session.add(audit_result)
            session.flush()
            session.refresh(audit_result)
            return audit_result

    def get_audit_result(self, audit_id: int) -> Optional[AuditResult]:
        """Get audit result by ID"""
        with self.get_session() as session:
            return (
                session.query(AuditResult).filter(
                    AuditResult.id == audit_id).first()
            )

    def get_audit_results_by_device(
        self, device_name: str
    ) -> List[AuditResult]:
        """Get audit results for a device"""
        with self.get_session() as session:
            return session.query(AuditResult).filter(
                AuditResult.device_name == device_name).all()

    def get_audit_results_by_type(self, audit_type: str) -> List[AuditResult]:
        """Get audit results by type"""
        with self.get_session() as session:
            return session.query(AuditResult).filter(
                AuditResult.audit_type == audit_type
            ).all()

    def get_latest_audit_results(self, limit: int = 50) -> List[AuditResult]:
        """Get latest audit results"""
        with self.get_session() as session:
            results = session.query(AuditResult).order_by(
                AuditResult.executed_at.desc()).limit(limit).all()
            # Detach all results from session
            for result in results:
                session.expunge(result)
            return results

    # Chat message operations
    def create_chat_message(self, message_data: Dict[str, Any]) -> ChatMessage:
        """Create a new chat message"""
        with self.get_session() as session:
            message = ChatMessage(**message_data)
            session.add(message)
            session.flush()
            session.refresh(message)
            # Detach from session to avoid session issues
            session.expunge(message)
            return message

    def get_chat_messages(
        self, session_id: str, limit: int = 50
    ) -> List[ChatMessage]:
        """Get chat messages for a session"""
        with self.get_session() as session:
            return (
                session.query(ChatMessage)
                .filter(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at.desc())
                .limit(limit)
                .all()
            )

    def delete_chat_session(self, session_id: str) -> bool:
        """Delete all messages for a session"""
        with self.get_session() as session:
            messages = session.query(ChatMessage).filter(
                ChatMessage.session_id == session_id).all()
            if messages:
                for message in messages:
                    session.delete(message)
                return True
            return False

    # Utility operations
    def health_check(self) -> bool:
        """Check database health"""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            self.logger.error(f"Database health check failed: {e}")
            return False

    def get_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        with self.get_session() as session:
            stats = {
                "devices": session.query(Device).count(),
                "documents": session.query(Document).count(),
                "audit_results": session.query(AuditResult).count(),
                "chat_messages": session.query(ChatMessage).count(),
            }
            return stats

    def cleanup_old_data(self, days: int = 30) -> Dict[str, int]:
        """Clean up old data"""
        from datetime import datetime, timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)
        cleaned = {"audit_results": 0, "chat_messages": 0}

        with self.get_session() as session:
            # Clean old audit results
            old_audits = session.query(AuditResult).filter(
                AuditResult.executed_at < cutoff_date
            ).all()
            for audit in old_audits:
                session.delete(audit)
            cleaned["audit_results"] = len(old_audits)

            # Clean old chat messages (keep recent ones)
            old_messages = session.query(ChatMessage).filter(
                ChatMessage.created_at < cutoff_date
            ).all()
            for message in old_messages:
                session.delete(message)
            cleaned["chat_messages"] = len(old_messages)

            self.logger.info(f"Cleaned up old data: {cleaned}")
            return cleaned

    def backup_database(self) -> str:
        """Create database backup"""
        import shutil
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{config.database['SQLITE_DB']}.backup_{timestamp}"

        try:
            shutil.copy2(config.database['SQLITE_DB'], backup_path)
            self.logger.info(f"Database backup created: {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"Database backup failed: {e}")
            raise


# Global database manager instance
db_manager = DatabaseManager()


# Dependency for FastAPI/Flask
def get_database() -> DatabaseManager:
    """Get database manager instance"""
    return db_manager
