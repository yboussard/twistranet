"""
Twistranet content / account / ressource scope management.

Just global vars by now but we can imagine some kind of a registry
"""

ACCOUNTSCOPE_ANONYMOUS = "anonymous"            # All anonymous can access it
ACCOUNTSCOPE_AUTHENTICATED = "authenticated"    # All auth. can access it
ACCOUNTSCOPE_MEMBERS = "members"                # All members can access it
ACCOUNTSCOPE_PRIVATE = "private"                # Invisible (kinda)
CONTENTSCOPE_NETWORK = "network"                # All ppl in account network can access it
CONTENTSCOPE_PUBLIC = "public"                  # All ppl who has access to the account can access it
CONTENTSCOPE_PRIVATE = "private"                # Unvisible outside the account itself

ACCOUNT_SCOPES = (
    (ACCOUNTSCOPE_PRIVATE, "Private, invisible account", ),
    (ACCOUNTSCOPE_AUTHENTICATED, "An account visible for logged-in users", ),
    (ACCOUNTSCOPE_ANONYMOUS, "An account visible by anonymous users", ),
)

COMMUNITY_SCOPES = (
    (ACCOUNTSCOPE_MEMBERS, "Private community visible by its members only", ),
    (ACCOUNTSCOPE_AUTHENTICATED, "A regular intranet community visible by logged-in users", ),
    (ACCOUNTSCOPE_ANONYMOUS, "Public community visible by anonymous users", ),
    )
COMMUNITY_SCOPE_IDS = [ s[0] for s in COMMUNITY_SCOPES ]


CONTENT_SCOPES = (
    (CONTENTSCOPE_PUBLIC,      "This content is visible by anyone who has access to the publisher.", ),
    (CONTENTSCOPE_NETWORK,     "This content is visible only by the publisher's network.", ),
    (CONTENTSCOPE_PRIVATE,     "This content is private, only the author can see it.", ),
)

CONTENT_SCOPE_IDS = [ t[0] for t in CONTENT_SCOPES ]

