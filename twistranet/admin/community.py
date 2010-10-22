from twistranet.models.community import Community, CommunityMembership
from django.contrib import admin

class CommunityMembershipInline(admin.TabularInline):
    model = CommunityMembership
    extra = 1

class CommunityAdmin(admin.ModelAdmin):
    inlines = (CommunityMembershipInline,)


# not so easy ;-)
# admin.site.register(Community, CommunityAdmin)
admin.site.register(Community)
