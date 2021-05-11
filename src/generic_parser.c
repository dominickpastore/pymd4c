/*
 * PyMD4C
 * Python bindings for MD4C
 *
 * generic_parser.c - md4c._md4c.GenericParser class
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

#ifndef PY_SSIZE_T_CLEAN
#define PY_SSIZE_T_CLEAN
#endif
#include <Python.h>

#include <md4c.h>

#include "pymd4c.h"
#include "generic_parser.h"

/*
 * GenericParser "class"
 */
typedef struct {
    PyObject_HEAD
    unsigned int parser_flags;
} GenericParserObject;

/*
 * GenericParser.__init__(parser_flags: int)
 */
static int GenericParser_init(GenericParserObject *self, PyObject *args,
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
    unsigned int permissive_auto_links = 0;
    unsigned int no_html = 0;
    unsigned int dialect_github = 0;

    static char *kwlist[] = {
        "parser_flags",
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
        "permissive_auto_links",
        "no_html",
        "dialect_github",
        NULL
    };
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|I$ppppppppppppppppp",
                                     kwlist, &parser_flags,
                                     &collapse_whitespace,
                                     &permissive_atx_headers,
                                     &permissive_url_autolinks,
                                     &permissive_email_autolinks,
                                     &no_indented_code_blocks, &no_html_blocks,
                                     &no_html_spans, &tables, &strikethrough,
                                     &permissive_www_autolinks, &tasklists,
                                     &latex_math_spans, &wikilinks, &underline,
                                     &permissive_auto_links, &no_html,
                                     &dialect_github)) {
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

    if (permissive_auto_links) {
        parser_flags |= MD_FLAG_PERMISSIVEAUTOLINKS;
    }

    if (no_html) {
        parser_flags |= MD_FLAG_NOHTML;
    }

    if (dialect_github) {
        parser_flags |= MD_DIALECT_GITHUB;
    }

    self->parser_flags = parser_flags;
    return 0;
}

/*
 * GenericParser callback data
 * Stores the pointers to the Python callback functions and other data required
 * by the C callback functions
 */
typedef struct {
    PyObject *enter_block_callback;
    PyObject *leave_block_callback;
    PyObject *enter_span_callback;
    PyObject *leave_span_callback;
    PyObject *text_callback;
} GenericParserCallbackData;

/*
 * Helpers to get instances of the various enums
 */
static PyObject * get_enum_blocktype(int type) {
    // Get the module
    PyObject *enums = PyImport_AddModule(enums_module);
    if (enums == NULL) {
        return NULL;
    }
    // Get the enum class
    PyObject *type_enum = PyObject_GetAttrString(enums, "BlockType");
    if (type_enum == NULL) {
        return NULL;
    }
    // Instantiate the enum
    PyObject *instance = PyObject_CallFunction(type_enum, "(i)", type);
    if (instance == NULL) {
        Py_DECREF(type_enum);
        return NULL;
    }
    // Clean up and return
    Py_DECREF(type_enum);
    return instance;
}
static PyObject * get_enum_spantype(int type) {
    // Get the module
    PyObject *enums = PyImport_AddModule(enums_module);
    if (enums == NULL) {
        return NULL;
    }
    // Get the enum class
    PyObject *type_enum = PyObject_GetAttrString(enums, "SpanType");
    if (type_enum == NULL) {
        return NULL;
    }
    // Instantiate the enum
    PyObject *instance = PyObject_CallFunction(type_enum, "(i)", type);
    if (instance == NULL) {
        Py_DECREF(type_enum);
        return NULL;
    }
    // Clean up and return
    Py_DECREF(type_enum);
    return instance;
}
static PyObject * get_enum_texttype(int type) {
    // Get the module
    PyObject *enums = PyImport_AddModule(enums_module);
    if (enums == NULL) {
        return NULL;
    }
    // Get the enum class
    PyObject *type_enum = PyObject_GetAttrString(enums, "TextType");
    if (type_enum == NULL) {
        return NULL;
    }
    // Instantiate the enum
    PyObject *instance = PyObject_CallFunction(type_enum, "(i)", type);
    if (instance == NULL) {
        Py_DECREF(type_enum);
        return NULL;
    }
    // Clean up and return
    Py_DECREF(type_enum);
    return instance;
}
static PyObject * get_enum_align(int align) {
    // Get the module
    PyObject *enums = PyImport_AddModule(enums_module);
    if (enums == NULL) {
        return NULL;
    }
    // Get the enum class
    PyObject *align_enum = PyObject_GetAttrString(enums, "Align");
    if (align_enum == NULL) {
        return NULL;
    }
    // Instantiate the enum
    PyObject *instance = PyObject_CallFunction(align_enum, "(i)", align);
    if (instance == NULL) {
        Py_DECREF(align_enum);
        return NULL;
    }
    // Clean up and return
    Py_DECREF(align_enum);
    return instance;
}

