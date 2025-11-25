"""
Django settings for erp_core project.
"""

from pathlib import Path
import os
from django.urls import reverse_lazy
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
DEBUG = os.getenv('DEBUG', 'False') == 'True'

SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = 'django-insecure-dev-key'
    else:
        raise ValueError("SECRET_KEY environment variable is required in production")

allowed_hosts_env = os.getenv('ALLOWED_HOSTS', '')
if allowed_hosts_env:
    ALLOWED_HOSTS = [host for host in allowed_hosts_env.split(',') if host]
elif DEBUG:
    ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
else:
    raise ValueError("ALLOWED_HOSTS environment variable is required in production")

# Application definition

INSTALLED_APPS = [
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'drf_yasg',
    
    # Local apps
    'apps.core',
    'apps.helpdesk',
    'apps.timesheet',
    'apps.projects',
    'apps.api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.api.middleware.ApiRequestLogMiddleware',
]

ROOT_URLCONF = 'erp_core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.module_access',
            ],
        },
    },
]

WSGI_APPLICATION = 'erp_core.wsgi.application'

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3'),
        conn_max_age=600
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'core.User'

# Login/Logout
LOGIN_URL = 'core:login'
LOGIN_REDIRECT_URL = 'core:dashboard'
LOGOUT_REDIRECT_URL = 'core:login'

UNFOLD = {
    "SITE_TITLE": "ERP Admin",
    "SITE_HEADER": "Administração do ERP",
    "SITE_SUBHEADER": "Controles de acesso, projetos, timesheets e helpdesk",
    "SITE_URL": "/",
    "SITE_LOGO": {
        "light": "/static/img/stratesys-logo-light.svg",
        "dark": "/static/img/stratesys-logo-dark.svg",
    },
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SIDEBAR": {
        "show_search": True,
        "command_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": "Início",
                "items": [
                    {
                        "title": "Dashboard",
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": "Pessoas e acessos",
                "collapsible": True,
                "items": [
                    {
                        "title": "Usuários",
                        "icon": "badge",
                        "link": reverse_lazy("admin:core_user_changelist"),
                    },
                    {
                        "title": "Usuários internos",
                        "icon": "groups",
                        "link": reverse_lazy("admin:core_internaluser_changelist"),
                    },
                    {
                        "title": "Usuários externos",
                        "icon": "group_add",
                        "link": reverse_lazy("admin:core_externaluser_changelist"),
                    },
                    {
                        "title": "Grupos",
                        "icon": "shield_person",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                    {
                        "title": "Módulos por grupo",
                        "icon": "view_timeline",
                        "link": reverse_lazy("admin:core_groupmoduleaccess_changelist"),
                    },
                ],
            },
            {
                "title": "Projetos",
                "collapsible": True,
                "items": [
                    {
                        "title": "Projetos",
                        "icon": "work",
                        "link": reverse_lazy("admin:projects_project_changelist"),
                    },
                    {
                        "title": "Tarefas",
                        "icon": "task_alt",
                        "link": reverse_lazy("admin:projects_task_changelist"),
                    },
                    {
                        "title": "Centros de custo",
                        "icon": "account_balance",
                        "link": reverse_lazy("admin:projects_costcenter_changelist"),
                    },
                ],
            },
            {
                "title": "Timesheet",
                "collapsible": True,
                "items": [
                    {
                        "title": "Folhas de horas",
                        "icon": "calendar_month",
                        "link": reverse_lazy("admin:timesheet_timesheet_changelist"),
                    },
                    {
                        "title": "Lançamentos",
                        "icon": "schedule",
                        "link": reverse_lazy("admin:timesheet_timeentry_changelist"),
                    },
                    {
                        "title": "Atividades",
                        "icon": "checklist",
                        "link": reverse_lazy("admin:timesheet_activity_changelist"),
                    },
                ],
            },
            {
                "title": "Helpdesk",
                "collapsible": True,
                "items": [
                    {
                        "title": "Tickets",
                        "icon": "support_agent",
                        "link": reverse_lazy("admin:helpdesk_ticket_changelist"),
                    },
                    {
                        "title": "Categorias",
                        "icon": "category",
                        "link": reverse_lazy("admin:helpdesk_category_changelist"),
                    },
                ],
            },
            {
                "title": "API",
                "collapsible": True,
                "items": [
                    {
                        "title": "Aplicações de Integração",
                        "icon": "key",
                        "link": reverse_lazy("admin:api_integrationapp_changelist"),
                    },
                    {
                        "title": "Webhooks",
                        "icon": "share",
                        "link": reverse_lazy("admin:api_webhooksubscription_changelist"),
                    },
                    {
                        "title": "Logs de Requisição",
                        "icon": "rule_folder",
                        "link": reverse_lazy("admin:api_apirequestlog_changelist"),
                    },
                    {
                        "title": "Entregas de Webhook",
                        "icon": "receipt_long",
                        "link": reverse_lazy("admin:api_webhookdeliverylog_changelist"),
                    },
                ],
            },
        ],
    },
    "COMMAND": {
        "search_models": True,
        "show_history": True,
    },
}


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.server': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.staticfiles': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# REST Framework settings
REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_CLASSES": ["apps.api.throttling.APIKeyRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {"api": "100/min"},
    "DEFAULT_PERMISSION_CLASSES": [],
    "DEFAULT_AUTHENTICATION_CLASSES": [],
}

