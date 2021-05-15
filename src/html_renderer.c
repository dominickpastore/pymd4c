/*
 * PyMD4C
 * Python bindings for MD4C
 *
 * html_renderer.c - md4c._md4c.HTMLRenderer class
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

#ifndef PY_SSIZE_T_CLEAN
#define PY_SSIZE_T_CLEAN
#endif
#include <Python.h>

#include <stdlib.h>
#include <string.h>

#include <md4c.h>
#include <md4c-html.h>

#include "pymd4c.h"
#include "html_renderer.h"

/******************************************************************************
 * Buffer functions                                                           *
 ******************************************************************************/

#define DYNAMICBUFFER_INITSIZE 256

typedef struct {
    char *data;
    size_t pos;
    size_t len;
} DynamicBuffer;

/*
 * Initialize a DynamicBuffer. Return 0 on success, -1 on failure.
 */
static int buffer_init(DynamicBuffer *buf) {
    buf->data = malloc(DYNAMICBUFFER_INITSIZE);
    if (buf->data == NULL) {
        return -1;
    }
    buf->pos = 0;
    buf->len = DYNAMICBUFFER_INITSIZE;
    return 0;
}

/*
 * Double the size of the DynamicBuffer. Return 0 on success, -1 on failure.
 */
static int buffer_grow(DynamicBuffer *buf) {
    size_t new_len = buf->len * 2;
    char *new_data = realloc(buf->data, new_len);
    if (new_data == NULL) {
        return -1;
    }
    buf->data = new_data;
    buf->len = new_len;
    return 0;
}

/*
 * Append data to a DynamicBuffer. Return 0 on success, -1 on failure.
 */
static int buffer_append(DynamicBuffer *buf, const char *data, size_t len) {
    // Grow if necessary
    while (len > (buf->len - buf->pos)) {
        if (buffer_grow(buf) < 0) {
            return -1;
        }
    }

    // Append
    memcpy(buf->data + buf->pos, data, len);
    buf->pos += len;
    return 0;
}

/*
 * Free the DynamicBuffer
 */
static void buffer_free(DynamicBuffer *buf) {
    free(buf->data);
}

/******************************************************************************
 * HTML renderer class                                                        *
 ******************************************************************************/

/*
 * HTMLRenderer "class"
 */
typedef struct {
    PyObject_HEAD
    unsigned int parser_flags;
    unsigned int renderer_flags;
} HTMLRendererObject;

/*
 * HTMLRenderer.__init__(parser_flags: int, renderer_flags: int)
 */
