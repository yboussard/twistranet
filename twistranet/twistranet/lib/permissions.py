from roles import *

# Basic permissions
# TODO: List which roles are possible for each permission kind.
can_list = "can_list"           # BASIC ACCESS PERMISSION. You won't be able to do anything if you can't list an object.
can_view = "can_view"
can_edit = "can_edit"           # One who can edit can also delete
can_list_members = "can_list_members"
can_publish = "can_publish"
can_join = "can_join"
can_leave = "can_leave"
can_create = "can_create"
can_delete = "can_delete"

# Special role arrangements
class PermissionTemplate:
    """
    Permission template helper.
    XXX TODO: Avoid value modification when for example you do perm[4]['can_view'] = True !
    """
    def __init__(self, perm_tuple, default_index = 0):
        """
        See content_permissions_templates for an example of what perm_tuple should look like.
        """
        self.perm_tuple = perm_tuple
        self.default_index = default_index
        self.perm_dict = dict()
        [ self.perm_dict.__setitem__(v['id'], v) for v in perm_tuple ]
        
    def get_choices(self):
        """
        Return a choice tuple suitable for the model
        """
        return [ (t["id"], t["name"], ) for t in self.perm_tuple ]
        
    def get_default(self):
        return self.perm_tuple[self.default_index]["id"]
        
    def permissions(self):
        return tuple(self.perm_tuple)
        
    def get(self, id_):
        return self.perm_dict[id_]
        
        
# Regular content permissions
content_templates = PermissionTemplate((
    {
        "id":               "public",
        "name":             "Public content", 
        "description":      "Content visible to anyone who can view this page.",
        can_list:           public,
        can_view:           public,
        can_edit:           owner,
        can_delete:         owner,
    },
    {
        "id":               "network",
        "name":             "Network-only content",
        "description":      """
                            Content visible only to my network.
                            For community content, use 'Members-only content' instead.
                            """,
        can_list:           network,
        can_view:           network,
        can_edit:           owner,
        can_delete:         owner,
        "disabled_for_community":   True,
    },
    {
        "id":               "members",
        "name":             "Members-only content",
        "description":      """
                            Content visible only to community members.
                            For regular wall content, use 'Network-only content' instead.
                            """,
        can_list:           network,
        can_view:           network,
        can_edit:           owner,
        can_delete:         owner,
        "disabled_for_useraccount":  True,
    },
    {
        "id":               "private",
        "name":             "Private",
        "description":      "Content visible only for the author",
        can_list:           owner,
        can_view:           owner,
        can_edit:           owner,
        can_delete:         owner,
    },
))

# Ephemeral (ie. non-editable after writing) content permissions
ephemeral_templates = PermissionTemplate((
    {
        "id":               "public",
        "name":             "Public content", 
        "description":      "Content visible to anyone who can view this page.",
        can_list:           public,
        can_view:           public,
        can_edit:           system,
        can_delete:         owner,
    },
    {
        "id":               "network",
        "name":             "Network-only content",
        "description":      """
                            Content visible only to my network.
                            For community content, use 'Members-only content' instead.
                            """,
        can_list:           network,
        can_view:           network,
        can_edit:           system,
        can_delete:         owner,
        "disabled_for_community":   True,
    },
    {
        "id":               "members",
        "name":             "Members-only content",
        "description":      """
                            Content visible only to community members.
                            For regular wall content, use 'Network-only content' instead.
                            """,
        can_list:           network,
        can_view:           network,
        can_edit:           system,
        can_delete:         owner,
        "disabled_for_useraccount":  True,
    },
    {
        "id":               "private",
        "name":             "Private",
        "description":      "Content visible only for the author (only used for private notifications)",
        can_list:           owner,
        can_view:           owner,
        can_edit:           owner,
        can_delete:         owner,
        "disabled_for_useraccount":     True,
        "disabled_for_community":       True,
    },
))

