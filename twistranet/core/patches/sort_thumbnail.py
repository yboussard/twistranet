from sorl.thumbnail.images import ImageFile
from django.core.urlresolvers import reverse
from twistranet.twistapp.lib.log import *

@property
def absolute_url(self):
    """
    return thumbnail absolute_url
    """
    home_url = reverse("twistranet_home")
    return '%s%s' %(home_url, self.storage.url(self.name))

log.info("Patched sorl.thumbnail.image.ImageFile.url to get absolute url")
ImageFile.old_url = ImageFile.url
ImageFile.url = absolute_url