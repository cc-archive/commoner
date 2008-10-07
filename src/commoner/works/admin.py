from django.contrib import admin
from commoner.works.models import Registration, Feed
from commoner.works.models import Work, Constraint


class RegistrationAdmin(admin.ModelAdmin):
    pass

admin.site.register(Registration, RegistrationAdmin)

class FeedAdmin(admin.ModelAdmin):
    pass

admin.site.register(Feed, FeedAdmin)

class ConstraintAdmin(admin.TabularInline):
    model=Constraint

class WorkAdmin(admin.ModelAdmin):
    inlines = [ConstraintAdmin]

admin.site.register(Work, WorkAdmin)