# XXX TODO: Have some specific stuff for each account type. Not an easy problem to overload the choices field...
account_templates = PermissionTemplate((
    # User account templates
    {
        "id":               "public",
        "name":             "Public account",
        "description":      "Account listed and accessible to anyone who has access to TwistraNet (public if TwistraNet is in internet mode).",
        can_view:           public,
        can_list:           public,
        can_publish:        network,
        can_edit:           owner,
    },
    {
        "id":               "intranet",
        "name":             "Restricted intranet account",
        "description":      "Account listed and accessible to anyone who is logged into to TwistraNet.",
        can_view:           network,
        can_list:           network,
        can_publish:        network,
        can_edit:           owner,
    },
    {
        "id":               "listed",
        "name":             "Private but searchable", 
        "description":      "Account listed BUT NOT necessarily accessible to anyone who is logged into TwistraNet: Must be in his network to see it.",
        can_view:           network,
        can_list:           public,
        can_publish:        network,
        can_edit:           owner,
    },
    {
        "id":               "private",
        "name":             "Private, unsearchable account (except for administrators and ppl in account's network). They cannot write on their wall, only on the communities they're in.",
        "description":      "Ghost account.",
        can_view:           network,
        can_list:           network,
        can_publish:        network,
        can_edit:           owner,
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
        # can_create:         (administrator, ),
        can_list:           public,
        can_view:           network,
        can_list_members:   public,
        can_edit:           managers,
        can_delete:         owner,
        can_publish:        network,
        can_join:           network,
        can_leave:          network,
    },
    {
        "id":               "ou",
        "name":             "Company Service or Division",
        "description":      """
                            A great way of managing a service or division communication for a SBE.
                            Content is public and discussable, membership is managed by the application administrators only.
                            """,
        # can_create:         (administrator, ),
        can_list:           public,
        can_view:           public,
        can_list_members:   public,
        can_edit:           managers,
        can_delete:         owner,
        can_publish:        public,
        can_join:           managers,
        can_leave:          managers,
    },
    {
        "id":               "private",
        "name":             "Private", 
        "description":      """
                            A private community, visible only to its members but ruled like a workgroup otherwise.
                            """,
        # can_create:         (administrator, ),
        can_list:           network,
        can_view:           network,
        can_list_members:   network,
        can_edit:           managers,
        can_delete:         owner,
        can_publish:        network,
        can_join:           managers,
        can_leave:          network,
    },
    {
        "id":               "interest",
        "name":             "Interest group",
        "description":      """
                            A free interest group with free join and publication rules.
                            Very useful for extra-professionnal communities.
                            All authenticated people can create an interest group.
                            """,
        # can_create:         public,
        can_list:           public,
        can_view:           public,
        can_list_members:   public,
        can_edit:           managers,
        can_delete:         owner,
        can_publish:        public,
        can_join:           public,
        can_leave:          network,
    },
    {
        "id":               "blog",
        "name":             "Blog",
        "description":      """
                            The way a blog usually works: PUBLIC (even for anonymous if the site is opened) content,
                            community managers as main editors, plus a few contributors who can join the blog.
                            """,
        # can_create:         (administrator, ),
        can_list:           public,
        can_view:           public,
        can_list_members:   public,
        can_edit:           managers,
        can_delete:         owner,
        can_publish:        public,
        can_join:           managers,
        can_leave:          network,
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
        # can_create:         (administrator, ),
        can_list:           network,
        can_view:           network,
        can_list_members:   managers,
        can_edit:           managers,
        can_delete:         owner,
        can_publish:        network,
        can_join:           managers,
        can_leave:          managers,
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
        can_list:           network,
        can_view:           network,
        can_list_members:   network,
        can_edit:           managers,
        can_delete:         system,
        can_publish:        managers,
        can_join:           system,             # Mandatory for global community.
        can_leave:          system,             # Mandatory for global community.
    },
    {
        "id":               "extranet",
        "name":             "Extranet: Access restricted to members, they must not know each other.",
        "description":      """
                            Use this to have your TwistraNet site opened to your customers and partners.
                            Customers must not see each other. So they can't be listed in there.
                            """,
        can_list:           network,
        can_view:           network,
        can_list_members:   managers,
        can_edit:           managers,
        can_delete:         system,
        can_publish:        managers,
        can_join:           system,             # Mandatory for global community.
        can_leave:          system,             # Mandatory for global community.
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
        can_list:           public,
        can_view:           public,
        can_list_members:   network,
        can_edit:           managers,
        can_delete:         system,
        can_publish:        managers,
        can_join:           system,             # Mandatory for global community.
        can_leave:          system,             # Mandatory for global community.
    },
))





