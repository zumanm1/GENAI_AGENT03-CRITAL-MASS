"""
Core Data Models
SQLAlchemy models for the Network Automation AI Agent
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
import json

Base = declarative_base()


class Device(Base):
    """Network device model"""
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    host = Column(String(15), nullable=False)  # IP address
    device_type = Column(String(50), nullable=False)  # cisco_ios, etc.
    role = Column(String(50))  # PE Router, CE Router, etc.
    as_number = Column(Integer)  # BGP AS number
    
    # Connection details
    username = Column(String(50))
    password = Column(String(100))
    secret = Column(String(100))  # Enable password
    port = Column(Integer, default=22)
    
    # Status and metadata
    status = Column(String(20), default="unknown")  # up, down, unknown
    last_seen = Column(DateTime)
    last_backup = Column(DateTime)
    
    # Device information
    vendor = Column(String(50))
    model = Column(String(50))
    version = Column(String(50))
    serial_number = Column(String(50))
    
    # Configuration
    configuration = Column(Text)  # Current configuration
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Device(name='{self.name}', host='{self.host}', status='{self.status}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert device to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "host": self.host,
            "device_type": self.device_type,
            "role": self.role,
            "as_number": self.as_number,
            "status": self.status,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "vendor": self.vendor,
            "model": self.model,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class Document(Base):
    """Document model for uploaded files"""
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, txt, xlsx, etc.
    file_size = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    
    # Processing status
    status = Column(String(50), default="uploaded")  # uploaded, processing, processed, error
    processing_error = Column(Text)
    
    # Content metadata
    content_type = Column(String(100))  # network_config, documentation, etc.
    extracted_text = Column(Text)
    chunk_count = Column(Integer, default=0)
    
    # Vector storage
    vector_ids = Column(JSON)  # ChromaDB vector IDs
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    
    def __repr__(self):
        return f"<Document(filename='{self.filename}', status='{self.status}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary"""
        return {
            "id": self.id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "status": self.status,
            "content_type": self.content_type,
            "chunk_count": self.chunk_count,
            "uploaded_at": self.uploaded_at.isoformat(),
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
        }


class AuditResult(Base):
    """Network audit result model"""
    __tablename__ = "audit_results"
    
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, nullable=False)
    device_name = Column(String(50), nullable=False)
    
    # Audit details
    audit_type = Column(String(50), nullable=False)  # ospf, bgp, interface, ping
    audit_category = Column(String(50))  # connectivity, configuration, performance
    
    # Results
    status = Column(String(20), nullable=False)  # pass, fail, warning, error
    summary = Column(String(500))
    details = Column(JSON)  # Detailed results
    
    # Metrics
    response_time = Column(Float)  # For ping tests
    neighbor_count = Column(Integer)  # For OSPF/BGP
    
    # Issues and recommendations
    issues_found = Column(JSON)  # List of issues
    recommendations = Column(JSON)  # List of recommendations
    
    # Timestamps
    executed_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AuditResult(device='{self.device_name}', type='{self.audit_type}', status='{self.status}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit result to dictionary"""
        return {
            "id": self.id,
            "device_id": self.device_id,
            "device_name": self.device_name,
            "audit_type": self.audit_type,
            "audit_category": self.audit_category,
            "status": self.status,
            "summary": self.summary,
            "details": self.details,
            "response_time": self.response_time,
            "neighbor_count": self.neighbor_count,
            "issues_found": self.issues_found,
            "recommendations": self.recommendations,
            "executed_at": self.executed_at.isoformat(),
        }


class ChatMessage(Base):
    """Chat message model"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), nullable=False)
    
    # Message details
    message_type = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    
    # Agent information
    agent_name = Column(String(50))  # Which agent responded
    agent_role = Column(String(100))
    
    # Context and metadata
    context_used = Column(JSON)  # RAG context used
    tools_used = Column(JSON)  # Tools/functions used
    execution_time = Column(Float)  # Response time
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ChatMessage(type='{self.message_type}', session='{self.session_id}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chat message to dictionary"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "message_type": self.message_type,
            "content": self.content,
            "agent_name": self.agent_name,
            "agent_role": self.agent_role,
            "context_used": self.context_used,
            "tools_used": self.tools_used,
            "execution_time": self.execution_time,
            "created_at": self.created_at.isoformat(),
        }


# Pydantic models for API validation
class DeviceCreate(BaseModel):
    """Pydantic model for creating devices"""
    name: str = Field(..., min_length=1, max_length=50)
    host: str = Field(..., min_length=7, max_length=15)  # IP address
    device_type: str = Field(..., min_length=1, max_length=50)
    role: Optional[str] = Field(None, max_length=50)
    as_number: Optional[int] = Field(None, ge=1, le=65535)
    username: Optional[str] = Field(None, max_length=50)
    password: Optional[str] = Field(None, max_length=100)
    secret: Optional[str] = Field(None, max_length=100)
    port: int = Field(22, ge=1, le=65535)


class DeviceUpdate(BaseModel):
    """Pydantic model for updating devices"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    role: Optional[str] = Field(None, max_length=50)
    as_number: Optional[int] = Field(None, ge=1, le=65535)
    status: Optional[str] = Field(None, max_length=20)
    vendor: Optional[str] = Field(None, max_length=50)
    model: Optional[str] = Field(None, max_length=50)
    version: Optional[str] = Field(None, max_length=50)
    serial_number: Optional[str] = Field(None, max_length=50)


class ChatMessageCreate(BaseModel):
    """Pydantic model for creating chat messages"""
    session_id: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)
    message_type: str = Field("user", pattern="^(user|assistant|system)$")


class AuditRequest(BaseModel):
    """Pydantic model for audit requests"""
    device_names: List[str] = Field(..., min_items=1)
    audit_types: List[str] = Field(..., min_items=1)
    include_recommendations: bool = Field(True)


# Export all models
__all__ = [
    "Base",
    "Device",
    "Document", 
    "AuditResult",
    "ChatMessage",
    "DeviceCreate",
    "DeviceUpdate",
    "ChatMessageCreate",
    "AuditRequest",
] 