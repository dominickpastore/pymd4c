/*
 * PyMD4C
 * Python bindings for MD4C
 *
 * enum_consts.c - md4c._enum_consts module
 * Python bindings for the various enum constants for MD4C. These are not
 * intended for direct use by applications--they should use the Python enums
 * instead
 *
 * Copyright (c) 2020 Dominick C. Pastore
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

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <md4c.h>

/*
 * Add MD_BLOCKTYPE enum constants
 */
int add_blocktype_consts(PyObject *m) {
    if (PyModule_AddIntConstant(m, "MD_BLOCK_DOC",
                MD_BLOCK_DOC) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_BLOCK_QUOTE",
                MD_BLOCK_QUOTE) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_BLOCK_UL",
                MD_BLOCK_UL) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_BLOCK_OL",
                MD_BLOCK_OL) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_BLOCK_LI",
                MD_BLOCK_LI) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_BLOCK_HR",
                MD_BLOCK_HR) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_BLOCK_H",
                MD_BLOCK_H) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_BLOCK_CODE",
                MD_BLOCK_CODE) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_BLOCK_HTML",
                MD_BLOCK_HTML) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_BLOCK_P",
                MD_BLOCK_P) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_BLOCK_TABLE",
                MD_BLOCK_TABLE) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_BLOCK_THEAD",
                MD_BLOCK_THEAD) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_BLOCK_TBODY",
                MD_BLOCK_TBODY) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_BLOCK_TR",
                MD_BLOCK_TR) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_BLOCK_TH",
                MD_BLOCK_TH) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_BLOCK_TD",
                MD_BLOCK_TD) < 0) {
        return -1;
    }
    return 0;
}

/*
 * Add MD_SPANTYPE enum constants
 */
int add_spantype_consts(PyObject *m) {
    if (PyModule_AddIntConstant(m, "MD_SPAN_EM",
                MD_SPAN_EM) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_SPAN_STRONG",
                MD_SPAN_STRONG) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_SPAN_A",
                MD_SPAN_A) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_SPAN_IMG",
                MD_SPAN_IMG) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_SPAN_CODE",
                MD_SPAN_CODE) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_SPAN_DEL",
                MD_SPAN_DEL) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_SPAN_LATEXMATH",
                MD_SPAN_LATEXMATH) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_SPAN_LATEXMATH_DISPLAY",
                MD_SPAN_LATEXMATH_DISPLAY) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_SPAN_WIKILINK",
                MD_SPAN_WIKILINK) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_SPAN_U",
                MD_SPAN_U) < 0) {
        return -1;
    }
    return 0;
}

/*
 * Add MD_TEXTTYPE enum constants
 */
int add_texttype_consts(PyObject *m) {
    if (PyModule_AddIntConstant(m, "MD_TEXT_NORMAL",
                MD_TEXT_NORMAL) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_TEXT_NULLCHAR",
                MD_TEXT_NULLCHAR) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_TEXT_BR",
                MD_TEXT_BR) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_TEXT_SOFTBR",
                MD_TEXT_SOFTBR) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_TEXT_ENTITY",
                MD_TEXT_ENTITY) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_TEXT_CODE",
                MD_TEXT_CODE) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_TEXT_HTML",
                MD_TEXT_HTML) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_TEXT_LATEXMATH",
                MD_TEXT_LATEXMATH) < 0) {
        return -1;
    }
    return 0;
}

/*
 * Add MD_ALIGN enum constants
 */
int add_align_consts(PyObject *m) {
    if (PyModule_AddIntConstant(m, "MD_ALIGN_DEFAULT",
                MD_ALIGN_DEFAULT) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_ALIGN_LEFT",
                MD_ALIGN_LEFT) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_ALIGN_CENTER",
                MD_ALIGN_CENTER) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_ALIGN_RIGHT",
                MD_ALIGN_RIGHT) < 0) {
        return -1;
    }
    return 0;
}

/******************************************************************************
 * Module-wide code                                                           *
 ******************************************************************************/

/*
 * Module Definition
 */
static PyModuleDef enum_consts_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "_enum_consts",
    .m_doc = "Python bindings for MD4C enum constants",
    .m_size = -1,
};

/*
 * Module initialization function
 */
PyMODINIT_FUNC PyInit__enum_consts(void)
{
    // Create the module object
    PyObject *m;
    m = PyModule_Create(&enum_consts_module);
    if (m == NULL) {
        return NULL;
    }

    // Add all the enum constants to the module
    if (add_blocktype_consts(m) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (add_spantype_consts(m) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (add_texttype_consts(m) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (add_align_consts(m) < 0) {
        Py_DECREF(m);
        return NULL;
    }

    return m;
}
