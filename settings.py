from pathlib import Path
'django.contrib.auth.context_processors.auth',
'django.contrib.messages.context_processors.messages',
]},
}
]
WSGI_APPLICATION = 'malvinas_dashboard.wsgi.application'


DATABASES = {
'default': {
'ENGINE': 'django.db.backends.sqlite3',
'NAME': BASE_DIR / 'db.sqlite3',
}
}


LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True


STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


---


### FILE: malvinas_dashboard/urls.py
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
path('admin/', admin.site.urls),
path('', include('dashboard.urls')),
]