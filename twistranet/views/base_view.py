from django.template import Context, RequestContext, loader
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template

class BaseView(object):
    """
    This is used as a foundation for our classical views.
    You can define for each class which are the boxes used on it.
    """
    context_boxes = []
    
    global_boxes = [
        "actions/general.part.html",
        "content/content_creation.box.html",
    ]
    
    @classmethod
    def as_view(cls, *args, **kw):
        return cls(*args, **kw)
    
    def __call__(self, request):
        """
        It's up to you to override this method.
        """
        raise NotImplementedError("You must override this method")
        
    def render_template(self, template, params):
        """
        Render the given template with the specified params (dict)...
        ...PLUS adds some parameters to provide better integration.
        """
        params['path'] = self.request.path
        params['context_boxes'] = self.context_boxes
        params['global_boxes'] = self.global_boxes
        t = get_template(template)
        c = RequestContext(self.request, params)
        return HttpResponse(t.render(c))
        
        
        