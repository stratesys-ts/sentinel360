from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import Category, Comment, Ticket

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'sla_hours')
    search_fields = ('name',)
    ordering = ('name',)

class CommentInline(TabularInline):
    model = Comment
    extra = 0
    fields = ('author', 'content', 'attachment', 'is_internal', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(Ticket)
class TicketAdmin(ModelAdmin):
    list_display = (
        'id',
        'title',
        'priority',
        'status',
        'category',
        'project',
        'created_by',
        'assigned_to',
        'created_at',
    )
    list_filter = ('status', 'priority', 'category', 'project', 'assigned_to')
    search_fields = (
        'title',
        'description',
        'created_by__username',
        'assigned_to__username',
        'project__name',
    )
    autocomplete_fields = ('project', 'category', 'created_by', 'assigned_to')
    list_select_related = ('category', 'project', 'created_by', 'assigned_to')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CommentInline]
    list_per_page = 25
