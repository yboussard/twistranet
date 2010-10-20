from twistranet.models import UserAccount, AccountLanguage
from django.contrib import admin



class AccountLanguageInline(admin.StackedInline):
    model = AccountLanguage
    extra = 3

class UserAccountAdmin(admin.ModelAdmin):
    inlines = [AccountLanguageInline]

admin.site.register(UserAccount, UserAccountAdmin)
