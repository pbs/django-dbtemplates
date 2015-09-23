from django.db import router
from django.template import TemplateDoesNotExist
from django.contrib.sites.models import Site

from dbtemplates.models import Template
from dbtemplates.utils.cache import (
    get_cache_key,
    add_template_to_cache,
    fetch_template_from_cache,
    cache,
)
from django.template.loaders.base import Loader as BaseLoader


def site_cache_permission_rule(current_site, cache_value):
    return cache_value and current_site.pk in cache_value.get('sites')


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

    @classmethod
    def make_display_name(cls, origin, template_name, domain):
        """
        Used in the Loader by make_origin for template debuging purposes.
        See django.template.loader.make_origin.
        """
        return cls.display_format.format(
            origin=origin,
            template_name=template_name,
            domain=domain
        )

    def fetch_template_from_db(self, template_name, **params):
        templates = Template.objects.filter(
            name__exact=template_name, **params).distinct()
        if not templates:
            raise Template.DoesNotExist(template_name)
        # template names are unique => there should always be a single
        # template returned
        template = templates[0]
        return template

    def load_and_store_template(self, template_name, key, site, **params):
        template = self.fetch_template_from_db(template_name, **params)
        add_template_to_cache(template)
        db = router.db_for_read(Template, instance=template)
        display_name = self.make_display_name(db, template_name, site.domain)
        template_content = template.content
        return template_content, display_name

    def load_from_cache(self, site, template_name):
        source = fetch_template_from_cache(
            template_name,
            lambda cached: site_cache_permission_rule(site, cached)
        )
        if source:
            display_name = self.make_display_name(
                'cache',
                template_name,
                site.domain
            )
            return source, display_name

    def load_template_source(self, template_name, template_dirs=None):
        site = Site.objects.get_current()
        cache_tuple = self.load_from_cache(site, template_name)
        if cache_tuple:
            return cache_tuple

        cache_key = get_cache_key(template_name)
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