static int HTMLRenderer_init(HTMLRendererObject *self, PyObject *args,
        PyObject *kwds) {
    unsigned int parser_flags = 0;
    unsigned int collapse_whitespace = 0;
    unsigned int permissive_atx_headers = 0;
    unsigned int permissive_url_autolinks = 0;
    unsigned int permissive_email_autolinks = 0;
    unsigned int no_indented_code_blocks = 0;
    unsigned int no_html_blocks = 0;
    unsigned int no_html_spans = 0;
    unsigned int tables = 0;
    unsigned int strikethrough = 0;
    unsigned int permissive_www_autolinks = 0;
    unsigned int tasklists = 0;
    unsigned int latex_math_spans = 0;
    unsigned int wikilinks = 0;
    unsigned int underline = 0;
    unsigned int permissive_autolinks = 0;
    unsigned int no_html = 0;
    unsigned int dialect_github = 0;

    unsigned int renderer_flags = 0;
    unsigned int debug = 0;
    unsigned int verbatim_entities = 0;
    unsigned int skip_utf8_bom = 0;
    unsigned int xhtml = 0;

    static char *kwlist[] = {
        "parser_flags",
        "renderer_flags",
        "collapse_whitespace",
        "permissive_atx_headers",
        "permissive_url_autolinks",
        "permissive_email_autolinks",
        "no_indented_code_blocks",
        "no_html_blocks",
        "no_html_spans",
        "tables",
        "strikethrough",
        "permissive_www_autolinks",
        "tasklists",
        "latex_math_spans",
        "wikilinks",
        "underline",
        "permissive_autolinks",
        "no_html",
        "dialect_github",
        "debug",
        "verbatim_entities",
        "skip_utf8_bom",
        "xhtml",
        NULL,
    };
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|II$ppppppppppppppppppppp",
                                     kwlist, &parser_flags, &renderer_flags,
                                     &collapse_whitespace,
                                     &permissive_atx_headers,
                                     &permissive_url_autolinks,
                                     &permissive_email_autolinks,
                                     &no_indented_code_blocks, &no_html_blocks,
                                     &no_html_spans, &tables, &strikethrough,
                                     &permissive_www_autolinks, &tasklists,
                                     &latex_math_spans, &wikilinks, &underline,
                                     &permissive_autolinks, &no_html,
                                     &dialect_github,
                                     &debug, &verbatim_entities,
                                     &skip_utf8_bom, &xhtml)) {
        return -1;
    }

    if (collapse_whitespace) {
        parser_flags |= MD_FLAG_COLLAPSEWHITESPACE;
    }

    if (permissive_atx_headers) {
        parser_flags |= MD_FLAG_PERMISSIVEATXHEADERS;
    }

    if (permissive_url_autolinks) {
        parser_flags |= MD_FLAG_PERMISSIVEURLAUTOLINKS;
    }

    if (permissive_email_autolinks) {
        parser_flags |= MD_FLAG_PERMISSIVEEMAILAUTOLINKS;
    }

    if (no_indented_code_blocks) {
        parser_flags |= MD_FLAG_NOINDENTEDCODEBLOCKS;
    }

    if (no_html_blocks) {
        parser_flags |= MD_FLAG_NOHTMLBLOCKS;
    }

    if (no_html_spans) {
        parser_flags |= MD_FLAG_NOHTMLSPANS;
    }

    if (tables) {
        parser_flags |= MD_FLAG_TABLES;
    }

    if (strikethrough) {
        parser_flags |= MD_FLAG_STRIKETHROUGH;
    }

    if (permissive_www_autolinks) {
        parser_flags |= MD_FLAG_PERMISSIVEWWWAUTOLINKS;
    }

    if (tasklists) {
        parser_flags |= MD_FLAG_TASKLISTS;
    }

    if (latex_math_spans) {
        parser_flags |= MD_FLAG_LATEXMATHSPANS;
    }

    if (wikilinks) {
        parser_flags |= MD_FLAG_WIKILINKS;
    }

    if (underline) {
        parser_flags |= MD_FLAG_UNDERLINE;
    }

    if (permissive_autolinks) {
        parser_flags |= MD_FLAG_PERMISSIVEAUTOLINKS;
    }

    if (no_html) {
        parser_flags |= MD_FLAG_NOHTML;
    }

    if (dialect_github) {
        parser_flags |= MD_DIALECT_GITHUB;
    }

    if (debug) {
        renderer_flags |= MD_HTML_FLAG_DEBUG;
    }

    if (verbatim_entities) {
        renderer_flags |= MD_HTML_FLAG_VERBATIM_ENTITIES;
    }

    if (skip_utf8_bom) {
        renderer_flags |= MD_HTML_FLAG_SKIP_UTF8_BOM;
    }

    if (xhtml) {
        renderer_flags |= MD_HTML_FLAG_XHTML;
    }

    self->parser_flags = parser_flags;
    self->renderer_flags = renderer_flags;
    return 0;
}

/*
 * MD4C HTML callback. Appends to the buffer.
 */
static void HTMLRenderer_parse_callback(const char *output,
        MD_SIZE out_size, void *buf) {
    buffer_append(buf, output, out_size);
}

/*
 * HTMLRenderer.parse(input: str) -> str
 * Parse a Markdown document and return the rendered HTML
 */
