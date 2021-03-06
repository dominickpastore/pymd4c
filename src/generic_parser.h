/*
 * PyMD4C
 * Python bindings for MD4C
 *
 * generic_parser.h - md4c._md4c.GenericParser class
 * Wraps MD4C's SAX-like parser
 *
 * Copyright (c) 2020-2021 Dominick C. Pastore
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
 * OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 * IN THE SOFTWARE.
 */

#ifndef GENERIC_PARSER_H
#define GENERIC_PARSER_H

#ifndef PY_SSIZE_T_CLEAN
#define PY_SSIZE_T_CLEAN
#endif
#include <Python.h>

/*
 * GenericParser type object
 */
extern PyTypeObject GenericParserType;

/*
 * lookup_entity() function
 */
PyObject * lookup_entity(PyObject *self, PyObject *args);

#define LOOKUP_ENTITY_DOC "lookup_entity(entity)\n" \
    "\n" \
    "Translate an HTML entity to its UTF-8 representation. Returns the " \
    "unmodified input if it is not a valid entity.\n" \
    "\n" \
    ":param entity: The HTML entity, including ampersand and semicolon\n" \
    ":type entity: str\n" \
    ":returns: Corresponding UTF-8 character(s)\n" \
    ":rtype: str\n"

#endif
