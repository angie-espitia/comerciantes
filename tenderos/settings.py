import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 's&33@8ot(aqyv3d@e@zo8o9q)=6mebgjz28)hc_ngn420kvvns'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
    'main.templatetags'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'tenderos.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'main/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'tenderos.wsgi.application'

### mysql

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'bd_tenderos',
#         'USER': 'root',
#         'PASSWORD': '1234567',
#         'HOST': 'localhost',
#         'PORT': '3306',
#         'STORAGE_ENGINE': 'INNODB'
#     }
# }

### herokuostgres

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
         'NAME': 'd9f12ct43vnd4f',
         'USER': 'yapciqupdzcbuz',
         'PASSWORD': 'abc4eac788084f581d02db55ff8f32ad293606fe1eee670f341608c0be58abf5',
         'HOST': 'ec2-54-172-17-119.compute-1.amazonaws.com',
         'PORT': '5432',
    }
}

### db para sqlite

# DATABASES = {
#    'default': {
#      'ENGINE': 'django.db.backends.sqlite3',
#      'NAME': 'db_tenderos',
#    }
# }

# DATABASES = {
#     'default': dj_database_url.config{
#         default=config('DATABASE_URL')
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

#URL para acceder a los archivos estaticos
STATIC_URL = '/static/'
STATIC_ROOT = 'staticfiles'

#Directorio donde se almacenaran archivos css
STATICFILES_DIRS = [ BASE_DIR + '/static' ]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

MEDIA_URL = '/media/'

STATIC_ROLS = {'administrativo': 1, 'propietario_negocio': 2, 'empleado_negocio': 3}

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Cargue para heroku
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
