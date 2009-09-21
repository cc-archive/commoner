import django.test
from django.core import mail

from django.contrib import auth
from commoner.log.models import LogEntry

class TestLogEntries(django.test.TestCase):

    fixtures = ['test_users.json',]

    def test_add_basic_log_entry(self):

        entry = LogEntry.objects.record("testing",
                                        "testing message")
        entry.save()

        self.assertEquals(entry.message_id, "testing")
        self.assertEquals(entry.message, "testing message")
        self.assert_(entry.created is not None)

    def test_add_sends_email(self):

        entry = LogEntry.objects.record("testing",
                                        "testing message",
                                        send_email=True)
        entry.save()

        self.assert_(len(mail.outbox) > 0)

    def test_add_entry_with_generic_object(self):

        user = auth.models.User.objects.get(username='testing')

        entry = LogEntry.objects.record("testing",
                                        "testing message",
                                        user)
        entry.save()

        self.assertEquals(entry.message_id, "testing")
        self.assertEquals(entry.message, "testing message")
        self.assert_(entry.created is not None)
        self.assertEquals(entry.content_object, user)
