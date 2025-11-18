"""
Mock modules.scripts for testing purposes.
"""


class Script:
    """Base class for scripts."""
    
    def elem_id(self, name):
        """Generate element ID."""
        return f"outpainting_{name}"

