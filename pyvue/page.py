import contextlib as ctx


def tag(tag_name, bufferer):
    @ctx.contextmanager
    def factory(**attrs):
        bufferer._buffer += '<{} {}>'.format(tag_name,
                                             ' '.join(['{}="{}"'.format(key.replace('klass', 'class'), val) 
                                                       for (key, val) in attrs.iteritems()]))
        yield
        bufferer._buffer += '</{}>'.format(tag_name)
    return factory


class Page(object):
    def __init__(self):
        self._buffer = ''

    def __getattr__(self, attr):
        try:
            if attr in ('input', 'img', 'hr'):
                return lambda **attrs: self._self_closing_tag(attr, **attrs)
            return object.__getattr__(self, attr)
        except AttributeError:
            return tag(attr, self)

    def text(self, t):
        self._buffer += str(t)

    def _self_closing_tag(self, tag_name, **attrs):
        self._buffer += '<{} {}/>'.format(tag_name,
                                          ' '.join(['{}="{}"'.format(key.replace('klass', 'class'), val) 
                                                    for (key, val) in attrs.iteritems()]))

    def __str__(self):
        return self._buffer


def view(f):
    def _inner(*args, **kwargs):
        p = Page()
        f(p, *args, **kwargs)
        return str(p)
    return _inner