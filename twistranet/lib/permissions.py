from roles import *

# Basic permissions
# TODO: List which roles are possible for each permission kind.
can_view = "can_view"
can_edit = "can_edit"           # One who can edit can also delete
can_list = "can_list"
can_list_members = "can_list_members"
can_publish = "can_publish"
can_join = "can_join"
can_leave = "can_leave"
can_create = "can_create"

can_delete = can_edit

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
        
        
# Regular content permissions
content_templates = PermissionTemplate((
    {
        "id":               "public",
        "name":             "Public content", 
        "description":      "Content visible to anyone who can view this page.",
        can_view:           (content_public, ),
        can_edit:           (content_author, ),
    },
    {
        "id":               "network",
        "name":             "Network-only content",
        "description":      """
                            Content visible only to my network.
                            For community content, use 'Members-only content' instead.
                            """,
        can_view:           (content_network, ),
        can_edit:           (content_author, ),
    },
    {
        "id":               "members",
        "name":             "Members-only content",
        "description":      """
                            Content visible only to community members.
                            For regular wall content, use 'Network-only content' instead.
                            """,
        can_view:           (content_community_member, ),
        can_edit:           (content_author, ),
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
        "id":               "public",
        "name":             "Public account",
        "description":      "Account listed and accessible to anyone who has access to TwistraNet (public if TwistraNet is in internet mode).",
        can_view:           (anonymous, ),
        can_list:           (anonymous, ),
        can_publish:        (owner, ),
        can_edit:           (owner, administrator, ),
    },
    {
        "id":               "intranet",
        "name":             "Restricted intranet account",
        "description":      "Account listed and accessible to anyone who is logged into to TwistraNet.",
        can_view:           (authenticated, ),
        can_list:           (authenticated, ),
        can_publish:        (owner, administrator, ),
        can_edit:           (owner, administrator, ),
    },
    {
        "id":               "listed",
        "name":             "Private but searchable", 
        "description":      "Account listed BUT NOT necessarily accessible to anyone who is logged into TwistraNet: Must be in his network to see it.",
        can_view:           (account_network, ),
        can_list:           (authenticated, ),
        can_publish:        (owner, administrator, ),
        can_edit:           (owner, administrator, ),
    },
    {
        "id":               "private",
        "name":             "Private, unsearchable account (except for administrators and ppl in account's network)",
        "description":      "Ghost account.",
        can_view:           (account_network, ),
        can_list:           (account_network, ),
        can_publish:        (owner, administrator, ),
        can_edit:           (owner, administrator, ),
    },
))

# Community templates
# Default is that, except interest groups, communities must be created by an admin 
community_templates = PermissionTemplate((
    {
        "id":               "workgroup",
        "name":             "Workgroup", 
        "description":      """
                            A (often small) community where all people want to work together.
                            Members have a very high autonomy level and can do many things on their own.
                            Content is usually restricted to members only.
                            """,
        can_create:         (administrator, ),
        can_list:           (authenticated, ),
        can_view:           (community_member, ),
        can_list_members:   (authenticated, ),
        can_edit:           (community_manager, ),
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
        can_create:         (administrator, ),
        can_list:           (authenticated, ),
        can_view:           (authenticated, ),
        can_list_members:   (authenticated, ),
        can_edit:           (community_manager, ),
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
                            All authenticated people can create an interest group.
                            """,
        can_create:         (authenticated, ),
        can_list:           (authenticated, ),
        can_view:           (authenticated, ),
        can_list_members:   (authenticated, ),
        can_edit:           (community_manager, ),
        can_publish:        (community_member, ),
        can_join:           (authenticated, ),
        can_leave:          (community_member, ),
    },
    {
        "id":               "blog",
        "name":             "Blog",
        "description":      """
                            The way a blog usually works: PUBLIC (even for anonymous if the site is opened) content,
                            community managers as main editors, plus a few contributors who can join the blog.
                            """,
        can_create:         (administrator, ),
        can_list:           (anonymous, ),
        can_view:           (anonymous, ),
        can_list_members:   (anonymous, ),
        can_edit:           (community_manager, ),
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
        can_create:         (administrator, ),
        can_list:           (community_member, ),
        can_view:           (community_member, ),
        can_list_members:   (community_manager, ),
        can_edit:           (community_manager, ),
        can_publish:        (community_manager, ),
        can_join:           (community_manager, ),
        can_leave:          (community_manager, ),
    },
))

# Global community templates.
global_community_templates = PermissionTemplate((
    {
        "id":               "intranet",
        "name":             "Intranet: Access restricted to logged-in users only.",
        "description":      """
                            Use this to have your TwistraNet site opened only to logged-in users.
                            Everybody is listed, although some accounts can be private.
                            This is usually how an intranet site works.
                            """,
        can_list:           (authenticated, ),
        can_view:           (authenticated, ),
        can_list_members:   (authenticated, ),
        can_publish:        (community_manager, ),
        can_join:           (system, ),             # Mandatory for global community.
        can_leave:          (system, ),             # Mandatory for global community.
    },
    {
        "id":               "extranet",
        "name":             "Extranet: Access restricted to members, they must not know each other.",
        "description":      """
                            Use this to have your TwistraNet site opened to your customers and partners.
                            Customers must not see each other. So they can't be listed in there.
                            """,
        can_list:           (authenticated, ),
        can_view:           (authenticated, ),
        can_list_members:   (community_manager, ),
        can_publish:        (community_manager, ),
        can_join:           (system, ),             # Mandatory for global community.
        can_leave:          (system, ),             # Mandatory for global community.
    },
    {
        "id":               "internet",
        "name":             "Internet: Opened to the World.",
        "description":      """
                            Want to open your community the the World? That's what this is for.
                            If you have an association, a (possibly open-source ;)) community project
                            or just want your company to be reachable, keep the content opened.
                            Of course, anonymous people won't be able to do anything but read authorized stuff.
                            
                            Global community content will still be restricted to auth people.
                            """,
        can_list:           (anonymous, ),
        can_view:           (authenticated, ),
        can_list_members:   (authenticated, ),
        can_publish:        (community_manager, ),
        can_join:           (system, ),             # Mandatory for global community.
        can_leave:          (system, ),             # Mandatory for global community.
    },
))





