class McpToolBase:
    """
    Base class for Model Context Protocol (MCP) Tools.
    All future tools must inherit this class to be automatically registered.
    """
    
    @property
    def name(self) -> str:
        """The exact name of the tool to be invoked by the AI."""
        raise NotImplementedError()

    @property
    def description(self) -> str:
        """A detailed description of what the tool does and when to use it."""
        raise NotImplementedError()

    @property
    def input_schema(self) -> dict:
        """JSON Schema defining the expected inputs."""
        raise NotImplementedError()

    @property
    def output_schema(self) -> dict:
        """JSON Schema defining the expected outputs."""
        raise NotImplementedError()

    def execute(self, inputs: dict) -> dict:
        """
        The method that actually runs the tool logic.
        Must accept a dict matching input_schema and return a dict matching output_schema.
        """
        raise NotImplementedError()
