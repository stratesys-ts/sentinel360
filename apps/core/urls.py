from django.urls import path
from django.contrib.auth.views import LogoutView
from django.views.generic import RedirectView
from .views import (
    CustomLoginView,
    DashboardView,
    portal_login,
    portal_dashboard,
    logout_view,
    InternalUserListView,
    ExternalUserListView,
    ExternalUserCreateView,
    InternalUserCreateView,
    FAQView,
    ProfileView,
    SettingsView,
    GlobalSearchView,
    ForcePasswordChangeView,
)

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('portal/login/', portal_login, name='portal_login'),
    path('logout/', logout_view, name='logout'),
    path('', DashboardView.as_view(), name='dashboard'),
    path('faq/', FAQView.as_view(), name='faq'),
    path('perfil/', ProfileView.as_view(), name='profile'),
    path('configuracoes/', SettingsView.as_view(), name='settings'),
    path('search/', GlobalSearchView.as_view(), name='search'),
    path('portal/', portal_dashboard, name='portal_dashboard'),
    path('redefinir-senha/', ForcePasswordChangeView.as_view(), name='force_password_change'),
    path('forcar-troca/', RedirectView.as_view(pattern_name='core:force_password_change', permanent=True)),
    path('users/internal/', InternalUserListView.as_view(), name='internal_user_list'),
    path('users/internal/add/', InternalUserCreateView.as_view(), name='internal_user_add'),
    path('users/external/', ExternalUserListView.as_view(), name='external_user_list'),
    path('users/external/add/', ExternalUserCreateView.as_view(), name='external_user_add'),
]
