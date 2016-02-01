import contextlib as ctx
from functools import partial, wraps
from inspect import isgeneratorfunction as is_gen


def format_tag(template, tag_name, attrs):
    """
    Format a template of a tag with attributes, so that:
    >>> format_tag('<{} {}>', 'span', {'id': 'foo'})
    >>> '<span id="foo">'
    Note: use `klass` instead of the `class` attribute.
    """
    return template.format(tag_name, ' '.join(['{}="{}"'.format(key.replace('klass', 'class'), val) 
                                               for (key, val) in attrs.iteritems()]))


def tag(tag_name, bufferer):
    """
    Creates a tag factory used via context manager.
    DO NOT USE DIRECTLY.
    >>> with tag('span', page)({'id': 'foo'}):
        ... page.text('foo!')
    >>> str(page)
    >>> '<span id="foo">foo!</span>'
    """
    @ctx.contextmanager
    def factory(**attrs):
        bufferer.append(format_tag('<{} {}>', tag_name, attrs))
        yield
        bufferer.append('</{}>'.format(tag_name))
    return factory


class Page(object):
    """
    Create a page buffer.
    """
    custom_elements = {}

    @classmethod
    def register(cls, element_factory):
        cls.custom_elements[element_factory.func_name] = element_factory

    def __init__(self):
        self._buffer = ''

    def __getattr__(self, attr):
        """
        This creates the magic of tag factories.
        """
        if attr.startswith('_') or attr == 'text': 
            return super(Page, self).__getattr__(self, attr)
        elif attr in ('input', 'img', 'hr'):
            return partial(self._self_closing_tag, attr)
        elif attr in self.custom_elements:
            return partial(self.custom_elements[attr], self)
        return tag(attr, self)

    def __str__(self):
        return self._buffer

    def append(self, text):
        self._buffer += text

    def _self_closing_tag(self, tag_name, **attrs):
        self._buffer += format_tag('<{} {}/>', tag_name, attrs)

    def text(self, t):
        self._buffer += str(t)


def view(f):
    """
    Decorate a view function.
    The decorated function has to recieve a Page object
    as a first parameter.
    The resulting function will recieve all parameters *except*
    the Page object, and will always return the rendered Page.
    
    A generator function can be decorated for a different creature.
    This results in a custom element, registered on all Page objects,
    That can be used using `with` as normal.
    This usage returns None.

    Example usage:

    @view
    def main(p, title):
        with p.div(klass='container'):
            with p.h1():
                p.text(title)

    >>> main('Foo')
    >>> '<div class="container"><h1>Foo</h1></div>'
    """
    if is_gen(f):
        Page.register(ctx.contextmanager(f))
        return

    @wraps(f)
    def _inner(*args, **kwargs):
        p = Page()
        f(p, *args, **kwargs)
        return str(p)
    return _inner