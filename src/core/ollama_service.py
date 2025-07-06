"""
Ollama Service
Handles interactions with the Ollama LLM for network automation tasks
"""

import logging
import requests
from typing import Dict, List, Any
from datetime import datetime

from .config import config


class OllamaService:
    """Service for interacting with Ollama LLM"""

    def __init__(self):
        self.base_url = config.ollama['BASE_URL']
        self.model = config.ollama['MODEL_NAME']
        self.timeout = config.ollama['TIMEOUT']
        self.logger = logging.getLogger(__name__)

        # Verify connection
        self._verify_connection()

    def _verify_connection(self) -> bool:
        """Verify connection to Ollama service"""
        try:
            response = requests.get(f"{self.base_url}/api/version", timeout=5)
            if response.status_code == 200:
                version_info = response.json()
                self.logger.info(
                    f"Connected to Ollama version: "
                    f"{version_info.get('version', 'unknown')}"
                )
                return True
            else:
                self.logger.error(
                    f"Failed to connect to Ollama: HTTP {response.status_code}"
                )
                return False
        except Exception as e:
            self.logger.error(f"Error connecting to Ollama: {e}")
            return False

    def check_connection(self) -> bool:
        """Alias for _verify_connection for backward compatibility."""
        return self._verify_connection()

    def list_models(self) -> List[Dict[str, Any]]:
        """Get list of available models"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags", timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                return data.get('models', [])
            else:
                self.logger.error(
                    f"Failed to list models: HTTP {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"Error listing models: {e}")
            return []

    def is_model_available(self, model_name: str = None) -> bool:
        """Check if a specific model is available"""
        if model_name is None:
            model_name = self.model

        models = self.list_models()
        available_models = [model['name'] for model in models]
        return model_name in available_models

    def generate_response(
        self,
        prompt: str,
        model: str = None,
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """Generate a response from the LLM"""
        if model is None:
            model = self.model

        try:
            # Prepare the request payload
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }

            # Add system prompt if provided
            if system_prompt:
                payload["system"] = system_prompt

            # Make the request
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result.get("response", ""),
                    "model": model,
                    "prompt_tokens": result.get("prompt_eval_count", 0),
                    "completion_tokens": result.get("eval_count", 0),
                    "total_duration": result.get("total_duration", 0),
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                self.logger.error(
                    f"Ollama generation failed: HTTP {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "timestamp": datetime.utcnow().isoformat()
                }

        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """Generate a chat completion (conversation format)"""
        if model is None:
            model = self.model

        try:
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }

            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result.get("message", {}).get("content", ""),
                    "model": model,
                    "prompt_tokens": result.get("prompt_eval_count", 0),
                    "completion_tokens": result.get("eval_count", 0),
                    "total_duration": result.get("total_duration", 0),
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                self.logger.error(
                    f"Ollama chat failed: HTTP {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "timestamp": datetime.utcnow().isoformat()
                }

        except Exception as e:
            self.logger.error(f"Error in chat completion: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def analyze_network_config(self, config_text: str) -> Dict[str, Any]:
        """Analyze network configuration using LLM"""
        system_prompt = (
            """You are a network engineer AI assistant specializing in Cisco "
            "network configurations. Analyze the provided configuration and "
            "identify:\n"
            "        1. Device type and role\n"
            "        2. Interface configurations\n"
            "        3. Routing protocols (OSPF, BGP, etc.)\n"
            "        4. Potential issues or misconfigurations\n"
            "        5. Security settings\n"
            "        6. Recommendations for improvement\n\n"
            "        Provide a structured analysis in JSON format."""
        )
        prompt = f"""Please analyze this network configuration:

{config_text}

Provide a detailed analysis including any issues found and recommendations."""

        return self.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,  # Lower temperature for more consistent analysis
            max_tokens=1500
        )

    def generate_network_command(
        self, task_description: str, device_type: str = "cisco_ios"
    ) -> Dict[str, Any]:
        """Generate network commands for a specific task"""
        system_prompt = (
            f"""You are a network automation expert. Generate {device_type} "
            f"commands for network tasks. Always provide:\n"
            f"        1. The exact commands to execute\n"
            f"        2. Any prerequisites or warnings\n"
            f"        3. Expected outcomes\n"
            f"        4. Rollback commands if applicable\n\n"
            f"        Be precise and safe - only generate commands you are "
            f"confident about."""
        )

        prompt = (
            f"""Generate {device_type} commands for this task: "
            f"{task_description}\n\n"
            f"Please provide a structured format with explanations."""
        )

        return self.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.2,  # Very low temperature for command generation
            max_tokens=800
        )

    def troubleshoot_network_issue(
        self, issue_description: str, device_logs: str = ""
    ) -> Dict[str, Any]:
        """Help troubleshoot network issues"""
        system_prompt = (
            """You are a senior network troubleshooting expert. Analyze "
            "network issues and provide:\n"
            "        1. Possible root causes\n"
            "        2. Diagnostic steps to verify the issue\n"
            "        3. Resolution steps\n"
            "        4. Prevention measures\n\n"
            "        Be methodical and provide step-by-step guidance."""
        )

        prompt = f"""Network Issue: {issue_description}

Device Logs (if available):
{device_logs}

Please provide troubleshooting guidance."""

        return self.generate_response(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.4,
            max_tokens=1200
        )

    def health_check(self) -> Dict[str, Any]:
        """Perform health check of the Ollama service"""
        try:
            # Check connection
            if not self._verify_connection():
                return {
                    "status": "unhealthy",
                    "error": "Cannot connect to Ollama service",
                    "timestamp": datetime.utcnow().isoformat()
                }

            # Check if model is available
            if not self.is_model_available():
                return {
                    "status": "unhealthy",
                    "error": f"Model '{self.model}' not available",
                    "available_models": [
                        m["name"] for m in self.list_models()
                    ],
                    "timestamp": datetime.utcnow().isoformat()
                }

            # Test generation with a simple prompt
            test_result = self.generate_response(
                prompt=(
                    "Hello, please respond with 'OK' to confirm "
                    "you're working."
                ),
                temperature=0.1,
                max_tokens=10,
            )

            if test_result["success"]:
                return {
                    "status": "healthy",
                    "model": self.model,
                    "base_url": self.base_url,
                    "test_response": test_result["response"][:50],
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": "Test generation failed",
                    "details": test_result.get("error", "Unknown error"),
                    "timestamp": datetime.utcnow().isoformat()
                }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# Global instance
ollama_service = OllamaService()
