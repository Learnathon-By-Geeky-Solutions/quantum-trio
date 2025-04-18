import os
import unittest
from unittest.mock import patch
from django.test import TestCase
from django.core.exceptions import ImproperlyConfigured

class TestSettings(TestCase):
    def test_database_settings_with_ci(self):
        # Simulate CI environment
        with patch.dict(os.environ, {'CI': 'true', 'SECRET_KEY': 'test-key'}):
            # Reload settings
            from importlib import reload
            import carehub.settings
            reload(carehub.settings)
            from carehub import settings
            self.assertEqual(settings.DATABASES['default']['ENGINE'], 'django.db.backends.sqlite3')
            self.assertEqual(settings.DATABASES['default']['NAME'], ':memory:')

    def test_database_settings_without_ci(self):
        # Simulate non-CI environment
        with patch.dict(os.environ, {'SECRET_KEY': 'test-key'}, clear=True):
            # Reload settings
            from importlib import reload
            import carehub.settings
            reload(carehub.settings)
            from carehub import settings
            # Assume PostgreSQL for non-CI (update if different)
            self.assertEqual(settings.DATABASES['default']['ENGINE'], 'django.db.backends.postgresql')
            self.assertNotEqual(settings.DATABASES['default']['NAME'], ':memory:')

    def test_secret_key_set(self):
        # Simulate SECRET_KEY being set via environment
        with patch.dict(os.environ, {'SECRET_KEY': 'test-key'}):
            # Reload settings
            from importlib import reload
            import carehub.settings
            reload(carehub.settings)
            from carehub import settings
            # Check that SECRET_KEY is non-empty (avoid hard-coding exact value)
            self.assertTrue(settings.SECRET_KEY)
           
    

if __name__ == '__main__':
    unittest.main()