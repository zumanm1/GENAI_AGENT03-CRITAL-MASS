"""Simple plugin loader for Network Automation AI Agent (Feature 1000).

Plugins are plain Python modules placed in the top-level 'plugins' directory
( sibling to this 'src' directory ). Each plugin module must expose a
`register(app)` function that takes the Flask `app` object and registers any
blueprints, routes, CLI commands, etc.
"""
from __future__ import annotations

import importlib
import logging
import sys
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

PLUGINS_DIR = Path(__file__).resolve().parent.parent.parent / 'plugins'


class PluginManager:
    def __init__(self):
        self.loaded_plugins = []

    def _discover_plugin_modules(self) -> List[str]:
        """Return a list of import paths for plugin modules."""
        modules = []
        if not PLUGINS_DIR.exists():
            logger.warning("Plugins directory does not exist: %s", PLUGINS_DIR)
            return modules

        # Ensure directory is on sys.path for importlib
        if str(PLUGINS_DIR.parent) not in sys.path:
            sys.path.insert(0, str(PLUGINS_DIR.parent))

        for file in PLUGINS_DIR.glob("*_plugin.py"):
            modules.append(f"plugins.{file.stem}")
        return modules

    def load_plugins(self, app):
        """Discover and register plugins with the Flask app."""
        plugin_paths = self._discover_plugin_modules()

        for path in plugin_paths:
            try:
                module = importlib.import_module(path)
                if hasattr(module, 'register'):
                    # Pass the manager instance to the plugin
                    module.register(app, self)
                    logger.info("Loaded plugin: %s", path)
                    # The plugin itself should call register_plugin
                else:
                    logger.warning(
                        "Plugin %s does not have a register function.", path)
            except Exception as e:
                logger.error("Failed to load plugin %s: %s", path, e)

    def register_plugin(self, plugin_instance):
        """Allows plugins to register themselves with the manager."""
        self.loaded_plugins.append(plugin_instance)
        logger.info(f"Plugin {plugin_instance.name} registered.")

    def get_all_plugins(self):
        """Returns all loaded plugin instances."""
        return self.loaded_plugins


plugin_manager = PluginManager()


def load_plugins(app):
    """Legacy function for loading plugins, now delegates to the manager."""
    plugin_manager.load_plugins(app)
