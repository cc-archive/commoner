from django.contrib import admin
from commoner.content.models import Content

class ContentAdmin(admin.ModelAdmin):
    pass

admin.site.register(Content, ContentAdmin)
