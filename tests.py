"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from Crypto.Cipher import AES

from django.core import serializers
import reversion

from django.test import TestCase
from django.db import models

from nudge.utils import *
from nudge.client import encrypt, serialize_batch
from nudge.server import decrypt
from nudge.models import Batch
from nudge.exceptions import *

from nudge.demo.models import Post, Author

reversion.register(Post)
reversion.register(Author)

from nudge.management.commands import nudgeinit
nudgeinit.Command().handle_noargs()

@reversion.create_revision()
def create_author():
         new_author= Author(name="Ross")
         new_author.save()
         return new_author



class EncryptionTest(TestCase):
    def setUp(self):
        self.new_author=create_author()
        
    def tearDown(self):
        Author.objects.all().delete()
    
    
    def test_encryption(self):
        """
        Tests that encryption and decryption are sane
        """
        message=u"Hello, Nudge Encryption!"
        key=generate_key()
        encrypted, iv = encrypt(key.decode('hex'), message)
        decrypted= decrypt(key.decode('hex'), encrypted, iv)
        self.assertEqual(message, decrypted.strip())
        
    def test_batch_serialization(self):
        key=generate_key()
        batch=Batch(title="Best Batch Ever")
        batch.save()
        add_versions_to_batch(batch, changed_items())
        serialized= serialize_batch(key.decode('hex'),batch)
        

class VersionTest(TestCase):
    def setUp(self):
        self.new_author=create_author()
        
    def tearDown(self):
        Author.objects.all().delete()
        
             
    def test_identify_changes(self):
        self.assertIn(self.new_author, [version.object for version in changed_items()])
        
    def test_add_changes_to_batch(self):
        new_batch=Batch(title="Best Batch Ever")
        new_batch.save()
        add_versions_to_batch(new_batch, changed_items())
        self.assertIn(self.new_author, [bi.version.object for bi in  new_batch.batchitem_set.all()])
        
        
    def test_batch_validation(self):
        batch1=Batch(title="Best Batch Ever")
        batch1.save()
        batch2=Batch(title="2nd Best Batch Ever")
        batch2.save()
        add_versions_to_batch(batch1, changed_items())
        add_versions_to_batch(batch2, changed_items())
        with self.assertRaises(BatchValidationError):
            batch1.is_valid(test_only=False)
            
            
    