import contextlib as ctx
from functools import partial


def format_tag(template, tag_name, attrs):
    return template.format(tag_name, ' '.join(['{}="{}"'.format(key.replace('klass', 'class'), val) 
                                               for (key, val) in attrs.iteritems()]))


def tag(tag_name, bufferer):
    @ctx.contextmanager
    def factory(**attrs):
        bufferer._buffer += format_tag('<{} {}>', tag_name, attrs)
        yield
        bufferer._buffer += '</{}>'.format(tag_name)
    return factory


class Page(object):
    def __init__(self):
        self._buffer = ''

    def __getattr__(self, attr):
        if attr.startswith('_') or attr == 'text': 
            return super(Page, self).__getattr__(self, attr)
        elif attr in ('input', 'img', 'hr'):
            return partial(self._self_closing_tag, attr)
        return tag(attr, self)

    def __str__(self):
        return self._buffer

    def _self_closing_tag(self, tag_name, **attrs):
        self._buffer += format_tag('<{} {}/>', tag_name, attrs)

    def text(self, t):
        self._buffer += str(t)


def view(f):
    def _inner(*args, **kwargs):
        p = Page()
        f(p, *args, **kwargs)
        return str(p)
    return _inner