class NeoversePlugin:
    """
    Base class for all NEOVERSE OS plugins.
    Modules inheriting this class will be automatically discovered and initialized.
    """
    def initialize(self):
        """
        Called automatically by the PluginManager on startup.
        Ideal place to subscribe to Event Bus channels.
        """
        pass
