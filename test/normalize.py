# -*- coding: utf-8 -*-
from html.parser import HTMLParser
import urllib

from html.entities import name2codepoint
import sys
import re
import html

# Normalization code, adapted from
# https://github.com/karlcow/markdown-testsuite/
significant_attrs = ["alt", "href", "src", "title"]
whitespace_re = re.compile(r'\s+')
class MyHTMLParser(HTMLParser):
    def __init__(self, preserve_self_closing=True):
        HTMLParser.__init__(self)
        self.convert_charrefs = False
        self.preserve_self_closing = preserve_self_closing
        self.last = "starttag"
        self.in_pre = False
        self.output = ""
        self.last_tag = ""
    def handle_data(self, data):
        after_tag = self.last == "endtag" or self.last == "starttag"
        after_block_tag = after_tag and self.is_block_tag(self.last_tag)
        if after_tag and self.last_tag == "br":
            data = data.lstrip('\n')
        if not self.in_pre:
            data = whitespace_re.sub(' ', data)
        if after_block_tag and not self.in_pre:
            if self.last == "starttag":
                data = data.lstrip()
            elif self.last == "endtag":
                data = data.strip()
        self.output += data
        self.last = "data"
    def handle_endtag(self, tag):
        if tag == "pre":
            self.in_pre = False
        elif self.is_block_tag(tag):
            self.output = self.output.rstrip()
        self.output += "</" + tag + ">"
        self.last_tag = tag
        self.last = "endtag"
    def starttag(self, tag, attrs, self_closing):
        if tag == "pre":
            self.in_pre = True
        if self.is_block_tag(tag):
            self.output = self.output.rstrip()
        self.output += "<" + tag
        # For now we don't strip out 'extra' attributes, because of
        # raw HTML test cases.
        # attrs = filter(lambda attr: attr[0] in significant_attrs, attrs)
        if attrs:
            attrs.sort()
            for (k,v) in attrs:
                self.output += " " + k
                if v in ['href','src']:
                    self.output += ("=" + '"' +
                            urllib.quote(urllib.unquote(v), safe='/') + '"')
                elif v != None:
                    self.output += ("=" + '"' + html.escape(v,quote=True) + '"')
        if self_closing:
            self.output += "/"
        self.output += ">"
    def handle_starttag(self, tag, attrs):
        self.starttag(tag, attrs, False)
        self.last_tag = tag
        self.last = "starttag"
    def handle_startendtag(self, tag, attrs):
        """Potentially convert a self-closing tag to a regular tag"""
        self.starttag(tag, attrs, self.preserve_self_closing)
        self.last_tag = tag
        self.last = "endtag"
    def handle_comment(self, data):
        self.output += '<!--' + data + '-->'
        self.last = "comment"
    def handle_decl(self, data):
        self.output += '<!' + data + '>'
        self.last = "decl"
    def unknown_decl(self, data):
        self.output += '<!' + data + '>'
        self.last = "decl"
    def handle_pi(self,data):
        self.output += '<?' + data + '>'
        self.last = "pi"
    def handle_entityref(self, name):
        try:
            c = chr(name2codepoint[name])
        except KeyError:
            c = None
        self.output_char(c, '&' + name + ';')
        self.last = "ref"
    def handle_charref(self, name):
        try:
            if name.startswith("x"):
                c = chr(int(name[1:], 16))
            else:
                c = chr(int(name))
        except ValueError:
                c = None
        self.output_char(c, '&' + name + ';')
        self.last = "ref"
    # Helpers.
    def output_char(self, c, fallback):
        if c == '<':
            self.output += "&lt;"
        elif c == '>':
            self.output += "&gt;"
        elif c == '&':
            self.output += "&amp;"
        elif c == '"':
            self.output += "&quot;"
        elif c == None:
            self.output += fallback
        else:
            self.output += c

    def is_block_tag(self,tag):
        return (tag in ['article', 'header', 'aside', 'hgroup', 'blockquote',
            'hr', 'iframe', 'body', 'li', 'map', 'button', 'object', 'canvas',
            'ol', 'caption', 'output', 'col', 'p', 'colgroup', 'pre', 'dd',
            'progress', 'div', 'section', 'dl', 'table', 'td', 'dt',
            'tbody', 'embed', 'textarea', 'fieldset', 'tfoot', 'figcaption',
            'th', 'figure', 'thead', 'footer', 'tr', 'form', 'ul',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'video', 'script', 'style'])

def normalize_html(html, preserve_self_closing=True):
    r"""
    Return normalized form of HTML which ignores insignificant output
    differences:

    Multiple inner whitespaces are collapsed to a single space (except
    in pre tags):

        >>> normalize_html("<p>a  \t b</p>")
        '<p>a b</p>'

        >>> normalize_html("<p>a  \t\nb</p>")
        '<p>a b</p>'

    * Whitespace surrounding block-level tags is removed.

        >>> normalize_html("<p>a  b</p>")
        '<p>a b</p>'

        >>> normalize_html(" <p>a  b</p>")
        '<p>a b</p>'

        >>> normalize_html("<p>a  b</p> ")
        '<p>a b</p>'

        >>> normalize_html("\n\t<p>\n\t\ta  b\t\t</p>\n\t")
        '<p>a b</p>'

        >>> normalize_html("<i>a  b</i> ")
        '<i>a b</i> '

    * Attributes are sorted and lowercased.

        >>> normalize_html('<a title="bar" HREF="foo">x</a>')
        '<a href="foo" title="bar">x</a>'

    * References are converted to unicode, except that '<', '>', '&', and
      '"' are rendered using entities.

        >>> normalize_html("&forall;&amp;&gt;&lt;&quot;")
        '\u2200&amp;&gt;&lt;&quot;'

    * Self-closing tags are optionally converted to open tags.

        >>> normalize_html("<br />")
        '<br>'

    """
    html_chunk_re = re.compile(r"(\<!\[CDATA\[.*?\]\]\>|\<[^>]*\>|[^<]+)")
    parser = MyHTMLParser(preserve_self_closing)
    # We work around HTMLParser's limitations parsing CDATA
    # by breaking the input into chunks and passing CDATA chunks
    # through verbatim.
    for chunk in re.finditer(html_chunk_re, html):
        if chunk.group(0)[:8] == "<![CDATA":
            parser.output += chunk.group(0)
        else:
            parser.feed(chunk.group(0))
    parser.close()
    return parser.output
