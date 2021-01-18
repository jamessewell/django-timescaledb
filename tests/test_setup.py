from django.test import TestCase



class BaseSetup(TestCase):

    def setUp(self):
        print("SETUP")
    

    def test_can_setup(self):
        pass