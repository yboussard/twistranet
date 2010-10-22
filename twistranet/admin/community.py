from twistranet.models.community import GlobalCommunity, CommunityMembership
from django.contrib import admin

class CommunityMembershipInline(admin.TabularInline):
    model = CommunityMembership
    extra = 1

class GlobalCommunityAdmin(admin.ModelAdmin):
    inlines = (CommunityMembershipInline,)


# not so easy ;-)
# admin.site.register(Community, CommunityAdmin)
admin.site.register(GlobalCommunity)
