"""
Models for the 'tag' object used by twistranet.
"""
from django.db import models
from django.db.models import Avg, Max, Min, Count

from twistranet.twistapp.models import Twistable
from twistranet.twistapp.lib import permissions   
from twistranet.twistapp.models import fields


# Default tagging settings.
# XXX TODO: Move this somewhere else
DEFAULT_EXPERTS_COUNT = 18              # Max experts fetched by default. The greater, the slower.
USERACCOUNT_TAG_EXPERT_FACTOR = 5       # Users bearing a tag are scored USER_TAG_EXPERT_FACTOR-times more (float).
CONTRIBUTOR_TAG_EXPERT_FACTOR = 0.5     # Users contributing to existing content are scored CONTRIBUTOR_TAG_EXPERT_FACTOR-times more (or less).
                                        # Default tag factor is the contributor status: everytime a user contributes a content, it scores 1.

class Tag(Twistable):
    """
    The Tag content is used to categorize content quite freely.
    We inherit from Twistable so that we can benefit from most of the twistable features,
    BUT you have to know that a Tag object is **NOT** secured and should be considered
    as always visible!
    """
    # Tag attributes.
    # Most of them (title, descr, ...) are derived from twistable, but a Tag can be bound
    # to as many Twistables as we want, plus tags can be nested (hence the 'parent' attribute).
    parent = models.ForeignKey("self", related_name = "children", null = True, blank = True)
    
    # Disable security model for tags (it's not necessary to have it, in fact)
    objects = models.Manager()
    _ALLOW_NO_PUBLISHER = True
    permission_templates = permissions.public_template
    default_picture_resource_slug = "default_menu_picture"
    
    # Behaviour overload
    def getDefaultPublisher(self,):
        """
        Default publisher is always None for tags.
        But we can imagine in further versions to have tag DOMAINS.
        """
        return None

    class Meta:
        app_label = 'twistapp'

    # Specific tag-related features.
    # We provide a set of methods to fetch users 'experts' on a field,
    # content matching a particular field, & so on
    def get_experts(self, max_count = DEFAULT_EXPERTS_COUNT):
        """
        Return experts on the given tag (as a LIST of no more than max_count users on the specified field).
        The first item in the returned list scores MORE than the second, and so on.
        Score is returned as the 'score' property of each underlying object.
        XXX TODO: Have this carefuly cached!
        """
        from twistranet.twistapp.models import UserAccount
        
        # Ppl who set it as their own tag
        # XXX TODO: Find a clever sorting key. Most active? Last activity?
        user_experts = UserAccount.objects.filter(tags__id = self.id).\
            extra(select = {"by__count": 1})[:max_count]
        
        # Ppl who contributed on it
        content_experts = UserAccount.objects.filter(by__tags__id = self.id).\
            annotate(Count('by')).order_by("-by__count")[:max_count]
        
        # Ppl who contributed to communities bearing this tag
        contributor_experts = UserAccount.objects.filter(by__publisher__tags = self.id).\
            annotate(Count('by')).order_by("-by__count")[:max_count]
        
        # Now let's aggregate all this...
        ret_dict = {}
        for lst, score_attr, factor in [
            (user_experts, "by__count", USERACCOUNT_TAG_EXPERT_FACTOR),
            (content_experts, "by__count", 1),
            (contributor_experts, "by__count", CONTRIBUTOR_TAG_EXPERT_FACTOR),
            ]:
            for useraccount in lst:
                uid = useraccount.id
                if not ret_dict.has_key(uid):
                    ret_dict[uid] = [0, useraccount, ]
                ret_dict[uid][0] += getattr(useraccount, score_attr) * factor
            
        # ...and return a pretty list.
        dictitems = ret_dict.items()
        dictitems.sort(lambda x,y: cmp(y[1], x[1]))
        ret = []
        for i in dictitems:
            u = i[1][1]
            u.score = i[1][0]
            ret.append(u)
        return ret

