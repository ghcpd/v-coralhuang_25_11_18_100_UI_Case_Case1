"""Mock modules.scripts for testing"""

class Script:
    """Base class for SD WebUI scripts"""
    
    def elem_id(self, item_id):
        """Generate element ID"""
        return f"{self.__class__.__name__}_{item_id}"
    
    def title(self):
        """Script title"""
        return "Script"
    
    def show(self, is_img2img):
        """Whether to show this script"""
        return True
    
    def ui(self, is_img2img):
        """Create UI elements"""
        return []
    
    def run(self, p, *args):
        """Run the script"""
        pass
