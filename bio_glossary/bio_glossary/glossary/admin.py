from django.contrib import admin
from .models import Term, UserTest, UserResponse


admin.site.register(UserTest)
admin.site.register(UserResponse)
@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('term', 'theme_display', 'definition_short', 'is_approved')
    list_editable = ('is_approved',)
    list_filter = ('is_approved', 'theme')
    search_fields = ('term', 'definition')
    actions = ['approve_selected']

    def theme_display(self, obj):
        return obj.get_theme_display()
    theme_display.short_description = 'Тематика'

    def definition_short(self, obj):
        return f"{obj.definition[:50]}..." if len(obj.definition) > 50 else obj.definition
    definition_short.short_description = 'Определение'

    def approve_selected(self, request, queryset):
        queryset.update(is_approved=True)
    approve_selected.short_description = "Одобрить выбранные термины"