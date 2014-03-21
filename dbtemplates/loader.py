from django.contrib.sites.models import Site
from django.db import router
from django.template import TemplateDoesNotExist

from dbtemplates.models import Template
from dbtemplates.utils.cache import (
    get_cache_key,
    add_template_to_cache,
    cache,
)
from django.template.loader import BaseLoader


class Loader(BaseLoader):
    """
    A custom template loader to load templates from the database.

    Tries to load the template from the dbtemplates cache backend specified
    by the DBTEMPLATES_CACHE_BACKEND setting. If it does not find a template
    it falls back to query the database field ``name`` with the template path
    and ``sites`` with the current site.
    """
    is_usable = True
    display_format = 'dbtemplates:{origin}:{template_name}:{domain}'

    def make_display_name(self, origin, template_name, domain):
        return self.display_format.format(
            origin=origin,
            template_name=template_name,
            domain=domain
        )

    def load_and_store_template(self, template_name, cache_key, site, **params):
        templates = Template.objects.filter(
            name__exact=template_name, **params).distinct()
        if not templates:
            raise Template.DoesNotExist(template_name)
        #template names are unique => there should always be a single template returned
        template = templates[0]
        db = router.db_for_read(Template, instance=template)
        display_name = self.make_display_name(db, template_name, site.domain)
        data = add_template_to_cache(template)
        content = data.get('content')
        return content, display_name

    def load_template_source(self, template_name, template_dirs=None):
        site = Site.objects.get_current()
        cache_key = get_cache_key(template_name)
        if cache:
            try:
                value = cache.get(cache_key)
                if value and site.pk in value.get('sites'):
                    backend_template = value.get('content')
                    display_name = self.make_display_name('cache', template_name, site.domain)
                    return backend_template, display_name
            except:             # XXX : Evil !!!
                pass

        try:
            return self.load_and_store_template(template_name, cache_key,
                                                site, sites__in=[site.id])
        except (Template.MultipleObjectsReturned, Template.DoesNotExist):
            try:
                return self.load_and_store_template(template_name, cache_key,
                                                    site, sites__isnull=True)
            except (Template.MultipleObjectsReturned, Template.DoesNotExist):
                pass

        raise TemplateDoesNotExist(template_name)
