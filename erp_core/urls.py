from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Inclui o app core com namespace 'core'
    path('', include(('apps.core.urls', 'core'), namespace='core')),
    # New unified issues routes
    path('issues/helpdesk/', include(('apps.helpdesk.urls', 'helpdesk'), namespace='helpdesk')),
    path('issues/projects/', include(('apps.projects.urls', 'projects'), namespace='projects')),
    # Legacy paths redirect to new issues URLs
    re_path(r'^helpdesk/(?P<path>.*)$', RedirectView.as_view(url='/issues/helpdesk/%(path)s', permanent=True)),
    path('helpdesk/', RedirectView.as_view(url='/issues/helpdesk/', permanent=True)),
    re_path(r'^projects/(?P<path>.*)$', RedirectView.as_view(url='/issues/projects/%(path)s', permanent=True)),
    path('projects/', RedirectView.as_view(url='/issues/projects/', permanent=True)),
    path('timesheet/', include('apps.timesheet.urls')),
    path('api/', include(('apps.api.urls', 'api'), namespace='api')),
]

admin.site.site_header = "Administração do ERP"
admin.site.site_title = "ERP Admin"
admin.site.index_title = "Painel administrativo"
