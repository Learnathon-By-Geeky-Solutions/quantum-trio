import os
import sys
from unittest.mock import patch, MagicMock
import pytest
from django.core.asgi import get_asgi_application

# Ensure the carehub module is reloaded fresh
def reload_asgi_module():
    # Remove the module from sys.modules to force reload
    if 'carehub.asgi' in sys.modules:
        del sys.modules['carehub.asgi']
    import carehub.asgi
    return carehub.asgi

@pytest.fixture
def reset_env():
    """Fixture to reset os.environ after each test."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)

@patch('dotenv.load_dotenv')  # Patch at the source module
def test_load_dotenv_called(mock_load_dotenv, reset_env):
    """Test that load_dotenv is called during module import."""
    asgi = reload_asgi_module()
    mock_load_dotenv.assert_called_once()

@patch('django.core.asgi.get_asgi_application')  # Patch at the source module
def test_django_settings_module(mock_get_asgi, reset_env):
    """Test that DJANGO_SETTINGS_MODULE is set correctly."""
    reload_asgi_module()
    assert os.environ['DJANGO_SETTINGS_MODULE'] == 'carehub.settings'

@patch('django.core.asgi.get_asgi_application')  # Patch at the source module
def test_application_is_asgi_callable(mock_get_asgi, reset_env):
    """Test that application is set to the ASGI callable."""
    mock_asgi_app = MagicMock()
    mock_get_asgi.return_value = mock_asgi_app
    asgi = reload_asgi_module()
    assert asgi.application == mock_asgi_app
    mock_get_asgi.assert_called_once()

def test_application_callable_without_mock(reset_env):
    """Test that application is a callable ASGI application."""
    asgi = reload_asgi_module()
    assert callable(asgi.application)