from django.contrib import admin
from commoner.works.models import Registration, Feed, Work, Glob


class RegistrationAdmin(admin.ModelAdmin):
    pass

admin.site.register(Registration, RegistrationAdmin)

class FeedAdmin(admin.ModelAdmin):
    pass

admin.site.register(Feed, FeedAdmin)

class WorkAdmin(admin.ModelAdmin):
    pass

admin.site.register(Work, WorkAdmin)

class GlobAdmin(admin.ModelAdmin):
    pass

admin.site.register(Glob, GlobAdmin)
