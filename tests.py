"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from Crypto.Cipher import AES

from django.core import serializers


from django.test import TestCase
from django.db import models

from nudge.utils import *
from nudge.client import encrypt
from nudge.server import decrypt

from nudge.demo import models, admin

from nudge.management.commands import nudgeinit
nudgeinit.Command().handle_noargs()

class EncryptionTest(TestCase):
    def test_encryption(self):
        """
        Tests that generate_key produces a valid hex key
        """
        message=u"Hello, Nudge Encryption!"
        key=generate_key()
        encrypted, iv = encrypt(key.decode('hex'), message)
        decrypted= decrypt(key.decode('hex'), encrypted, iv)
        self.assertEqual(message, decrypted.strip())
