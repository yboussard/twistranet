from twistranet.models.account import Account, UserAccount, AccountLanguage
from community import CommunityMembershipInline
from django.contrib import admin

class AccountLanguageInline(admin.StackedInline):
    model = AccountLanguage
    extra = 1

class UserAccountAdmin(admin.ModelAdmin):
    inlines = (AccountLanguageInline,CommunityMembershipInline,)

admin.site.register(UserAccount, UserAccountAdmin)
