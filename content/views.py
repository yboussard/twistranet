# Create your views here.
from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required

from TwistraNet.content.models import Content, StatusUpdate
from TwistraNet.account.models import Account

from TwistraNet.content.forms import getContentFormClass


@login_required
def account(request, account_id):
    """
    Account (user/profile) page.
    We just diplay posts of any given account.
    XXX TODO:
        - Check if account is listed and permit only if approved
    """
    account = Account.objects.get(id = account_id)
    latest_list = Content.secured(account).filter(account = account)
    latest_content_viewlets = [ HtmlContentViewlet(content) for content in latest_list ]
    t = loader.get_template('account.html')
    t = RequestContext(
        request,
        {
            "latest_content_list": latest_content_viewlets,
        },
        )
    return HttpResponse(t.render(c))
    
    

@login_required
def wall(request):
    """
    The WALL page. This is the "homepage" of the currently logged user.
    """
    # Account information used to build the wall view
    account = request.user.get_profile()
    
    # Wall edition form if user has the right to write on it
    form_class = getContentFormClass(account, account)
    if request.method == 'POST':                        # If the form has been submitted...
        # Should use some method to determine the form to render here
        form = form_class(request.POST)           # A form bound to the POST data
        if form.is_valid():                             # All validation rules pass
            # Process the data in form.cleaned_data
            c = form.save(commit = False)
            c.preSave(account)
            c.save()
            return HttpResponseRedirect('/') # Redirect after POST
    else:
        form = form_class() # An unbound form

    # Content displayed on the wall
    latest_list = Content.secured(account).all().order_by('-date')[:5]
    latest_content_viewlets = [ HtmlContentViewlet(content) for content in latest_list ]
    
    # Render the template
    t = loader.get_template('wall.html')
    c = RequestContext(
        request,
        {
            'latest_content_list': latest_content_viewlets,
            'form': form,
        },
        )
    return HttpResponse(t.render(c))
    # Or can do:
    # return render_to_response('wall.html', {'latest_content_list': latest_content_list})
    
    
class HtmlContentViewlet:
    """
    This superclass is used to provide special "viewlets" to content templates.
    """
    def __init__(self, content):
        """
        Init the superclass with the content itself.
        We ensure to init the proper subclass to display a nice view.
        """
        # Get right content type
        target_content = getattr(content, content.content_type.lower())
        self.content = target_content
    
    def htmlSingle(self, ):
        """
        This special view renders a single chunk of content information.
        It is used everytime we have to display it as a whole page.
        """
    
    
    def htmlList(self, ):
        """
        This view renders a single chunk of content information in a LIST.
        We must use that everytime we return a long and condensed list of information.
        """
    
    def htmlSummary(self, ):
        """
        We use this to display a content summary, for example inside the wall.
        Every content type may generate its own summary.
        """
        # TODO: Check if content defines its own summary view
        # XXX TODO
    
        # Special HTML renderers for various elements
        t = get_template('content/summary.part.html')
        return t.render(Context({'content': self.content}))


