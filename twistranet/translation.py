"""
This module enables model translation for all twistranet base classes.
"""
from modeltranslation.translator import translator, TranslationOptions
from twistranet.twistapp import Twistable, Account, Content, Community, \
    GlobalCommunity, AdminCommunity, SystemAccount, UserAccount, Resource
from twistranet.content_types import Document, StatusUpdate, Comment

# (oh, by the way, 'TO' stands for TranslationOptions)

# Classic twist objects
class _TwistableTO(TranslationOptions):
    fields = ('title', 'description',)
translator.register(Twistable, _TwistableTO)

# Accounts and derived objects
class _AccountTO(TranslationOptions):
    fields = _TwistableTO.fields
translator.register(Account, _AccountTO)

class _SystemAccountTO(TranslationOptions):
    fields = _AccountTO.fields
translator.register(SystemAccount, _SystemAccountTO)

class _UserAccountTO(TranslationOptions):
    fields = _AccountTO.fields
translator.register(UserAccount, _UserAccountTO)

class _CommunityTO(TranslationOptions):
    fields = _AccountTO.fields
translator.register(Community, _CommunityTO)

class _GlobalCommunityTO(TranslationOptions):
    fields = _CommunityTO.fields + ('site_name', 'baseline', )
translator.register(GlobalCommunity, _GlobalCommunityTO)

class _AdminCommunityTO(TranslationOptions):
    fields = _CommunityTO.fields
translator.register(AdminCommunity, _AdminCommunityTO)
    
# Content and like
class _ResourceTO(TranslationOptions):
    fields = _TwistableTO.fields
translator.register(Resource, _ResourceTO)

class _ContentTO(TranslationOptions):
    fields = _TwistableTO.fields
translator.register(Content, _ContentTO)


# Content types
class _DocumentTO(TranslationOptions):
    fields = _ContentTO.fields + ('text', )
translator.register(Document, _DocumentTO)

class _StatusUpdateTO(TranslationOptions):
    fields = _ContentTO.fields
translator.register(StatusUpdate, _StatusUpdateTO)

class _CommentTO(TranslationOptions):
    fields = _ContentTO.fields
translator.register(Comment, _CommentTO)


