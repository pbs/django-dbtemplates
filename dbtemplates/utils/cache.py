from django.core.cache import caches
from django.template.defaultfilters import slugify
from dbtemplates.conf import settings


def get_cache_backend():
    return caches[settings.DBTEMPLATES_CACHE_BACKEND]

cache = get_cache_backend()
key_format = 'dbtemplates::{template_name}'


def get_cache_key(template_name):
    return key_format.format(
        template_name=slugify(template_name)
    )


def fetch_template_from_cache(template_name, satisfies_permissions):
    """Returns a template_name from the cache conditionaly."""
    if cache:
        key = get_cache_key(template_name)
        cache_value = cache.get(key)
        if satisfies_permissions(cache_value):
            return cache_value.get('content')


def add_template_to_cache(instance, **kwargs):
    """
    Called via Django's signals to cache the templates, if the template
    in the database was added or changed.
    """
    remove_cached_template(instance)
    key = get_cache_key(instance.name)
    value = {
        'content': instance.content,
        'sites':  set(instance.sites.values_list('pk', flat=True))
    }
    if cache:
        cache_timeout = getattr(settings, 'DBTEMPLATES_CACHE_TIMEOUT')
        cache.set(key, value, cache_timeout)


def remove_cached_template(instance, **kwargs):
    """
    Called via Django's signals to remove cached templates, if the template
    in the database was changed or deleted.
    """
    cache.delete(get_cache_key(instance.name))
