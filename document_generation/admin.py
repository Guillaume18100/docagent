from django.contrib import admin
from .models import DocumentTemplate, GeneratedDocument

@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'template_content')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        ('Template Content', {
            'fields': ('template_content', 'variables')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(GeneratedDocument)
class GeneratedDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'template', 'generation_status', 'created_at')
    list_filter = ('generation_status', 'template')
    search_fields = ('title', 'content')
    readonly_fields = ('generation_status', 'error_message', 'created_at', 'updated_at')
    filter_horizontal = ('source_documents',)
    fieldsets = (
        (None, {
            'fields': ('title', 'template')
        }),
        ('Content', {
            'fields': ('content', 'file')
        }),
        ('Generation Information', {
            'fields': ('parameters', 'source_documents', 'generation_status', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    ) 