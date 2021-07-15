#
# PyMD4C
# Python bindings for MD4C
#
# Tests involving bytes input
#
# Copyright (c) 2021 Dominick C. Pastore
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

import md4c
import md4c.domparser
import pytest

@pytest.fixture
def html_renderer():
    return md4c.HTMLRenderer()

@pytest.fixture
def dom_parser():
    return md4c.domparser.DOMParser()

long_in = b'''# Hello, world

Lorem `ipsum` *dolor **sit*** [amet](http://example.com/ "foo").

    int main(int argc, char ** argv) {
        return 0;
    }

Some lists:

* Cat
* Dog
* Fish

---

1. One
2. Two
3. Three

> It was the best of times, it was the worst of times

The end.
'''

long_expected = b'''<h1>Hello, world</h1>
<p>Lorem <code>ipsum</code> <em>dolor <strong>sit</strong></em> <a href="http://example.com/" title="foo">amet</a>.</p>
<pre><code>int main(int argc, char ** argv) {
    return 0;
}
</code></pre>
<p>Some lists:</p>
<ul>
<li>Cat</li>
<li>Dog</li>
<li>Fish</li>
</ul>
<hr>
<ol>
<li>One</li>
<li>Two</li>
<li>Three</li>
</ol>
<blockquote>
<p>It was the best of times, it was the worst of times</p>
</blockquote>
<p>The end.</p>
'''

scenarios = [
    ('basic',
     b'Hello, world',
     b'<p>Hello, world</p>\n'),
    ('high_bytes',
     b'Hello, \xed\xb2\x93world',
     b'<p>Hello, \xed\xb2\x93world</p>\n'),
    ('null_byte',
     b'Hello, \x00world',
     b'<p>Hello, \xef\xbf\xbdworld</p>\n'),
    ('link1',
     b'[Hello, \xed\xb2\x93world](http://example.com/)',
     b'<p><a href="http://example.com/">Hello, \xed\xb2\x93world</a></p>\n'),
    ('link2',
     b'[Hello, world](http://example.com/ "foo\xed\xb2\x93bar")',
     b'<p><a href="http://example.com/" title="foo\xed\xb2\x93bar">Hello, world</a></p>\n'),
    ('link3',
     b'[Hello, world](http://example.com/\xed\xb2\x93/ "foo bar")',
     b'<p><a href="http://example.com/%ED%B2%93/" title="foo bar">Hello, world</a></p>\n'),
    ('long',
     long_in,
     long_expected),
]

@pytest.mark.parametrize('md,expected', ((y, z) for _, y, z in scenarios),
                         ids=(x for x, _, _ in scenarios))
def test_bytes_htmlrenderer(html_renderer, md, expected):
    actual = html_renderer.parse(md)
    assert actual == expected

@pytest.mark.parametrize('md,expected', ((y, z) for _, y, z in scenarios),
                         ids=(x for x, _, _ in scenarios))
def test_bytes_domparser(dom_parser, md, expected):
    ast = dom_parser.parse(md)
    actual = ast.render()
    assert actual == expected

def test_domparser_text_not_bytes():
    with pytest.raises(TypeError):
        md4c.domparser.ASTNode(md4c.TextType.NORMAL,
                               use_bytes=True,
                               text='Hello, world!')

def test_domparser_text_not_str():
    with pytest.raises(TypeError):
        md4c.domparser.ASTNode(md4c.TextType.NORMAL,
                               text=b'Hello, world!')

def test_domparser_child_not_bytes(dom_parser):
    md = b'''# Hello, world'''
    ast = dom_parser.parse(md)

    paragraph = md4c.domparser.ASTNode(md4c.BlockType.P)
    paragraph.append(md4c.domparser.ASTNode(md4c.TextType.NORMAL,
                                            text='foo bar'))
    with pytest.raises(ValueError):
        ast.append(paragraph)

def test_domparser_child_not_str(dom_parser):
    md = '''# Hello, world'''
    ast = dom_parser.parse(md)

    paragraph = md4c.domparser.ASTNode(md4c.BlockType.P, use_bytes=True)
    paragraph.append(md4c.domparser.ASTNode(md4c.TextType.NORMAL,
                                            use_bytes=True,
                                            text=b'foo bar'))
    with pytest.raises(ValueError):
        ast.append(paragraph)

def test_domparser_attr_not_bytes():
    with pytest.raises(TypeError):
        md4c.domparser.ASTNode(
            md4c.SpanType.A,
            use_bytes=True,
            href=[(md4c.TextType.NORMAL, 'http://www.example.com/')])

def test_domparser_attr_not_str():
    with pytest.raises(TypeError):
        md4c.domparser.ASTNode(
            md4c.SpanType.A,
            href=[(md4c.TextType.NORMAL, b'http://www.example.com/')])
