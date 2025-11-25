from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Inclui o app core com namespace 'core'
    path('', include(('apps.core.urls', 'core'), namespace='core')),
    path('helpdesk/', include('apps.helpdesk.urls')),
    path('timesheet/', include('apps.timesheet.urls')),
    path('projects/', include('apps.projects.urls')),
    path('api/', include(('apps.api.urls', 'api'), namespace='api')),
]

admin.site.site_header = "Administração do ERP"
admin.site.site_title = "ERP Admin"
admin.site.index_title = "Painel administrativo"
