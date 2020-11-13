# Based on spec_tests.py from
# https://github.com/commonmark/commonmark-spec/blob/master/test/spec_tests.py
# and
# https://github.com/github/cmark-gfm/blob/master/test/spec_tests.py

import re
import md4c
import pytest
from normalize import normalize_html


extension_flags = {
    'table': md4c.MD_FLAG_TABLES,
    'urlautolink': md4c.MD_FLAG_PERMISSIVEURLAUTOLINKS,
    'emailautolink': md4c.MD_FLAG_PERMISSIVEEMAILAUTOLINKS,
    'wwwautolink': md4c.MD_FLAG_PERMISSIVEWWWAUTOLINKS,
    'tasklist': md4c.MD_FLAG_TASKLISTS,
    #TODO Add test cases for the rest of these
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

    with open(specfile, 'r', encoding='utf-8', newline='\n') as specf:
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


all_tests = get_tests('spec.txt')


@pytest.mark.parametrize('test_case', all_tests,
                         id=lambda x: f'{x["file"]}:{x["start_line"]}')
test_html_example(test_case):
    """Test HTMLRenderer on the given example"""
    parser_flags = 0
    for extension in test_case['extensions']:
        parser_flags |= extension_flags[extension]

    renderer = md4c.HTMLRenderer(parser_flags, 0)
    output = renderer.parse(test_case['markdown'])

    assert normalized_html(output) == normalized_html(test_case['html'])

#TODO Test combination flags

#TODO Test keyword arguments for flags

#TODO Test HTML flags

#TODO Test mixing keyword arguments and traditional flags
