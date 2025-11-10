from django.contrib import admin
from engine.models.module import Module

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug','version', 'is_active', 'installed_at', 'updated_at')
    list_editable = ('is_active',)
    list_filter = ('is_active',)
    search_fields = ('name', 'slug')  

