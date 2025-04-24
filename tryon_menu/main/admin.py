from django.contrib import admin
from .models import  Model, ModelVersion, InputSet, Tryon, TryonBatch, PageLogs


@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    list_filter = ()
    search_fields = ('name', 'description')

@admin.register(ModelVersion)
class ModelVersionAdmin(admin.ModelAdmin):
    list_display = ('model', 'version', 'resolution', 'created_at')
    list_filter = ('model',)
    search_fields = ('version', 'description', 'model__name')

@admin.register(InputSet)
class InputSetAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'garment_image', 'model_image')

@admin.register(Tryon)
class TryonAdmin(admin.ModelAdmin):
    list_display = ('model_version', 'input_set', 'created_at')
    list_filter = ('model_version__model', 'model_version')
    search_fields = ('input_set__name', 'model_version__model__name', 'notes')

@admin.register(TryonBatch)
class TryonBatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')
    filter_horizontal = ('tryons',)

@admin.register(PageLogs)
class PageLogsAdmin(admin.ModelAdmin):
    list_display = ('url', 'accessed_at', 'user', 'ip_address')
    list_filter = ('user', 'ip_address')
    search_fields = ('url', 'user__username', 'ip_address')
    readonly_fields = ('user', 'ip_address', 'user_agent')
