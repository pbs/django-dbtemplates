from django import VERSION
from django.template import (
    Engine, Template, TemplateDoesNotExist, TemplateSyntaxError)


def get_loaders():
    try:
        default_template_engine = Engine.get_default()
    except (Exception, ):
        return []

    if not default_template_engine:
        return []
    try:
        return default_template_engine.template_loaders
    except (Exception, ):
        return []


def get_template_source(name):
    source = None
    for loader in get_loaders():
        if loader.__module__.startswith('dbtemplates.'):
            # Don't give a damn about dbtemplates' own loader.
            continue
        try:
            source, origin = loader.load_template_source(name)
            if source:
                return source
        except TemplateDoesNotExist:
            pass
    return None


def check_template_syntax(template):
    try:
        Template(template.content)
    except TemplateSyntaxError, e:
        return (False, e)
    return (True, None)
