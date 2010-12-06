"""
Mimics the Twitter API for the following resources:
statuses/show/:id
statuses/update
statuses/destroy/:id
statuses/retweet/:id
statuses/retweets/:id
"""
from piston.handler import BaseHandler
from piston.authentication import OAuthAuthentication, HttpBasicAuthentication
from twistranet.models import StatusUpdate
from piston import resource

auth = HttpBasicAuthentication(realm = "TwistraNet API")

class ShowHandler(BaseHandler):
    """
    Returns a single status, specified by the id parameter below. The status's author will be returned inline.
    Quite easy ;)
    
    Should return sth like:
    [
      {
        "coordinates": null,
        "favorited": false,
        "created_at": "Thu Jul 15 23:26:44 +0000 2010",
        "truncated": false,
        "text": "qu por qu kieres saver como poner pablito",
        "contributors": null,
        "id": 18639485000,
        "geo": null,
        "in_reply_to_user_id": null,
        "place": null,
        "in_reply_to_screen_name": null,
        "user": {
          "name": "paul isaias gallegos",
          "profile_sidebar_border_color": "eeeeee",
          "profile_background_tile": false,
          "profile_sidebar_fill_color": "efefef",
          "created_at": "Sun Jun 06 19:56:50 +0000 2010",
          "profile_image_url": "http://a1.twimg.com/profile_images/972549385/m_e26ddd7e7a424fdebceef1b3d005011f_normal.jpg",
          "location": "",
          "profile_link_color": "009999",
          "follow_request_sent": null,
          "url": null,
          "favourites_count": 0,
          "contributors_enabled": false,
          "utc_offset": -21600,
          "id": 152752917,
          "profile_use_background_image": true,
          "profile_text_color": "333333",
          "protected": false,
          "followers_count": 1,
          "lang": "es",
          "notifications": null,
          "time_zone": "Central Time (US & Canada)",
          "verified": false,
          "profile_background_color": "131516",
          "geo_enabled": false,
          "description": "",
          "friends_count": 2,
          "statuses_count": 18,
          "profile_background_image_url": "http://a3.twimg.com/profile_background_images/122541097/m_4011538d4b734ec7923bd641d2fa274f.jpg",
          "following": null,
          "screen_name": "izaloko"
        },
        "source": "web",
        "in_reply_to_status_id": null
      },
    ]    
    """
    fields = (
        "coordinates",
        "favorited",
        "created_at",
        "truncated",
        "text",
        "contributors",
        "id",
        "geo",
        "in_reply_to_user_id",
        "place",
        "in_reply_to_screen_name",
        "source",
        "in_reply_to_status_id",
        "user",
    )
    
    user_fields = (
        "name",
        "profile_sidebar_border_color",
        "profile_background_tile",
        "profile_sidebar_fill_color",
        "created_at",
        "profile_image_url",
        "location",
        "profile_link_color",
        "follow_request_sent",
        "url",
        "favourites_count",
        "contributors_enabled",
        "utc_offset",
        "id",
        "profile_use_background_image",
        "profile_text_color",
        "protected",
        "followers_count",
        "lang",
        "notifications",
        "time_zone",
        "verified",
        "profile_background_color",
        "geo_enabled",
        "description",
        "friends_count",
        "statuses_count",
        "profile_background_image_url",
        "following",
        "screen_name",
    )
    allowed_methods = ('GET', )
    model = StatusUpdate
    
    @classmethod
    def coordinates(self, obj):
        return None

    @classmethod
    def favorited(self, obj):
        return False

    @classmethod
    def truncated(self, obj):
        return False
        
    @classmethod
    def contributors(self, obj):
        return None
        
    @classmethod
    def geo(self, obj):
        return None
        
    @classmethod
    def in_reply_to_user_id(self, obj):
        return None
        
    @classmethod
    def place(self, obj):
        return None
    
    @classmethod
    def in_reply_to_screen_name(self, obj):
        return None
        
    @classmethod
    def source(self, obj):
        return obj.source
        
    @classmethod
    def in_reply_to_status_id(self, obj):
        return None

    @classmethod
    def user(self, obj):
        ret = dict()
        for field in self.user_fields:
            ret[field] = getattr(obj.author, field, None)
        return ret
    
    # def read(self, request, *args, **kwargs):
    #     """
    #     Return the nicely constructed object
    #     """
    #     # from api import users
    #     status = self.model.objects.get(pk=kwargs.get(pkfield))
    #     status['user'] = status.author

class PublicTimelineHandler(BaseHandler):
    allowed_methods = ('GET', )
    
    def read(self, dummy):
        return []

show = resource.Resource(ShowHandler, authentication = auth)
public_timeline = resource.Resource(PublicTimelineHandler, authentication = None)


