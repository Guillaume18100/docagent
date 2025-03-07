from django.contrib import admin
from .models import UserQuery, Conversation, Message

@admin.register(UserQuery)
class UserQueryAdmin(admin.ModelAdmin):
    list_display = ('query_text', 'created_at')
    search_fields = ('query_text',)
    filter_horizontal = ('related_documents',)
    readonly_fields = ('analyzed_result', 'created_at')
    fieldsets = (
        (None, {
            'fields': ('query_text', 'related_documents')
        }),
        ('Analysis Results', {
            'fields': ('analyzed_result',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [MessageInline]
    fieldsets = (
        (None, {
            'fields': ('title',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'role', 'content_preview', 'created_at')
    list_filter = ('role', 'conversation')
    search_fields = ('content',)
    readonly_fields = ('created_at',)
    
    def content_preview(self, obj):
        """Return a preview of the message content"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content' 