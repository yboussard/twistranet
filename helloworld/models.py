from django.db import models
from twistranet.models import Content


class HelloWorld(Content):
    """
    The classical 'Hello, World' example.
    Text is fixed, date and user are the only things that can move.
    
    You don't really need this in a production environment ;)
    """
    type_detail_view = None
    
    def preprocess_html_headline(self,):
        """
        Default is just to display "Hello, World!" as a headline.
        """
        return "Hello, World!"
        
    def preprocess_html_summary(self,):
        """
        Display a cheering text.
        """
        return "Hello, this is a <em>sample</em> content type for TwistraNet."
    
    