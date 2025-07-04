"""
Ollama Model Configuration
Manages AI model settings and preferences for the Network Automation AI Agent
"""

import os
import json
from typing import Dict, List, Optional

class ModelConfig:
    """Configuration for Ollama models"""
    
    # Default model preferences (ordered by performance)
    DEFAULT_MODELS = [
        {
            'name': 'llama3.2:1b',
            'size': '1.2B',
            'speed': 'fastest',
            'quality': 'good',
            'use_case': 'Quick responses, basic tasks',
            'recommended': True,
            'priority': 1
        },
        {
            'name': 'phi4-mini:latest',
            'size': '3.8B',
            'speed': 'fast',
            'quality': 'better',
            'use_case': 'Balanced performance',
            'recommended': False,
            'priority': 2
        },
        {
            'name': 'gemma3:latest',
            'size': '4.3B',
            'speed': 'medium',
            'quality': 'good',
            'use_case': 'Complex reasoning',
            'recommended': False,
            'priority': 3
        },
        {
            'name': 'llava:latest',
            'size': '7B',
            'speed': 'slow',
            'quality': 'best',
            'use_case': 'Advanced tasks, image processing',
            'recommended': False,
            'priority': 4
        }
    ]
    
    # Model performance characteristics
    SPEED_RANKING = {
        'fastest': 1,
        'fast': 2,
        'medium': 3,
        'slow': 4
    }
    
    QUALITY_RANKING = {
        'good': 1,
        'better': 2,
        'best': 3
    }
    
    # Default settings
    DEFAULT_SETTINGS = {
        'auto_select_fastest': True,
        'preferred_model': 'llama3.2:1b',
        'fallback_model': 'llama3.2:1b',
        'chat_timeout': 30,
        'max_chat_history': 50,
        'model_switching_enabled': True,
        'performance_monitoring': True
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize model configuration"""
        self.config_file = config_file or os.path.join(
            os.path.dirname(__file__), 'model_settings.json'
        )
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.load_settings()
    
    def load_settings(self) -> None:
        """Load settings from configuration file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    saved_settings = json.load(f)
                    self.settings.update(saved_settings)
        except Exception as e:
            print(f"Warning: Could not load model settings: {e}")
    
    def save_settings(self) -> None:
        """Save current settings to configuration file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving model settings: {e}")
    
    def get_fastest_model(self, available_models: List[Dict]) -> Optional[str]:
        """Get the fastest available model"""
        if not available_models:
            return self.settings['fallback_model']
        
        # Sort by speed (fastest first)
        sorted_models = sorted(
            available_models,
            key=lambda x: self.SPEED_RANKING.get(x.get('speed', 'medium'), 3)
        )
        
        return sorted_models[0]['name'] if sorted_models else self.settings['fallback_model']
    
    def get_recommended_model(self, available_models: List[Dict]) -> Optional[str]:
        """Get the recommended model based on settings"""
        if self.settings['auto_select_fastest']:
            return self.get_fastest_model(available_models)
        
        # Check if preferred model is available
        preferred = self.settings['preferred_model']
        for model in available_models:
            if model['name'] == preferred:
                return preferred
        
        # Fallback to fastest if preferred not available
        return self.get_fastest_model(available_models)
    
    def get_model_info(self, model_name: str) -> Dict:
        """Get detailed information about a model"""
        for model in self.DEFAULT_MODELS:
            if model['name'] == model_name:
                return model
        
        # Return default info for unknown models
        return {
            'name': model_name,
            'size': 'Unknown',
            'speed': 'medium',
            'quality': 'good',
            'use_case': 'General purpose',
            'recommended': False,
            'priority': 99
        }
    
    def update_setting(self, key: str, value) -> None:
        """Update a specific setting"""
        if key in self.settings:
            self.settings[key] = value
            self.save_settings()
    
    def get_setting(self, key: str, default=None):
        """Get a specific setting"""
        return self.settings.get(key, default)
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults"""
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.save_settings()
    
    def get_performance_score(self, model_name: str) -> int:
        """Get performance score for a model (lower is better)"""
        model_info = self.get_model_info(model_name)
        speed_score = self.SPEED_RANKING.get(model_info['speed'], 3)
        quality_score = self.QUALITY_RANKING.get(model_info['quality'], 1)
        
        # Weighted score (speed is more important for performance)
        return (speed_score * 2) + quality_score
    
    def sort_models_by_performance(self, models: List[Dict]) -> List[Dict]:
        """Sort models by performance (fastest first)"""
        return sorted(models, key=lambda x: self.get_performance_score(x['name']))

# Global model configuration instance
model_config = ModelConfig() 