/*
 * GenericParser Attribute Builder
 * Builds a list of 2-tuples (substr_type, substr_text) representing an
 * MD_ATTRIBUTE.
 * substr_type is a md4c.TextType Enum
 * and substr_text is a string
 *
 * If no MD_ATTRIBUTE is provided, that is, attr is NULL (can happen e.g. when
 * parsing an indented code block, which has no info string), returns None
 * instead.
 *
 * Return the list or None on success, NULL on failure
 */
static PyObject * GenericParser_md_attribute(MD_ATTRIBUTE *attr) {
    // If no MD_ATTRIBUTE, return None
    if (attr->text == NULL) {
        Py_RETURN_NONE;
    }

    // Init list
    PyObject *list = PyList_New(0);
    if (list == NULL) {
        return NULL;
    }

    // Add items
    for (int i = 0; attr->substr_offsets[i] != attr->size; i++) {
        // Init item
        PyObject *item = Py_BuildValue("(Os#)",
                get_enum_texttype(attr->substr_types[i]),
                attr->text + attr->substr_offsets[i],
                attr->substr_offsets[i + 1] - attr->substr_offsets[i]);
        if (item == NULL) {
            Py_DECREF(list);
            return NULL;
        }

        // Append item
        if (PyList_Append(list, item) < 0) {
            Py_DECREF(item);
            Py_DECREF(list);
            return NULL;
        }
    }

    return list;
}

/*
 * GenericParser C callbacks
 */
