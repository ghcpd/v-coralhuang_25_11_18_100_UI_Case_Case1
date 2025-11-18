"""
Mock modules.shared for testing purposes.
"""


class MockOpts:
    """Mock opts object."""
    def __init__(self):
        self.samples_save = False
        self.samples_format = "png"


class MockState:
    """Mock state object."""
    def __init__(self):
        self.job_count = 0
        self.job = ""


opts = MockOpts()
state = MockState()

