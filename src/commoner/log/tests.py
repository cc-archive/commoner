import django.test 

from django.contrib import auth
from commoner.log.models import LogEntry

class TestLogEntries(django.test.TestCase):

    def test_add_basic_log_entry(self):

        entry = LogEntry("testing", "testing message")
        entry.save()

        self.assertEquals(entry.message_id, "testing")
        self.assertEquals(entry.message, "testing message")
        self.assert_(entry.created is not None)

        
