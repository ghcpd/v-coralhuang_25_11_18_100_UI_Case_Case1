"""Mock modules.shared for testing"""

class MockOpts:
    """Mock options"""
    def __init__(self):
        self.samples_save = False
        self.samples_format = "png"


class MockState:
    """Mock state"""
    def __init__(self):
        self.job_count = 0
        self.job = ""


opts = MockOpts()
state = MockState()
