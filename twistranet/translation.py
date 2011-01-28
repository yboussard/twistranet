"""
This module enables model translation for all twistranet base classes.
"""
from modeltranslation.translator import translator, TranslationOptions
from twistranet.twistapp import Twistable, Account, Content, Community, \
    GlobalCommunity, AdminCommunity, SystemAccount, UserAccount

# TO stands for TranslationOptions

class _TwistableTO(TranslationOptions):
    fields = ('title', 'description',)

class _CommunityTO(TranslationOptions):
    fields = ('title', 'description',)

class _AccountTO(TranslationOptions):
    fields = ('title', 'description',)

class _ContentTO(TranslationOptions):
    fields = ('title', 'description',)
    
class _GlobalCommunityTO(TranslationOptions):
    fields = ('title', 'description',)

class _AdminCommunityTO(TranslationOptions):
    fields = ('title', 'description',)
    
class _SystemAccountTO(TranslationOptions):
    fields = ('title', 'description',)

class _UserAccountTO(TranslationOptions):
    fields = ('title', 'description',)

translator.register(Twistable, _TwistableTO)
translator.register(Community, _CommunityTO)
translator.register(Account, _AccountTO)
translator.register(Content, _ContentTO)
translator.register(GlobalCommunity, _GlobalCommunityTO)
translator.register(AdminCommunity, _AdminCommunityTO)
translator.register(SystemAccount, _SystemAccountTO)
translator.register(UserAccount, _UserAccountTO)

