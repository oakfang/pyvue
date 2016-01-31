import re


VIEW_RE = re.compile('^(\s*view \w+\(.*?\):(.|\n)*?\r?\n\s*)(\n|$)', re.MULTILINE)
VIEW_HEADER_RE = re.compile('(\s*)view (\w+)\((.*?)\):')


def view_parser(content):
    for view_block in [res[0] for res in VIEW_RE.findall(content)]:
        block = VIEW_HEADER_RE.sub(r'\1@view\n\1def \2(__p, \3):', view_block)
        block = re.sub(r'\<py\>((.|\n)*?)\</py\>', r'__p.text(\1)', block)
        temp = re.sub(r'^(\s*)?\<(\w+)\s?(.*?)\>((.|\n)*?)\1\</\2\>', r'\1with __p.\2(\3):\4', block, flags=re.M)
        while temp != block:
            block = temp
            temp = re.sub(r'^(\s*)?\<(\w+)\s?(.*?)\>((.|\n)*?)\1\</\2\>', r'\1with __p.\2(\3):\4', block, flags=re.M)
        block = re.sub(r'^(\s*)?<(\w+)\s?(.*?)\/\>\s*$', r'\1__p.\2(\3)', block, flags=re.M)
        content = content.replace(view_block, block)
    return content