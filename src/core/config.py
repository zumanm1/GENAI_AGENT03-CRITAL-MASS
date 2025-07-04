"""
Core Configuration Manager
Centralized configuration management for the Network Automation AI Agent
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any

# Add config directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "config"))

try:
    from app_config import *
except ImportError as e:
    print(f"Error importing configuration: {e}")
    sys.exit(1)


class AppConfig:
    """Centralized application configuration manager"""
    
    def __init__(self):
        self.flask = FLASK_CONFIG
        self.ollama = OLLAMA_CONFIG
        self.chromadb = CHROMADB_CONFIG
        self.network = NETWORK_CONFIG
        self.rag = RAG_CONFIG
        self.crewai = CREWAI_CONFIG
        self.logging = LOGGING_CONFIG
        self.upload = UPLOAD_CONFIG
        self.database = DATABASE_CONFIG
        self.security = SECURITY_CONFIG
        self.api = API_CONFIG
        self.agents = AGENT_CONFIG
        self.dev = DEV_CONFIG
        
        # Directory paths
        self.base_dir = BASE_DIR
        self.src_dir = SRC_DIR
        self.data_dir = DATA_DIR
        self.logs_dir = LOGS_DIR
        self.db_dir = DB_DIR
        self.documents_dir = DOCUMENTS_DIR
        
        # Initialize logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup application logging"""
        try:
            logging.basicConfig(
                level=logging.INFO,
                format=self.logging["FORMATTERS"]["default"]["FORMAT"],
                datefmt=self.logging["FORMATTERS"]["default"]["DATEFMT"]
            )
            
            # Create file handler
            file_handler = logging.FileHandler(
                self.logging["HANDLERS"]["file"]["FILENAME"]
            )
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                self.logging["FORMATTERS"]["detailed"]["FORMAT"],
                self.logging["FORMATTERS"]["detailed"]["DATEFMT"]
            )
            file_handler.setFormatter(file_formatter)
            
            # Add to root logger
            root_logger = logging.getLogger()
            root_logger.addHandler(file_handler)
            
            logging.info("Logging initialized successfully")
            
        except Exception as e:
            print(f"Error setting up logging: {e}")
    
    def get_network_devices(self) -> Dict[str, Dict[str, Any]]:
        """Get predefined network device configurations"""
        return {
            "R15": {
                "host": "172.16.39.115",
                "device_type": "cisco_ios",
                "username": self.network["SSH_USERNAME"],
                "password": self.network["SSH_PASSWORD"],
                "secret": self.network["ENABLE_PASSWORD"],
                "role": "PE Router",
                "as_number": 2222,
            },
            "R16": {
                "host": "172.16.39.116", 
                "device_type": "cisco_ios",
                "username": self.network["SSH_USERNAME"],
                "password": self.network["SSH_PASSWORD"],
                "secret": self.network["ENABLE_PASSWORD"],
                "role": "PE Router",
                "as_number": 2222,
            },
            "R17": {
                "host": "172.16.39.117",
                "device_type": "cisco_ios", 
                "username": self.network["SSH_USERNAME"],
                "password": self.network["SSH_PASSWORD"],
                "secret": self.network["ENABLE_PASSWORD"],
                "role": "P Router",
                "as_number": 2222,
            },
            "R18": {
                "host": "172.16.39.118",
                "device_type": "cisco_ios",
                "username": self.network["SSH_USERNAME"],
                "password": self.network["SSH_PASSWORD"],
                "secret": self.network["ENABLE_PASSWORD"],
                "role": "RR Router", 
                "as_number": 2222,
            },
            "R19": {
                "host": "172.16.39.119",
                "device_type": "cisco_ios",
                "username": self.network["SSH_USERNAME"],
                "password": self.network["SSH_PASSWORD"],
                "secret": self.network["ENABLE_PASSWORD"],
                "role": "CE Router",
                "as_number": 100,
            },
            "R20": {
                "host": "172.16.39.120",
                "device_type": "cisco_ios",
                "username": self.network["SSH_USERNAME"],
                "password": self.network["SSH_PASSWORD"],
                "secret": self.network["ENABLE_PASSWORD"],
                "role": "CE Router",
                "as_number": 13,
            },
        }
    
    def get_ip_range(self) -> list:
        """Parse IP range and return list of IP addresses"""
        range_str = self.network["IP_RANGE"]
        if "-" in range_str:
            start_ip, end_ip = range_str.split("-")
            start_parts = start_ip.split(".")
            end_num = int(end_ip)
            start_num = int(start_parts[-1])
            base_ip = ".".join(start_parts[:-1])
            
            return [f"{base_ip}.{i}" for i in range(start_num, end_num + 1)]
        else:
            return [range_str]
    
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.flask["DEBUG"] or self.dev["AUTO_RELOAD"]
    
    def is_testing(self) -> bool:
        """Check if running in testing mode"""
        return self.dev["TESTING"]
    
    def should_mock_devices(self) -> bool:
        """Check if should use mock devices"""
        return self.dev["MOCK_DEVICES"]
    
    def get_allowed_file_extensions(self) -> set:
        """Get allowed file extensions for uploads"""
        return self.upload["ALLOWED_EXTENSIONS"]
    
    def get_max_file_size(self) -> int:
        """Get maximum file size for uploads"""
        return self.upload["MAX_FILE_SIZE"]
    
    def validate_configuration(self) -> bool:
        """Validate configuration settings"""
        try:
            # Check required directories exist
            required_dirs = [
                self.data_dir,
                self.logs_dir,
                self.db_dir,
                self.documents_dir,
            ]
            
            for directory in required_dirs:
                if not Path(directory).exists():
                    logging.error(f"Required directory does not exist: {directory}")
                    return False
            
            # Check Ollama configuration
            if not self.ollama["BASE_URL"]:
                logging.error("Ollama base URL not configured")
                return False
                
            # Check network configuration
            if not self.network["SSH_USERNAME"]:
                logging.error("SSH username not configured")
                return False
                
            logging.info("Configuration validation successful")
            return True
            
        except Exception as e:
            logging.error(f"Configuration validation failed: {e}")
            return False
    
    def __str__(self) -> str:
        """String representation of configuration"""
        return f"AppConfig(debug={self.flask['DEBUG']}, mock_devices={self.dev['MOCK_DEVICES']})"


# Global configuration instance
config = AppConfig()

# Validate configuration on import
if not config.validate_configuration():
    logging.error("Configuration validation failed - some features may not work correctly") 