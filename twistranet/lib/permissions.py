from roles import *

# Basic permissions
can_view = "can_view"
can_edit = "can_edit"
can_list = "can_list"
can_list_members = "can_list_members"
can_publish = "can_publish"
can_join = "can_join"
can_leave = "can_leave"

# Special role arrangements
class PermissionTemplate:
    """
    Permission template helper.
    """
    def __init__(self, perm_tuple, default_index = 0):
        """
        See content_permissions_templates for an example of what perm_tuple should look like.
        """
        self.perm_tuple = perm_tuple
        self.default_index = default_index
        
    def get_choices(self):
        """
        Return a choice tuple suitable for the model
        """
        return [ (t["id"], t["name"], ) for t in self.perm_tuple ]
        
    def get_default(self):
        return self.perm_tuple[self.default_index]["id"]
        
    def permissions(self):
        return self.perm_tuple
        

content_templates = PermissionTemplate((
    {
        "id":               "public",
        "name":             "Public content", 
        "description":      "Content visible to anyone who can view this page.",
        can_view:           (content_public, ),
        can_edit:           (content_author, administrator),
    },
    {
        "id":               "network",
        "name":             "Network-only content",
        "description":      """Content visible only to my network.""",
        can_view:           (content_network, ),
        can_edit:           (content_author, administrator),
    },
    {
        "id":               "members",
        "name":             "Members-only content",
        "description":      "Content visible only to community members",
        can_view:           (content_community_member, ),
        can_edit:           (content_author, administrator),
    },
    {
        "id":               "private",
        "name":             "Private",
        "description":      "Content visible only for the author",
        can_view:           (content_author, ),
        can_edit:           (content_author, ),
    },
))


# XXX TODO: Have some specific stuff for each account type. Not an easy problem to overload the choices field...
account_templates = PermissionTemplate((
    # User account templates
    {
        "id":               "internet",
        "name":             "Public Internet account",
        "description":      "Account listed and accessible to anyone who has access to TwistraNet.",
        can_view:           (anonymous, ),
    },
    {
        "id":               "intranet",
        "name":             "Restricted intranet account",
        "description":      "Account listed and accessible to anyone who has access to TwistraNet.",
        can_view:           (authenticated, ),
    },
    {
        "id":               "listed",
        "name":             "Private but searchable", 
        "description":      "Account listed BUT NOT accessible to anyone who is logged into TwistraNet. Must be in network to see it.",
        can_view:           (authenticated, ),
    },
    {
        "id":               "private",
        "name":             "Private, unsearchable account (except for administrators)",
        "description":      "Ghost account.",
        can_view:           (administrator, ),
    },
))

# Community templates
community_templates = PermissionTemplate((
    {
        "id":               "workgroup",
        "name":             "Workgroup", 
        "description":      """
                            A usually small community where all people want to work together.
                            Members have a very high autonomy level and can do many things on their own.
                            Content is usually restricted to members only.
                            """,
        can_list:           (authenticated, ),
        can_view:           (community_member, ),
        can_list_members:   (authenticated, ),
        can_publish:        (community_member, ),
        can_join:           (community_member, ),
        can_leave:          (community_member, ),
    },
    {
        "id":               "ou",
        "name":             "Company Service or Division",
        "description":      """
                            A great way of managing a service or division communication for a SBE.
                            Content is public and discussable, membership is managed by the application administrators only.
                            """,
        can_list:           (authenticated, ),
        can_view:           (authenticated, ),
        can_list_members:   (authenticated, ),
        can_publish:        (community_manager, ),
        can_join:           (community_manager, ),
        can_leave:          (administrator, ),
    },
    {
        "id":               "interest",
        "name":             "Interest group",
        "description":      """
                            A free interest group with free join and publication rules.
                            Very useful for extra-professionnal communities.
                            """,
        can_list:           (authenticated, ),
        can_view:           (authenticated, ),
        can_list_members:   (authenticated, ),
        can_publish:        (community_member, ),
        can_join:           (authenticated, ),
        can_leave:          (community_member, ),
    },
    {
        "id":               "blog",
        "name":             "Blog",
        "description":      """
                            The way a blog usually works: PUBLIC (even for anonymous!) content,
                            community managers as main editors, plus a few contributors who can join the blog.
                            """,
        can_list:           (anonymous, ),
        can_view:           (anonymous, ),
        can_list_members:   (anonymous, ),
        can_publish:        (community_member, ),
        can_join:           (community_manager, ),
        can_leave:          (community_member, ),
    },
    {
        "id":               "darkroom",
        "name":             "Dark room",
        "description":      """
                            A community in which members do not know each other.
                            Useful for a customer community where you want to maintain a little privacy between users.
                            Don't forget to mark your users as 'unlisted' to ensure complete isolation.
                            Content is usually private to the group.
                            """,
        can_list:           (community_member, ),
        can_view:           (community_member, ),
        can_list_members:   (community_manager, ),
        can_publish:        (community_manager, ),
        can_join:           (community_manager, ),
        can_leave:          (community_manager, ),
    },
))