static PyObject * HTMLRenderer_parse(HTMLRendererObject *self,
        PyObject *args) {
    PyThreadState *_save;

    // Parse arguments
    const char *input;
    Py_ssize_t in_size;
    if (!PyArg_ParseTuple(args, "s#", &input, &in_size)) {
        return NULL;
    }

    // Do the parse
    Py_UNBLOCK_THREADS
    DynamicBuffer buf;
    if (buffer_init(&buf) < 0) {
        PyErr_SetFromErrno(PyExc_OSError);
        return NULL;
    }
    int sts = md_html(input, in_size, HTMLRenderer_parse_callback,
            &buf, self->parser_flags, self->renderer_flags);
    Py_BLOCK_THREADS

    // Return
    if (sts < 0) {
        PyErr_SetString(ParseError, "Could not parse markdown");
        return NULL;
    }
    PyObject *result = Py_BuildValue("s#", buf.data, buf.pos);
    if (result == NULL) {
        return NULL;
    }
    buffer_free(&buf);
    return result;
}

/*
 * HTMLRenderer helpers for garbage collection
 */
static int HTMLRenderer_traverse(HTMLRendererObject *self, visitproc visit,
        void *arg) {
    return 0;
}
static int HTMLRenderer_clear(HTMLRendererObject *self) {
    return 0;
}

/*
 * HTMLRenderer destructor
 */
static void HTMLRenderer_dealloc(HTMLRendererObject *self) {
    PyObject_GC_UnTrack(self);
    HTMLRenderer_clear(self);
    Py_TYPE(self)->tp_free((PyObject *) self);
}

static PyMethodDef HTMLRenderer_methods[] = {
    {"parse", (PyCFunction) HTMLRenderer_parse, METH_VARARGS,
        "parse(markdown)\n"
        "\n"
        "Parse a Markdown document and return the rendered HTML.\n"
        "\n"
        ":param markdown: The Markdown text to parse. If provided as a "
        ":class:`bytes`, it must be UTF-8 encoded.\n"
        ":type markdown: str or bytes\n"
        ":return: The generated HTML\n"
        ":rtype: str\n"
        ":raises ParseError: if there is a runtime error while parsing\n"
    },
    {NULL}
};

/*
 * HTMLRenderer type object
 */
PyTypeObject HTMLRendererType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "md4c._md4c.HTMLRenderer",
    .tp_doc = "HTMLRenderer(parser_flags, renderer_flags, **kwargs)\n"
        "\n"
        "A class to convert Markdown to HTML, implemented in C on top "
        "of the MD4C-HTML library. This is the fastest way to convert "
        "Markdown to HTML with PyMD4C.\n"
        "\n"
        ":param parser_flags: Zero or more parser option flags OR'd together. "
        "See :ref:`options`.\n"
        ":type parser_flags: int, optional\n"
        ":param renderer_flags: Zero or more HTML renderer option flags OR'd "
        "together. See :ref:`options`.\n"
        ":type renderer_flags: int, optional\n"
        "\n"
        "Option flags may also be specified in keyword-argument form for more "
        "readability. See :ref:`options`.\n",
    .tp_basicsize = sizeof(HTMLRendererObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc) HTMLRenderer_init,
    .tp_dealloc = (destructor) HTMLRenderer_dealloc,
    .tp_traverse = (traverseproc) HTMLRenderer_traverse,
    .tp_clear = (inquiry) HTMLRenderer_clear,
    .tp_methods = HTMLRenderer_methods,
};

/******************************************************************************
 * Module-wide initialization related to HTMLRenderer                         *
 ******************************************************************************/

/*
 * Helper to add HTML renderer flags to the _md4c module. Return 0 on success,
 * -1 on error.
 */
int md4c_add_htmlrenderer_flags(PyObject *m) {
    // Add the HTML renderer option flags
    if (PyModule_AddIntConstant(m, "MD_HTML_FLAG_DEBUG",
                MD_HTML_FLAG_DEBUG) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_HTML_FLAG_VERBATIM_ENTITIES",
                MD_HTML_FLAG_VERBATIM_ENTITIES) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_HTML_FLAG_SKIP_UTF8_BOM",
                MD_HTML_FLAG_SKIP_UTF8_BOM) < 0) {
        return -1;
    }
    if (PyModule_AddIntConstant(m, "MD_HTML_FLAG_XHTML",
                MD_HTML_FLAG_XHTML) < 0) {
        return -1;
    }

    return 0;
}
