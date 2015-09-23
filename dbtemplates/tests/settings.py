DBTEMPLATES_CACHE_BACKEND = 'dummy://'

DATABASE_ENGINE = 'sqlite3'
# SQLite does not support removing unique constraints (see #28)
SOUTH_TESTS_MIGRATE = False

SITE_ID = 1

SECRET_KEY = 'something-something'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'dbtemplates',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'loaders': (
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                'django.template.loaders.eggs.Loader',
                'dbtemplates.loader.Loader'
            )
        },
    },
]