static int GenericParser_block(MD_BLOCKTYPE type, void *detail,
        PyObject *python_callback) {
    // Construct arguments
    PyObject *arglist;
    switch(type) {
        case MD_BLOCK_UL:
            arglist = Py_BuildValue("(O{s:N,s:C})", get_enum_blocktype(type),
                    "is_tight",
                    PyBool_FromLong(((MD_BLOCK_UL_DETAIL *) detail)->is_tight),
                    "mark", ((MD_BLOCK_UL_DETAIL *) detail)->mark);
            break;
        case MD_BLOCK_OL:
            arglist = Py_BuildValue("(O{s:I,s:N,s:C})",
                    get_enum_blocktype(type),
                    "start", ((MD_BLOCK_OL_DETAIL *) detail)->start,
                    "is_tight",
                    PyBool_FromLong(((MD_BLOCK_OL_DETAIL *) detail)->is_tight),
                    "mark_delimiter", ((MD_BLOCK_OL_DETAIL *) detail)->
                        mark_delimiter);
            break;
        case MD_BLOCK_LI:
            if (((MD_BLOCK_LI_DETAIL *) detail)->is_task) {
                arglist = Py_BuildValue("(O{s:O,s:C,s:I})",
                        get_enum_blocktype(type), "is_task", Py_True,
                        "task_mark",
                        ((MD_BLOCK_LI_DETAIL *) detail)->task_mark,
                        "task_mark_offset", ((MD_BLOCK_LI_DETAIL *) detail)->
                            task_mark_offset);
            } else {
                arglist = Py_BuildValue("(O{s:O})", get_enum_blocktype(type),
                        "is_task", Py_False);
            }
            break;
        case MD_BLOCK_H:
            arglist = Py_BuildValue("(O{s:I})", get_enum_blocktype(type),
                    "level", ((MD_BLOCK_H_DETAIL *) detail)->level);
            break;
        case MD_BLOCK_CODE:
            if (((MD_BLOCK_CODE_DETAIL *) detail)->fence_char == '\0') {
                arglist = Py_BuildValue("(O{s:O,s:O})",
                        get_enum_blocktype(type),
                        "info", GenericParser_md_attribute(
                            &((MD_BLOCK_CODE_DETAIL *) detail)->info),
                        "lang", GenericParser_md_attribute(
                            &((MD_BLOCK_CODE_DETAIL *) detail)->lang));
            } else {
                arglist = Py_BuildValue("(O{s:O,s:O,s:C})",
                        get_enum_blocktype(type),
                        "info", GenericParser_md_attribute(
                            &((MD_BLOCK_CODE_DETAIL *) detail)->info),
                        "lang", GenericParser_md_attribute(
                            &((MD_BLOCK_CODE_DETAIL *) detail)->lang),
                        "fence_char", ((MD_BLOCK_CODE_DETAIL *) detail)->
                            fence_char);
            }
            break;
        case MD_BLOCK_TABLE:
            arglist = Py_BuildValue("(O{s:I,s:I,s:I})",
                    get_enum_blocktype(type),
                    "col_count", ((MD_BLOCK_TABLE_DETAIL *) detail)->col_count,
                    "head_row_count", ((MD_BLOCK_TABLE_DETAIL *) detail)->
                        head_row_count,
                    "body_row_count", ((MD_BLOCK_TABLE_DETAIL *) detail)->
                        body_row_count);
        case MD_BLOCK_TH:
        case MD_BLOCK_TD:
            arglist = Py_BuildValue("(O{s:O})", get_enum_blocktype(type),
                    "align", get_enum_align(
                        ((MD_BLOCK_TD_DETAIL *) detail)->align));
            break;
        default:
            arglist = Py_BuildValue("(O{})", get_enum_blocktype(type));
    }
    if (arglist == NULL) {
        return -1;
    }

    // Call the Python callback
    PyObject *result = PyObject_CallObject(python_callback, arglist);
    Py_DECREF(arglist);
    if (result == NULL) {
        // Exception. Stop parsing. GenericParser.parse will check if the
        // exception was StopParsing.
        return -1;
    }

    // No error, continue parsing.
    Py_DECREF(result);
    return 0;
}
static int GenericParser_enter_block(MD_BLOCKTYPE type, void *detail,
        void *cb_data) {
    return GenericParser_block(type, detail,
            ((GenericParserCallbackData *) cb_data)->enter_block_callback);
}
static int GenericParser_leave_block(MD_BLOCKTYPE type, void *detail,
        void *cb_data) {
    return GenericParser_block(type, detail,
            ((GenericParserCallbackData *) cb_data)->leave_block_callback);
}
static int GenericParser_span(MD_SPANTYPE type, void *detail,
        PyObject *python_callback) {
    // Construct arguments
    PyObject *arglist;
    switch(type) {
        case MD_SPAN_A:
            arglist = Py_BuildValue("(O{s:O,s:O})", get_enum_spantype(type),
                    "href", GenericParser_md_attribute(
                        &((MD_SPAN_A_DETAIL *) detail)->href),
                    "title", GenericParser_md_attribute(
                        &((MD_SPAN_A_DETAIL *) detail)->title));
            break;
        case MD_SPAN_IMG:
            arglist = Py_BuildValue("(O{s:O,s:O})", get_enum_spantype(type),
                    "src", GenericParser_md_attribute(
                        &((MD_SPAN_IMG_DETAIL *) detail)->src),
                    "title", GenericParser_md_attribute(
                        &((MD_SPAN_IMG_DETAIL *) detail)->title));
            break;
        case MD_SPAN_WIKILINK:
            arglist = Py_BuildValue("(O{s:O})", get_enum_spantype(type),
                    "target", GenericParser_md_attribute(
                        &((MD_SPAN_WIKILINK_DETAIL *) detail)->target));
            break;
        default:
            arglist = Py_BuildValue("(O{})", get_enum_spantype(type));
    }
    if (arglist == NULL) {
        return -1;
    }

    // Call the Python callback
    PyObject *result = PyObject_CallObject(python_callback, arglist);
    Py_DECREF(arglist);
    if (result == NULL) {
        // Exception. Stop parsing. GenericParser.parse will check if the
        // exception was StopParsing.
        return -1;
    }

    // No error, continue parsing.
    Py_DECREF(result);
    return 0;
}
static int GenericParser_enter_span(MD_SPANTYPE type, void *detail,
        void *cb_data) {
    return GenericParser_span(type, detail,
            ((GenericParserCallbackData *) cb_data)->enter_span_callback);
}
static int GenericParser_leave_span(MD_SPANTYPE type, void *detail,
        void *cb_data) {
    return GenericParser_span(type, detail,
            ((GenericParserCallbackData *) cb_data)->leave_span_callback);
}
static int GenericParser_text(MD_TEXTTYPE type, const char *text, MD_SIZE size,
        void *cb_data) {
    // Construct arguments
    PyObject *arglist = Py_BuildValue("(Os#)", get_enum_texttype(type),
            text, size);
    if (arglist == NULL) {
        return -1;
    }

    // Call the Python callback
    PyObject *result = PyObject_CallObject(
            ((GenericParserCallbackData *) cb_data)->text_callback, arglist);
    Py_DECREF(arglist);
    if (result == NULL) {
        // Exception. Stop parsing. GenericParser.parse will check if the
        // exception was StopParsing.
        return -1;
    }

    // No error, continue parsing.
    Py_DECREF(result);
    return 0;
}

