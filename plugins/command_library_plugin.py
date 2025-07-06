"""Command Library Plugin (refactored Feature 0500).

Provides the /library route as a Flask Blueprint so it can be loaded via the
plugin architecture (Feature 1000).
"""
from flask import Blueprint, render_template
from flask_login import login_required
from src.web.decorators import roles_required

class CommandLibraryPlugin:
    def __init__(self):
        self.name = "Command Library"
        self.bp = Blueprint(
            'command_library', __name__, template_folder='../src/web/templates'
        )

        # Move routes here, binding them to the blueprint
        @self.bp.route('/library')
        @login_required
        @roles_required('Admin', 'Operator')
        def library():
            """Render the command library page."""
            return render_template('library.html', commands=self.get_commands())

    def register(self, app, manager):
        """Called by plugin loader to register with the manager and app."""
        app.register_blueprint(self.bp)
        manager.register_plugin(self)
        
    def get_commands(self):
        """Returns a list of commands provided by this plugin."""
        return [
            {"id": 1, "category": "Cisco IOS", "command": "show ip interface brief", "description": "Display a brief summary of IP interface status and configuration."},
            {"id": 2, "category": "Cisco IOS", "command": "show running-config", "description": "Display the current running configuration."},
            {"id": 3, "category": "Juniper Junos", "command": "show interfaces terse", "description": "Display a brief summary of interface status."},
            {"id": 4, "category": "Arista EOS", "command": "show ip interface brief", "description": "Display a brief summary of IP interface status and configuration."},
        ]

def register(app, manager):
    """Plugin registration hook."""
    instance = CommandLibraryPlugin()
    instance.register(app, manager)
