"""
The pyvue syntax is a superset of python, allowing for a new
type of function declaration. Essentially, it adds the `view` keyword,
which becomes a very specialized type of `def`, and allows you to define
view functions.
A view finction uses a mixture of python code and HTML markup,
and returns a rendered Page when called. The only rendered elements are
the ones written in HTML, but they are directly affected by the python code.
Example:

view main(title):
    <div klass="foo">
        <h1>
            <py>title</py>
        </h1>
        <ul>
            for x in xrange(10):
                <li>
                    <py>x</py>
                </li>
        </ul>
    </div>

Notes:
- A view function has to have a blank line or EOF after it
- A view fuunction mustn't have blank lines in its body
- Any untagged line is ALWAYS a python line
- Adding "text" to the page will be done using the `py` tag,
  and will actually inject python code as text, so contant text
  should be a string expression: <py>'FOO'</py>
  All objects passed to the `py` tag will be converted to strings via str().
- `py` is the only tag that can be used inline, other tags must
  be used like this:
  <div>
      ...
  </div> # closing tag on its own line with the same indentation as 
  the openning tag.
"""
import re
import tokenize
from cStringIO import StringIO as sio


VIEW_RE = re.compile('^(\s*view \w+\(.*?\):(.|\n)*?\r?\n\s*)(\n|$)', re.MULTILINE)
VIEW_HEADER_RE = re.compile('(\s*)view (\w+)\((.*?)\):')


def handle_tokens(args_map):
    state = {
        'recording': False,
        'toks': []
    }
    def handler(ttype, value, _, __, ___):
        if ttype == tokenize.OP and value == '=':
            recording_for = state['toks'].pop()
            if state['toks']:
                args_map[state['recording']] = ' '.join(state['toks'])
            state['recording'] = recording_for
            state['toks'] = []
        elif ttype == tokenize.ENDMARKER:
            args_map[state['recording']] = ' '.join(state['toks'])
        else:
            state['toks'].append(value)
    return handler


def tokenize_args(line):
    args_map = {}
    if line:
        tokenize.tokenize(sio(line).readline, handle_tokens(args_map))
    return args_map


def replace_args(has_block, self_closing=False):
    def handler(match):
        template = ('{space}with __p.{tag}(**dict({args})):{block}' 
                    if not self_closing 
                    else '{space}__p.{tag}(**dict({args}))')
        return template.format(space=match.group(1),
                                tag=match.group(2),
                                args=', '.join([
                                  '{key}={val}'.format(key=key, val=val)
                                  for (key, val) 
                                  in tokenize_args(match.group(3)).iteritems()]),
                                block=match.group(4) if has_block else ' pass')
    return handler


def view_parser(content):
    """
    Parses pyvue syntax into normal python code.
    This will NOT inject the view decorator into your code,
    which you will have to import explicitly.
    """
    for view_block in [res[0] for res in VIEW_RE.findall(content)]:
        block = VIEW_HEADER_RE.sub(r'\1@view\n\1def \2(__p, \3):', view_block)
        block = re.sub(r'\<py\>((.|\n)*?)\</py\>', r'__p.text(\1)', block)
        block = re.sub(r'^(\s*)?\<([a-zA-Z0-9_]+)\s?(.*?)\>\s*</\2\>', replace_args(False), block, flags=re.M)
        temp = re.sub(r'^(\s*)?\<([a-zA-Z0-9_]+)\s?(.*?)\>((.|\n)*?)\1\</\2\>', replace_args(True), block, flags=re.M)
        while temp != block:
            block = temp
            temp = re.sub(r'^(\s*)?\<([a-zA-Z0-9_]+)\s?(.*?)\>((.|\n)*?)\1\</\2\>', replace_args(True), block, flags=re.M)
        block = re.sub(r'^(\s*)?<(\w+)\s?(.*?)\/\>\s*$', replace_args(False, True), block, flags=re.M)
        content = content.replace(view_block, block)
    return content


def compile_file():
    """
    Parse a file and print the generated python code
    """
    from sys import argv, exit
    if len(argv) < 2:
        print 'Usage: {} <file_path>'.format(argv[0])
        exit(1)

    file_path = argv[1]
    with open(file_path) as pyv_file:
        print view_parser(pyv_file.read() + '\n')