/*
 * GenericParser.parse(input: str,
 *     enter_block_callback: Callable[[BlockType, dict], None]
 *     leave_block_callback: Callable[[BlockType, dict], None],
 *     enter_span_callback: Callable[[SpanType, dict], None],
 *     leave_span_callback: Callable[[SpanType, dict], None],
 *     text_callback: Callable[[TextType, str], None]) -> None
 * Parse a Markdown document and call the callbacks
 */
static PyObject * GenericParser_parse(GenericParserObject *self,
        PyObject *args, PyObject *kwds) {
    // Parse arguments
    const char *input;
    Py_ssize_t in_size;
    GenericParserCallbackData cb_data;
    static char *kwlist[] = {
        "input",
        "enter_block_callback",
        "leave_block_callback",
        "enter_span_callback",
        "leave_span_callback",
        "text_callback",
        NULL
    };
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "s#OOOOO:parse", kwlist,
                &input, &in_size,
                &cb_data.enter_block_callback,
                &cb_data.leave_block_callback,
                &cb_data.enter_span_callback,
                &cb_data.leave_span_callback,
                &cb_data.text_callback)) {
        return NULL;
    }

    // Check that callbacks are all valid
    if (!PyCallable_Check(cb_data.enter_block_callback)) {
        PyErr_SetString(PyExc_TypeError,
                "enter_block_callback must be callable");
        return NULL;
    }
    if (!PyCallable_Check(cb_data.leave_block_callback)) {
        PyErr_SetString(PyExc_TypeError,
                "leave_block_callback must be callable");
        return NULL;
    }
    if (!PyCallable_Check(cb_data.enter_span_callback)) {
        PyErr_SetString(PyExc_TypeError,
                "enter_span_callback must be callable");
        return NULL;
    }
    if (!PyCallable_Check(cb_data.leave_span_callback)) {
        PyErr_SetString(PyExc_TypeError,
                "leave_span_callback must be callable");
        return NULL;
    }
    if (!PyCallable_Check(cb_data.text_callback)) {
        PyErr_SetString(PyExc_TypeError,
                "text_callback must be callable");
        return NULL;
    }

    // Make callback references owned
    Py_INCREF(cb_data.enter_block_callback);
    Py_INCREF(cb_data.leave_block_callback);
    Py_INCREF(cb_data.enter_span_callback);
    Py_INCREF(cb_data.leave_span_callback);
    Py_INCREF(cb_data.text_callback);

    // Do the parse
    MD_PARSER parser = {
        0,
        self->parser_flags,
        GenericParser_enter_block,
        GenericParser_leave_block,
        GenericParser_enter_span,
        GenericParser_leave_span,
        GenericParser_text,
        NULL,
        NULL
    };
    int result = md_parse(input, in_size, &parser, &cb_data);
    if (result != 0) {
        if (PyErr_Occurred()) {
            if (PyErr_ExceptionMatches(StopParsing)) {
                // StopParsing was raised. No error, just abort.
                PyErr_Clear();
                result = 0;
            }
            // Otherwise, some other exception was raised. Let it propagate.
        } else {
            // Error from MD4C: Raise an exception.
            PyErr_SetString(ParseError, "Error during parsing. "
                    "Perhaps out of memory?");
        }
    }

    // Return callback references
    Py_DECREF(cb_data.enter_block_callback);
    Py_DECREF(cb_data.leave_block_callback);
    Py_DECREF(cb_data.enter_span_callback);
    Py_DECREF(cb_data.leave_span_callback);
    Py_DECREF(cb_data.text_callback);

    // Return
    if (result == 0) {
        Py_INCREF(Py_None);
        return Py_None;
    } else {
        return NULL;
    }
}

