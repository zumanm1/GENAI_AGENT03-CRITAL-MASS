"""
Application Configuration
Main configuration file for the Network Automation AI Agent
"""

import os
from pathlib import Path

# Base Configuration
BASE_DIR = Path(__file__).parent.parent
SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = DATA_DIR / "logs"
DB_DIR = DATA_DIR / "db"
DOCUMENTS_DIR = DATA_DIR / "documents"

# Flask Configuration
FLASK_CONFIG = {
    "SECRET_KEY": os.environ.get(
        "SECRET_KEY", "dev-secret-key-change-in-production"
    ),
    "DEBUG": os.environ.get("FLASK_DEBUG", "True").lower() == "true",
    "HOST": os.environ.get("FLASK_HOST", "0.0.0.0"),
    "PORT": int(os.environ.get("FLASK_PORT", 5003)),
    "THREADED": True,
}

# Ollama Configuration
OLLAMA_CONFIG = {
    "BASE_URL": os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
    "MODEL_NAME": os.environ.get("OLLAMA_MODEL", "llama3.2:1b"),
    "TEMPERATURE": float(os.environ.get("OLLAMA_TEMPERATURE", 0.7)),
    "MAX_TOKENS": int(os.environ.get("OLLAMA_MAX_TOKENS", 2048)),
    "TIMEOUT": int(os.environ.get("OLLAMA_TIMEOUT", 60)),
}

# ChromaDB Configuration
CHROMADB_CONFIG = {
    "PERSIST_DIRECTORY": str(DB_DIR / "chroma"),
    "COLLECTION_NAME": "network_docs",
    "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2",
    "CHUNK_SIZE": 1000,
    "CHUNK_OVERLAP": 200,
}

# Network Configuration
NETWORK_CONFIG = {
    "IP_RANGE": "172.16.39.107-120",
    "SSH_USERNAME": os.environ.get("SSH_USERNAME", "cisco"),
    "SSH_PASSWORD": os.environ.get("SSH_PASSWORD", "cisco"),
    "DEVICE_TYPE": "cisco_ios",
    "SSH_TIMEOUT": 30,
    "SSH_PORT": 22,
    "ENABLE_PASSWORD": os.environ.get("ENABLE_PASSWORD", "cisco"),
    "DISCOVERY_TIMEOUT": 5,
    "CONCURRENT_CONNECTIONS": 10,
}

# RAG Configuration
RAG_CONFIG = {
    "CHUNK_SIZE": 1000,
    "CHUNK_OVERLAP": 200,
    "SIMILARITY_THRESHOLD": 0.7,
    "MAX_RESULTS": 5,
    "EMBEDDING_DIMENSION": 384,
}

# CrewAI Configuration
CREWAI_CONFIG = {
    "VERBOSE": True,
    "MEMORY": True,
    "MAX_ITER": 10,
    "MAX_EXECUTION_TIME": 300,  # 5 minutes
}

# Logging Configuration
LOGGING_CONFIG = {
    "VERSION": 1,
    "DISABLE_EXISTING_LOGGERS": False,
    "FORMATTERS": {
        "default": {
            "FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "DATEFMT": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "FORMAT": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - "
            "%(funcName)s - %(message)s",
            "DATEFMT": "%Y-%m-%d %H:%M:%S",
        },
    },
    "HANDLERS": {
        "console": {
            "CLASS": "logging.StreamHandler",
            "LEVEL": "INFO",
            "FORMATTER": "default",
            "STREAM": "ext://sys.stdout",
        },
        "file": {
            "CLASS": "logging.FileHandler",
            "LEVEL": "DEBUG",
            "FORMATTER": "detailed",
            "FILENAME": str(LOGS_DIR / "app.log"),
            "MODE": "a",
        },
    },
    "LOGGERS": {
        "": {
            "LEVEL": "DEBUG",
            "HANDLERS": ["console", "file"],
        },
        "netmiko": {
            "LEVEL": "WARNING",
            "HANDLERS": ["file"],
        },
        "paramiko": {
            "LEVEL": "WARNING",
            "HANDLERS": ["file"],
        },
    },
}

