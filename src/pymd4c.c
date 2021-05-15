/*
 * PyMD4C
 * Python bindings for MD4C
 *
 * pymd4c.c - md4c._md4c module
 * Provides the parser and renderer classes that interface directly with MD4C
 * (The classes themselves are in separate .c files)
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

#ifndef PY_SSIZE_T_CLEAN
#define PY_SSIZE_T_CLEAN
#endif
#include <Python.h>

#include <md4c.h>

#include "pymd4c.h"
#include "generic_parser.h"
#include "html_renderer.h"

/*
 * Name of enums module to import
 */
const char *enums_module = "md4c.enums";

/*
 * Exception objects
 */
PyObject *ParseError;
PyObject *StopParsing;

/*
 * Add the flag constants to the provided module. Return 0 on success, -1 on
 * error.
 */
static int md4c_add_flags(PyObject *m) {
    // Add the parser option flags
    if (PyModule_AddIntConstant(m, "MD_FLAG_COLLAPSEWHITESPACE",
                MD_FLAG_COLLAPSEWHITESPACE) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_PERMISSIVEATXHEADERS",
                MD_FLAG_PERMISSIVEATXHEADERS) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_PERMISSIVEURLAUTOLINKS",
                MD_FLAG_PERMISSIVEURLAUTOLINKS) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_PERMISSIVEEMAILAUTOLINKS",
                MD_FLAG_PERMISSIVEEMAILAUTOLINKS) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_NOINDENTEDCODEBLOCKS",
                MD_FLAG_NOINDENTEDCODEBLOCKS) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_NOHTMLBLOCKS",
                MD_FLAG_NOHTMLBLOCKS) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_NOHTMLSPANS",
                MD_FLAG_NOHTMLSPANS) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_TABLES",
                MD_FLAG_TABLES) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_STRIKETHROUGH",
                MD_FLAG_STRIKETHROUGH) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_PERMISSIVEWWWAUTOLINKS",
                MD_FLAG_PERMISSIVEWWWAUTOLINKS) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_TASKLISTS",
                MD_FLAG_TASKLISTS) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_LATEXMATHSPANS",
                MD_FLAG_LATEXMATHSPANS) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_WIKILINKS",
                MD_FLAG_WIKILINKS) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_UNDERLINE",
                MD_FLAG_UNDERLINE) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_PERMISSIVEAUTOLINKS",
                MD_FLAG_PERMISSIVEAUTOLINKS) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_NOHTML",
                MD_FLAG_NOHTML) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_DIALECT_COMMONMARK",
                MD_DIALECT_COMMONMARK) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_DIALECT_GITHUB",
                MD_DIALECT_GITHUB) < 0) {
        return -1;
    }

    if (md4c_add_htmlrenderer_flags(m) < 0) {
        return -1;
    }

    return 0;
}

/*
 * Module Definition
 */
static PyModuleDef md4c_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "_md4c",
    .m_doc = "Python bindings for MD4C parsers and renderers",
    .m_size = -1,
};

/*
 * Module initialization function
 */
PyMODINIT_FUNC PyInit__md4c(void)
{
    // Initialize the types in the module
    if (PyType_Ready(&HTMLRendererType) < 0) {
        return NULL;
    }
    if (PyType_Ready(&GenericParserType) < 0) {
        return NULL;
    }

    // Create the module object
    PyObject *m;
    m = PyModule_Create(&md4c_module);
    if (m == NULL) {
        return NULL;
    }

    // Add the option flag constants to the module
    if (md4c_add_flags(m) < 0) {
        Py_DECREF(m);
        return NULL;
    }

    // Add the types to the module
    Py_INCREF(&HTMLRendererType);
    if (PyModule_AddObject(m, "HTMLRenderer", (PyObject *) &HTMLRendererType)
            < 0) {
        Py_DECREF(&HTMLRendererType);
        Py_DECREF(m);
        return NULL;
    }
    Py_INCREF(&GenericParserType);
    if (PyModule_AddObject(m, "GenericParser", (PyObject *) &GenericParserType)
            < 0) {
        Py_DECREF(&GenericParserType);
        Py_DECREF(m);
        return NULL;
    }

    // Add the ParseError and StopParsing exceptions to the module
    ParseError = PyErr_NewExceptionWithDoc("md4c._md4c.ParseError",
            "Raised when an error occurs during parsing, such as running out "
            "of memory. Note that there is no such thing as invalid syntax in "
            "Markdown, so this really only signals some sort of system error.",
            NULL, NULL);
    Py_XINCREF(ParseError);
    if (PyModule_AddObject(m, "ParseError", ParseError) < 0) {
        Py_XDECREF(ParseError);
        Py_CLEAR(ParseError);
        Py_DECREF(m);
        return NULL;
    }
    StopParsing = PyErr_NewExceptionWithDoc("md4c._md4c.StopParsing",
            "A callback function can raise this to stop parsing early for non-"
            "error reasons. :class:`GenericParser` (and by extension, "
            ":class:`ParserObject`) will catch it and abort quietly.",
            NULL, NULL);
    Py_XINCREF(StopParsing);
    if (PyModule_AddObject(m, "StopParsing", StopParsing) < 0) {
        Py_XDECREF(StopParsing);
        Py_CLEAR(StopParsing);
        Py_DECREF(m);
        return NULL;
    }

    // Import the md4c._enums module
    PyObject *enums = PyImport_ImportModule(enums_module);
    if (enums == NULL) {
        Py_DECREF(m);
        return NULL;
    }
    Py_DECREF(enums);

    return m;
}