/*
 * GenericParser helpers for garbage collection
 */
static int GenericParser_traverse(GenericParserObject *self, visitproc visit,
        void *arg) {
    return 0;
}
static int GenericParser_clear(GenericParserObject *self) {
    return 0;
}

/*
 * GenericParser destructor
 */
static void GenericParser_dealloc(GenericParserObject *self) {
    PyObject_GC_UnTrack(self);
    GenericParser_clear(self);
    Py_TYPE(self)->tp_free((PyObject *) self);
}

static PyMethodDef GenericParser_methods[] = {
    {"parse", (PyCFunction) GenericParser_parse, METH_VARARGS | METH_KEYWORDS,
        "Parse a Markdown document using the callbacks for output\n\n"
        "Block and span callbacks must accept two arguments:\n"
        "type - BlockType or SpanType Enum representing the block/span type\n"
        "details - A dict with extra attributes for certain block/span types\n"
        "\n"
        "Text callbacks must accept two different arguments:\n"
        "type - TextType Enum\n"
        "text - str with the text data\n\n"
        "All callbacks should return None but may raise exceptions.\n"
        "Raising StopParsing will abort parsing early with no error.\n"
        "Any other exception will be propagated back to the caller of this\n"
        "method."
    },
    {NULL}
};

/*
 * GenericParser type object
 */
PyTypeObject GenericParserType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "md4c._md4c.GenericParser",
    .tp_doc = "Generic MD4C Parser\n\n"
        "Parse Markdown documents using MD4C. This is the base parser-only\n"
        "class that requires callables to be used as callbacks. This is\n"
        "the slowest but most flexible way to parse.",
    .tp_basicsize = sizeof(GenericParserObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc) GenericParser_init,
    .tp_dealloc = (destructor) GenericParser_dealloc,
    .tp_traverse = (traverseproc) GenericParser_traverse,
    .tp_clear = (inquiry) GenericParser_clear,
    .tp_methods = GenericParser_methods,
};
