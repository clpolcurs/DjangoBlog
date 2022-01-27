import json

from django.test import Client, RequestFactory, TestCase

from accounts.models import BlogUser
from .models import OwnTrackLog


# Create your tests here.

class OwnTrackLogTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
    
    def test_own_track_log(self):
        o = {
            'tid': 12,
            'lat': 123.123,
            'lon': 134.341
        }
        
        length = self.get_track_log_number(o)
        o = {
            'tid': 12,
            'lat': 123.123
        }
        
        length = self.get_track_log_number(o)
        rsp = self.client.get('/owntracks/show_maps')
        self.assertEqual(rsp.status_code, 302)
        
        user = BlogUser.objects.create_superuser(
                email="liangliangyy1@gmail.com",
                username="liangliangyy1",
                password="liangliangyy1"
        )
        
        self.client.login(username='liangliangyy1', password='liangliangyy1')
        s = OwnTrackLog()
        s.tid = 12
        s.lon = 123.234
        s.lat = 34.234
        s.save()
        
        rsp = self.client.get('/owntracks/show_dates')
        self.assertEqual(rsp.status_code, 200)
        rsp = self.client.get('/owntracks/show_maps')
        self.assertEqual(rsp.status_code, 200)
    
    # TODO Rename this here and in `test_own_track_log`
    def get_track_log_number(self, o):
        self.client.post('/owntracks/logtracks', json.dumps(o), content_type='application/json')
        result = len(OwnTrackLog.objects.all())
        self.assertEqual(result, 1)
        return result
