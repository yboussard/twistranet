# Create your views here.
from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db.models import Q

from twistranet.models import Content, StatusUpdate, Community, Account, Community
from twistranet.lib import form_registry


def create_content(request, content_type):
    """
    XXX TODO
    """
    raise NotImplementedError


