"""Mock gradio for testing"""

class Component:
    """Base component class"""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class Slider(Component):
    """Mock Slider component"""
    pass


class Radio(Component):
    """Mock Radio component"""
    pass


class CheckboxGroup(Component):
    """Mock CheckboxGroup component"""
    pass
