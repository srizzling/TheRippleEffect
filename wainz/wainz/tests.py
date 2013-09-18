"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test import Client

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class RestTests(TestCase):
    def test_unused_image_methods(self):
        """
        Tests that the following methods are correctly  
        rejected by the image endpoint
        """
        """
        These fail as disallowed methods, so should return
        405 status codes
        """
        c = Client()
        response = c.get('/api/image')
        self.assertEqual(response.status_code, 405)
        c = Client()
        response = c.put('/api/image', {})
        self.assertEqual(response.status_code, 405)
        c = Client()
        response = c.delete('/api/image')
        self.assertEqual(response.status_code, 405)
        c = Client()
        response = c.options('/api/image')
        self.assertEqual(response.status_code, 405)
        """
        This has bad post syntax, so should return 400
        """
        c = Client()
        response = c.post('/api/image', {})
        self.assertEqual(response.status_code, 400)
        """
        Trace should return with the information we
        we posted to it
        """
        #TODO - write a test for this
