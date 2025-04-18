import os
import unittest
from unittest.mock import patch
from django.test import TestCase

class TestWSGI(TestCase):
    def test_wsgi_application(self):
        # Test with DJANGO_SETTINGS_MODULE pre-set
        with patch.dict(os.environ, {'DJANGO_SETTINGS_MODULE': 'carehub.settings'}):
            from carehub import wsgi
            self.assertTrue(callable(wsgi.application))
            self.assertEqual(os.environ.get('DJANGO_SETTINGS_MODULE'), 'carehub.settings')


if __name__ == '__main__':
    unittest.main()