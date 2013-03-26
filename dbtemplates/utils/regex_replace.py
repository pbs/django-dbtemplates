import re

PATTERN_LOAD = [r'(\{% load .*)', r'(.*%\})']
PATTERN_FILTER = [r'(\{\{.*\|)' ,r'(:"\d*x|X\d*".*\}\})']


def regex_replace(content, old, new):
    pattern = re.compile(old.join(PATTERN_LOAD))
    new_content = pattern.sub(r'\1%s\2' % new, content)

    pattern = re.compile(old.join(PATTERN_FILTER))
    return pattern.sub(r'\1%s\2' % new, new_content)
