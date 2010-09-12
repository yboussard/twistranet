from django.db import models
from TwistraNet.content.models import Content


class HelloWorld(Content):
    """
    The classical 'Hello, World' example.
    Text is fixed, date and user are the only things that can move.
    
    You don't really need this in a production environment ;)
    """
    def getText(self):
        """This always return the same boring text.
        """
        return "Hello, World"


