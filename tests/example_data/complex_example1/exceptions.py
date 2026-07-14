class PluginError(Exception):
    """Base plugin error."""


class ProcessingError(PluginError):
    pass
