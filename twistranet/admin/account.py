from twistranet.models.account import Account, UserAccount, AccountLanguage
# from community import CommunityMembershipInline
# from relation import InitiatorInline, TargetInline
from django.contrib import admin

class AccountLanguageInline(admin.StackedInline):
    model = AccountLanguage
    extra = 1

class UserAccountAdmin(admin.ModelAdmin):
    pass
    # inlines = (AccountLanguageInline, CommunityMembershipInline, InitiatorInline, TargetInline)

admin.site.register(Account)
admin.site.register(UserAccount, UserAccountAdmin)
