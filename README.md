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

### Transpiling .pyv files

```python
from pyvue import view_parser

with open('foo.pyv') as pyv:
    open('foo.py', 'wb').write(view_parser(pyv.read()))
```

Or, using [facade](http://github.com/oakfang/facade),
you can import them directly, using the pyv loader:

```python
from facade import pyv
import foo # that's a .pyv file!

foo.index(...)
```