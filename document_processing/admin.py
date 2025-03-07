from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'document_type', 'processing_status', 'created_at')
    list_filter = ('document_type', 'processing_status')
    search_fields = ('title', 'extracted_text')
    readonly_fields = ('extracted_text', 'metadata', 'processing_status', 'error_message', 'created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('title', 'file', 'document_type')
        }),
        ('Processing Information', {
            'fields': ('processing_status', 'error_message')
        }),
        ('Extracted Content', {
            'fields': ('extracted_text', 'metadata')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    ) 