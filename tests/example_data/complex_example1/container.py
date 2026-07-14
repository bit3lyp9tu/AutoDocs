from plugins.uppercase import UppercasePlugin
from plugins.reverse import ReversePlugin


class Container:
    def __init__(self):
        self.plugins = {
            "uppercase": UppercasePlugin(),
            "reverse": ReversePlugin(),
        }

    def get(self, name: str):
        return self.plugins[name]
