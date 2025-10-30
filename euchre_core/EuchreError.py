"""
euchre_error.py

Defines the custom EuchreError class for handling game-specific exceptions.
"""

class EuchreError(Exception):
    """
    Custom exception class for Euchre-specific errors.
    """

    def __init__(self, msg: str) -> None:
        """
        Initialize the EuchreError with an error message.

        Args:
            msg (str): The error message.
        """
        super().__init__(msg)

    def __json__(self):
        return {"type": EuchreError.__name__, "message": str(self)}