from django.test import TestCase


class TestStringMethods(TestCase):
    def test_play(self):
        self.assertEqual(1, 4, msg='AHAHAHA')
    
    def test_1(self):
        self.assertIn('ab', 'abababab')
