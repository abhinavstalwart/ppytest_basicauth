import pytest
import requests
from unittest.mock import patch, Mock
from datetime import datetime, timedelta
from src.common.authentication.oAuth2Handler import OAuth2Handler  # Update with the correct import path

@pytest.fixture
def oauth_handler():
    return OAuth2Handler(
        client_id="test_client_id",
        client_secret="test_client_secret",
        token_url="https://example.com/token",
        auth_url="https://example.com/auth",
        redirect_uri="https://example.com/callback",
        username="test_user",
        password="test_password",
        refresh_token="test_refresh_token",
        grant_type="authorization_code",
    )

@patch("requests.post")
def test_client_credentials_flow(mock_post, oauth_handler):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"access_token": "test_access_token"}
    mock_post.return_value = mock_response
    
    token = oauth_handler._client_credentials_flow()
    
    assert token == "test_access_token"
    assert oauth_handler.access_token == "test_access_token"

@patch("requests.post")
def test_exchange_code_for_token(mock_post, oauth_handler):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token"
    }
    mock_post.return_value = mock_response
    
    token = oauth_handler._exchange_code_for_token("test_auth_code")
    
    assert token == "test_access_token"
    assert oauth_handler.refresh_token == "test_refresh_token"

@patch("requests.post")
def test_refresh_access_token(mock_post, oauth_handler):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "new_access_token",
        "refresh_token": "new_refresh_token",
        "expires_in": 3600
    }
    mock_post.return_value = mock_response
    
    token = oauth_handler.refresh_access_token()
    
    assert token == "new_access_token"
    assert oauth_handler.refresh_token == "new_refresh_token"
    assert oauth_handler.token_expiry > datetime.utcnow()

@patch("requests.post")
def test_refresh_access_token_failure(mock_post, oauth_handler):
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Invalid refresh token"
    mock_post.return_value = mock_response
    
    with pytest.raises(ValueError, match="Failed to refresh token: Invalid refresh token"):
        oauth_handler.refresh_access_token()

@patch("requests.get")
def test_get_headers(mock_get, oauth_handler):
    oauth_handler.access_token = "test_access_token"
    headers = oauth_handler.get_headers()
    assert headers == {"Authorization": "Bearer test_access_token"}
