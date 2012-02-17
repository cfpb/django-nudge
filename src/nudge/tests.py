"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from Crypto.Cipher import AES

from django.core import serializers
import reversion
from reversion.models import Version

from django.test import TestCase
from django.db import models
from django.core.exceptions import *

from nudge.utils import *
from nudge.client import encrypt, serialize_batch
from nudge.server import decrypt, process_batch
from nudge.models import Batch, BatchItem, PushHistoryItem
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

@reversion.create_revision()
def delete_with_reversion(object):
    object.delete()


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
        
        

class BatchTest(TestCase):
    def setUp(self):
        self.key=generate_key()
        self.batch=Batch(title="Best Batch Ever")
        self.new_author=create_author()
        self.batch.save()
        
        
    def tearDown(self):
        Author.objects.all().delete()
        BatchItem.objects.all().delete()
        
        
    def test_batch_serialization_and_processing(self):
        add_versions_to_batch(self.batch, changed_items())
        serialized= serialize_batch(self.key.decode('hex'),self.batch)
        processed_batch=process_batch(self.key.decode('hex'), serialized['batch'], serialized['iv'])
        
    def test_batch_with_deletion(self):
        delete_with_reversion(self.new_author)
        add_versions_to_batch(self.batch, changed_items())
        serialized= serialize_batch(self.key.decode('hex'),self.batch)
        with self.assertRaises(ObjectDoesNotExist): # because it doesn't exist anymore in this database
            processed_batch=process_batch(self.key.decode('hex'), serialized['batch'], serialized['iv'])

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
        
    def test_add_deletion_to_batch(self):
        delete_with_reversion(self.new_author)
        
        
        
    def test_batch_validation(self):
        batch1=Batch(title="Best Batch Ever")
        batch1.save()
        batch2=Batch(title="2nd Best Batch Ever")
        batch2.save()
        add_versions_to_batch(batch1, changed_items())
        add_versions_to_batch(batch2, changed_items())
        with self.assertRaises(BatchValidationError):
            batch1.is_valid(test_only=False)
            
            
    