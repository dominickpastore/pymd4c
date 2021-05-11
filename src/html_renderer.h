/*
 * PyMD4C
 * Python bindings for MD4C
 *
 * html_renderer.h - md4c._md4c.HTMLRenderer class
 * Interfaces with MD4C's HTML renderer for fast rendering directly to HTML
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

#ifndef HTML_RENDERER_H
#define HTML_RENDERER_H

#ifndef PY_SSIZE_T_CLEAN
#define PY_SSIZE_T_CLEAN
#endif
#include <Python.h>

/*
 * HTMLRenderer type object
 */
extern PyTypeObject HTMLRendererType;

/*
 * Helper to add HTML renderer flags to the _md4c module. Return 0 on success,
 * -1 on error.
 */
int md4c_add_htmlrenderer_flags(PyObject *m);

#endif
