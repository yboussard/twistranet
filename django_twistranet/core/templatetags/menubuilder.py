"""
This is from http://code.google.com/p/django-menu/

"""

from django_twistranet.models import Menu, MenuItem  
from django import template  

register = template.Library()  
   
def build_menu(parser, token):  
    """ 
    {% menu menu_name %} 
    """  
    try:  
        tag_name, menu_name = token.split_contents()  
    except:  
        raise template.TemplateSyntaxError, "%r tag requires exactly one argument" % token.contents.split()[0]  
    return MenuObject(menu_name)  
   
class MenuObject(template.Node):
    def __init__(self, menu_name):  
        self.menu_name = menu_name  
   
    def render(self, context):  
        current_path = template.resolve_variable('path', context)  
        context['menuitems'] = get_items(self.menu_name, current_path)  
        return ''  
     
   
def get_items(menu, current_path):
    menuitems = []
    menu = Menu.objects.get(slug = menu)
    for i in menu.children:
        # XXX TODO: fix current position
        menuitems.append(i)
    return menuitems
   
register.tag('menu', build_menu)