# File Upload Configuration
UPLOAD_CONFIG = {
    "MAX_FILE_SIZE": 16 * 1024 * 1024,  # 16MB
    "ALLOWED_EXTENSIONS": {
        "pdf", "txt", "docx", "xlsx", "xls", "csv"
    },
    "UPLOAD_FOLDER": str(DOCUMENTS_DIR),
}

# Database Configuration
DATABASE_CONFIG = {
    "SQLITE_DB": str(DB_DIR / "network_automation.db"),
    "BACKUP_INTERVAL": 3600,  # 1 hour
    "MAX_BACKUPS": 10,
}

# Security Configuration
SECURITY_CONFIG = {
    "CSRF_ENABLED": True,
    "CSRF_SESSION_KEY": os.environ.get("CSRF_SESSION_KEY", "csrf-secret-key"),
    "WTF_CSRF_TIME_LIMIT": 3600,  # 1 hour
    "SESSION_COOKIE_SECURE": False,  # Set to True in production with HTTPS
    "SESSION_COOKIE_HTTPONLY": True,
    "SESSION_COOKIE_SAMESITE": "Lax",
}

# API Configuration
API_CONFIG = {
    "RATE_LIMIT": "100 per hour",
    "CORS_ORIGINS": ["http://localhost:3000", "http://localhost:5003"],
    "API_VERSION": "v1",
}

# Agent Configuration
AGENT_CONFIG = {
    "NETWORK_ENGINEER": {
        "ROLE": "Senior Network Engineer",
        "GOAL": "Analyze network configurations and provide expert recommendations",
        "BACKSTORY": "Expert in network design, configuration, and troubleshooting with "
        "15+ years experience",
    },
    "TROUBLESHOOTER": {
        "ROLE": "Network Troubleshooting Specialist",
        "GOAL": "Diagnose network issues and provide step-by-step solutions",
        "BACKSTORY": "Specialized in network problem diagnosis and resolution with "
        "deep protocol knowledge",
    },
    "CONFIG_MANAGER": {
        "ROLE": "Configuration Management Specialist",
        "GOAL": "Generate, validate, and deploy network configurations safely",
        "BACKSTORY": "Expert in configuration management, change control, and automation",
    },
    "AUDIT_AGENT": {
        "ROLE": "Network Audit Specialist",
        "GOAL": "Perform comprehensive network audits and compliance checks",
        "BACKSTORY": "Specialized in network security, compliance, and performance analysis",
    },
}

# Development Configuration
DEV_CONFIG = {
    "AUTO_RELOAD": True,
    "TESTING": False,
    "MOCK_DEVICES": False,  # Set to True for development without real devices
    "DEMO_MODE": False,
}

# Create directories if they don't exist
def create_directories():
    """Create necessary directories for the application"""
    directories = [
        DATA_DIR,
        LOGS_DIR,
        DB_DIR,
        DOCUMENTS_DIR,
        CHROMADB_CONFIG["PERSIST_DIRECTORY"],
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

# Initialize directories on import
create_directories()

# Export main configuration
__all__ = [
    "FLASK_CONFIG",
    "OLLAMA_CONFIG",
    "CHROMADB_CONFIG",
    "NETWORK_CONFIG",
    "RAG_CONFIG",
    "CREWAI_CONFIG",
    "LOGGING_CONFIG",
    "UPLOAD_CONFIG",
    "DATABASE_CONFIG",
    "SECURITY_CONFIG",
    "API_CONFIG",
    "AGENT_CONFIG",
    "DEV_CONFIG",
    "BASE_DIR",
    "SRC_DIR",
    "DATA_DIR",
    "LOGS_DIR",
    "DB_DIR",
    "DOCUMENTS_DIR",
]
