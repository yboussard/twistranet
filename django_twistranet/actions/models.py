

class Category(object):
    def __init__(self, id, label):
        self.id = id
        self.label = label

MAIN_ACTION = Category("main", "Main action")
USER_ACTIONS = Category("user", "User actions")                                     # Default: The user actions in the top bar
ACCOUNT_ACTIONS = Category("account", "Global account actions")                     # Default: The 'user & communities' box
LOCAL_ACTIONS = Category("local", "Local actions")
CONTENT_CREATION_ACTIONS = Category("content_creation", "Content creation actions") # The Create Content box and/or dropdown lists
GLOBAL_ACTIONS = Category("global", "Global actions")                               # The "toolbox" actions

class Action(object):
    """
    By now, actions are not stored in database, but they could be one day.
    """
    
    def __init__(self, category = None, label = None, confirm = None, url = None):
        """
        Store and check parameters.
        If action_class is None, it must be resolved later.
        """
        self.label = label
        self.category = category
        self.confirm = confirm
        self.url = url
        
        if url is None:
            raise ValueError("URL must be given")
        
        if not isinstance(category, Category):
            raise ValueError("%s must be a Category object" % category)
    
