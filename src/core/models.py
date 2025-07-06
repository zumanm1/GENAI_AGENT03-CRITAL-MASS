"""
Core Data Models
SQLAlchemy models for the Network Automation AI Agent
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Table,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

Base = declarative_base()


# Association table for User and Role many-to-many relationship
user_roles = Table('user_roles', Base.metadata,
                   Column('user_id', Integer, ForeignKey('users.id')),
                   Column('role_id', Integer, ForeignKey('roles.id'))
                   )


class Role(Base):
    """Role model for RBAC"""
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    users = relationship('User', secondary=user_roles, back_populates='roles')

    def __repr__(self):
        return f"<Role(name='{self.name}')>"


class User(UserMixin, Base):
    """User model for authentication"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(64), index=True, unique=True, nullable=False)
    email = Column(String(120), index=True, unique=True, nullable=False)
    password_hash = Column(String(256))
    created_at = Column(DateTime, default=datetime.utcnow)
    roles = relationship('Role', secondary=user_roles, back_populates='users')

    @property
    def is_active(self):
        return True

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<User {self.username}>'

    def has_role(self, role_name):
        return any(role.name == role_name for role in self.roles)


class Device(Base):
    __tablename__ = 'devices'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    ip_address = Column(String(100), nullable=False)
    device_type = Column(String(50))
    os_version = Column(String(50))
    is_managed = Column(String(10), default='false')
    last_seen = Column(DateTime, default=datetime.utcnow)


class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)


class AuditResult(Base):
    __tablename__ = 'audit_results'
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('devices.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)
    result = Column(Text)
    device = relationship("Device")


class ChatMessage(Base):
    __tablename__ = 'chat_messages'
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255))
    message = Column(Text)
    is_from_user = Column(String(10))
    timestamp = Column(DateTime, default=datetime.utcnow)
    in_reply_to = Column(Integer)


class NetworkDevice(Base):
    __tablename__ = 'network_devices'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    device_type = Column(String, nullable=False, default='unknown')
    ip_address = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<NetworkDevice(name='{self.name}', ip='{self.ip_address}')>"


class NetworkLink(Base):
    __tablename__ = 'network_links'
    id = Column(Integer, primary_key=True)
    source_device_id = Column(Integer, ForeignKey(
        'network_devices.id'), nullable=False)
    target_device_id = Column(Integer, ForeignKey(
        'network_devices.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    source_device = relationship(
        'NetworkDevice', foreign_keys=[source_device_id])
    target_device = relationship(
        'NetworkDevice', foreign_keys=[target_device_id])

    def __repr__(self):
        return (
            f"<NetworkLink(source={self.source_device_id}, "
            f"target={self.target_device_id})>"
        )


# Pydantic models for API validation
class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class DeviceCreate(BaseModel):
    name: str
    ip_address: str
    device_type: Optional[str] = None


class DocumentCreate(BaseModel):
    filename: str
    content: str


class ChatMessageCreate(BaseModel):
    message: str
    stream: Optional[bool] = False


class AuditRequest(BaseModel):
    device_ids: List[int]


# Export all models
__all__ = [
    "Base", "User", "Role", "Device", "Document", "AuditResult", "ChatMessage",
    "NetworkDevice", "NetworkLink", "user_roles",
    "UserCreate", "UserResponse", "Token", "DeviceCreate", "DocumentCreate",
    "ChatMessageCreate", "AuditRequest",
]
