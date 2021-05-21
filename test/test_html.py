# Based on spec_tests.py from
# https://github.com/commonmark/commonmark-spec/blob/master/test/spec_tests.py
# and
# https://github.com/github/cmark-gfm/blob/master/test/spec_tests.py

import sys
import os
import os.path
import re
import md4c
import md4c.domparser
import pytest
from normalize import normalize_html


extension_flags = {
    'table': md4c.MD_FLAG_TABLES,
    'urlautolink': md4c.MD_FLAG_PERMISSIVEURLAUTOLINKS,
    'emailautolink': md4c.MD_FLAG_PERMISSIVEEMAILAUTOLINKS,
    'wwwautolink': md4c.MD_FLAG_PERMISSIVEWWWAUTOLINKS,
    'tasklist': md4c.MD_FLAG_TASKLISTS,
    'strikethrough': md4c.MD_FLAG_STRIKETHROUGH,
    'underline': md4c.MD_FLAG_UNDERLINE,
    'wikilink': md4c.MD_FLAG_WIKILINKS,
    'latexmath': md4c.MD_FLAG_LATEXMATHSPANS,
    #TODO Add test cases for the rest of the flags
    # (including combination flags)
}


def get_tests(specfile):
    line_number = 0
    start_line = 0
    end_line = 0
    example_number = 0
    markdown_lines = []
    html_lines = []
    state = 0  # 0 regular text, 1 markdown example, 2 html output
    extensions = []
    headertext = ''
    tests = []

    header_re = re.compile('#+ ')

    full_specfile = os.path.join(sys.path[0], 'spec', specfile)
    with open(full_specfile, 'r', encoding='utf-8', newline='\n') as specf:
        for line in specf:
            line_number = line_number + 1
            l = line.strip()
            if l.startswith("`" * 32 + " example"):
                state = 1
                extensions = l[32 + len(" example"):].split()
            elif l == "`" * 32:
                state = 0
                example_number = example_number + 1
                end_line = line_number
                if 'disabled' not in extensions:
                    tests.append({
                        "markdown":''.join(markdown_lines).replace('→',"\t"),
                        "html":''.join(html_lines).replace('→',"\t"),
                        "example": example_number,
                        "start_line": start_line,
                        "end_line": end_line,
                        "section": headertext,
                        "file": specfile,
                        "extensions": extensions})
                start_line = 0
                markdown_lines = []
                html_lines = []
            elif l == ".":
                state = 2
            elif state == 1:
                if start_line == 0:
                    start_line = line_number - 1
                markdown_lines.append(line)
            elif state == 2:
                html_lines.append(line)
            elif state == 0 and re.match(header_re, line):
                headertext = header_re.sub('', line).strip()
    return tests


def collect_all_tests():
    all_tests = []
    specfiles = os.listdir(os.path.join(sys.path[0], 'spec'))
    for specfile in specfiles:
        all_tests.extend(get_tests(specfile))
    return all_tests


@pytest.mark.parametrize(
    'test_case', collect_all_tests(),
     ids=lambda x: f'{x["file"]}:{x["start_line"]}-{x["section"]}')
def test_html_output(test_case):
    """Test HTMLRenderer with default render flags on the given example"""
    parser_flags = 0
    for extension in test_case['extensions']:
        parser_flags |= extension_flags[extension]

    renderer = md4c.HTMLRenderer(parser_flags, 0)
    output = renderer.parse(test_case['markdown'])

    assert normalize_html(output) == normalize_html(test_case['html'], False)

@pytest.mark.parametrize(
    'test_case', collect_all_tests(),
     ids=lambda x: f'{x["file"]}:{x["start_line"]}-{x["section"]}')
def test_domparser_html(test_case):
    """Test that the output for DOMParser render() matches HTMLRenderer char
    for char"""
    parser_flags = 0
    for extension in test_case['extensions']:
        parser_flags |= extension_flags[extension]

    html_renderer = md4c.HTMLRenderer(parser_flags)
    html_output = html_renderer.parse(test_case['markdown'])

    dom_parser = md4c.domparser.DOMParser(parser_flags)
    dom_output = dom_parser.parse(test_case['markdown']).render()

    assert html_output == dom_output


#TODO Test keyword arguments for flags

#TODO Test HTML flags

#TODO Test mixing keyword arguments and traditional flags
