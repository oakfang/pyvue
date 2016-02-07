# PyVue
## Generate HTML strings in pure python, or JSX style code!

### The need
So, you find yourself coding a small webserver in python in
the middle of the night and you need some HTML.

BUT - you need dynamic HTML.

### The want
You want something like Jinja2 or Django templates. Something
that mixes HTML and python in a concise and readable way.

### The hurts
These libraries use weird syntax to handle python code.

### The solution
PyVue lets you write python templates in one of 2 ways:

```python
# hardcore.py
from pyvue import view

@view
def index_page(p, title, block):
    with p.html():
        with p.head():
            with p.title(): p.text(title)
        with p.body():
            with p.header():
                with p.h1(): p.text(title)
            with p.section():
                p.text(block)

@view
def component(p, items):
    with p.ul():
        for item in items:
            with p.li():
                p.text(item)

print index_page("Index", component(xrange(10)))
"""
<html>
    <head>
        <title>Index</title>
    </head>
    <body>
        <header>
            <h1>Index</h1>
        </header>
        <section>
            <ul>
                <li>0</li>
                <li>1</li>
                <li>2</li>
                <li>3</li>
                <li>4</li>
                <li>5</li>
                <li>6</li>
                <li>7</li>
                <li>8</li>
                <li>9</li>
            </ul>
        </section>
    </body>
</html>
"""
```

or:

```python
# awesome.pyv
from pyvue import view

view index_page(title, block):
    <html>
        <head>
            <title>
                <py>title</py>
            </title>
        </head>
        <body>
            <header>
                <h1>
                    <py>title</py>
                </h1>
            </header>
            <section>
                <py>block</py>
            </section>
        </body>
    </html>

view component(items):
    <ul>
        for item in items:
            <li>
                <py>item</py>
            </li>
    </ul>

print index_page("Index", component(xrange(10)))
# exactly the same output :)
```

### Resuable Components
Okay, so you can write renderable views. That's awesome,
but you want to use some of your views as reusable components, the way God intended.

The solution is easy enough: `yield`.

`yield`ing at any point inside a view will make it a `component view`.

#### What is a `component view` and how is it different than a regular `view`?
A `view` is a function that returns a string, which represents a rendered page.

A `component view` is added to the list of HTML tags every `Page` object recongnises,
and can be used as a context manager, just like `div` or `span` with one special difference:

The "attributes" passed to a `component view` are actually his function parameters
(again, the first `Page` parameter is implicit).

However, a `component view` **cannot** be rendered as a `view`.

Example:

```python
@view
def component(p, text):
    with p.span():
        p.text(text)
    yield # make this a component. Every alteration of the Page occuring in this context will happen here.
    

@view
def scope(p):
    with p.div():
        yield # make this a component. Every alteration of the Page occuring in this context will happen here.
    with p.div():
        with p.span():
            p.text('End of component')


@view
def main(p):
    with p.scope():
        with p.component('Hello!'): pass


main() # will render
scope() # will raise NoneType non-callable exception
```

Obviously, since .pyv syntax allows for arbitrary python code,
simply `yield`ing anywhere inside a `view` will be sufficient.

Afterwards, using a component as a tag is perfectly okay:

```python
view component(text):
    <span>
        <py>text</py>
    </span>
    yield


view scope():
    <div>
        yield
    </div>
    <div>
        <span>
            <py>'End of component'</py>
        </span>
    </div>


view main():
    <scope>
        <component text='hello!'></component>
    </scope>


main() # will render
scope() # will raise NoneType non-callable exception
```

### Transpiling .pyv files

#### Using the commandline

```
pyvuec ./foo.pyv > foo.py
```

#### Using the parser directly

```python
from pyvue import view_parser

with open('foo.pyv') as pyv:
    open('foo.py', 'wb').write(view_parser(pyv.read()))
```

#### Using [facade](http://github.com/oakfang/facade)

```python
from facade import pyv
import foo # that's a .pyv file!

foo.index(...)
```
