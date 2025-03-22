import pytest
import base64
from abc import ABC, abstractmethod

class BaseAuthHandler(ABC):
    """
    Base class for authentication handlers.
    """

    @abstractmethod
    def authenticate(self):
        """
        Perform the authentication process and return credentials.
        """
        pass

    @abstractmethod
    def refresh_token(self):
        """
        Refresh the token. Optional for API Key or Basic Auth.
        """
        pass

    @abstractmethod
    def get_headers(self) -> dict:
        """
        Generate the authentication headers. Must be implemented by derived classes.
        """
        pass



class BasicAuthHandler(BaseAuthHandler):
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def authenticate(self):
        return {"username": self.username, "password": self.password}

    def refresh_token(self):
        raise NotImplementedError("Basic Auth does not support token refreshing.")

    def get_headers(self) -> dict:
        auth_str = f"{self.username}:{self.password}"
        encoded_auth = base64.b64encode(auth_str.encode()).decode()
        return {"Authorization": f"Basic {encoded_auth}"}

def test_authenticate():
    auth_handler = BasicAuthHandler("testuser", "testpass")
    assert auth_handler.authenticate() == {"username": "testuser", "password": "testpass"}

def test_get_headers():
    auth_handler = BasicAuthHandler("testuser", "testpass")
    auth_str = "testuser:testpass"
    encoded_auth = base64.b64encode(auth_str.encode()).decode()
    expected_headers = {"Authorization": f"Basic {encoded_auth}"}
    assert auth_handler.get_headers() == expected_headers

def test_refresh_token():
    auth_handler = BasicAuthHandler("testuser", "testpass")
    with pytest.raises(NotImplementedError, match="Basic Auth does not support token refreshing."):
        auth_handler.refresh_token()
