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
#include <stdbool.h>

#include <md4c.h>
#include "entity.h"

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
    unsigned int permissive_autolinks = 0;
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
        "permissive_autolinks",
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
                                     &permissive_autolinks, &no_html,
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

    if (permissive_autolinks) {
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
    bool is_bytes;
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
static PyObject * GenericParser_md_attribute(MD_ATTRIBUTE *attr,
        bool is_bytes) {
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
        PyObject *item = Py_BuildValue(is_bytes ? "(Oy#)" : "(Os#)",
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
        PyObject *python_callback, bool is_bytes) {
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
                Py_INCREF(Py_None);
                arglist = Py_BuildValue("(O{s:O})", get_enum_blocktype(type),
                        "fence_char", Py_None);
            } else {
                arglist = Py_BuildValue("(O{s:O,s:O,s:C})",
                        get_enum_blocktype(type),
                        "info", GenericParser_md_attribute(
                            &((MD_BLOCK_CODE_DETAIL *) detail)->info,
                            is_bytes),
                        "lang", GenericParser_md_attribute(
                            &((MD_BLOCK_CODE_DETAIL *) detail)->lang,
                            is_bytes),
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
            break;
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
            ((GenericParserCallbackData *) cb_data)->enter_block_callback,
            ((GenericParserCallbackData *) cb_data)->is_bytes);
}
static int GenericParser_leave_block(MD_BLOCKTYPE type, void *detail,
        void *cb_data) {
    return GenericParser_block(type, detail,
            ((GenericParserCallbackData *) cb_data)->leave_block_callback,
            ((GenericParserCallbackData *) cb_data)->is_bytes);
}
static int GenericParser_span(MD_SPANTYPE type, void *detail,
        PyObject *python_callback, bool is_bytes) {
    // Construct arguments
    PyObject *arglist;
    switch(type) {
        case MD_SPAN_A:
            arglist = Py_BuildValue("(O{s:O,s:O})", get_enum_spantype(type),
                    "href", GenericParser_md_attribute(
                        &((MD_SPAN_A_DETAIL *) detail)->href, is_bytes),
                    "title", GenericParser_md_attribute(
                        &((MD_SPAN_A_DETAIL *) detail)->title, is_bytes));
            break;
        case MD_SPAN_IMG:
            arglist = Py_BuildValue("(O{s:O,s:O})", get_enum_spantype(type),
                    "src", GenericParser_md_attribute(
                        &((MD_SPAN_IMG_DETAIL *) detail)->src, is_bytes),
                    "title", GenericParser_md_attribute(
                        &((MD_SPAN_IMG_DETAIL *) detail)->title, is_bytes));
            break;
        case MD_SPAN_WIKILINK:
            arglist = Py_BuildValue("(O{s:O})", get_enum_spantype(type),
                    "target", GenericParser_md_attribute(
                        &((MD_SPAN_WIKILINK_DETAIL *) detail)->target,
                        is_bytes));
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
            ((GenericParserCallbackData *) cb_data)->enter_span_callback,
            ((GenericParserCallbackData *) cb_data)->is_bytes);
}
static int GenericParser_leave_span(MD_SPANTYPE type, void *detail,
        void *cb_data) {
    return GenericParser_span(type, detail,
            ((GenericParserCallbackData *) cb_data)->leave_span_callback,
            ((GenericParserCallbackData *) cb_data)->is_bytes);
}
static int GenericParser_text(MD_TEXTTYPE type, const char *text, MD_SIZE size,
        void *cb_data) {
    // Construct arguments
    PyObject *arglist;
    if (((GenericParserCallbackData *) cb_data)->is_bytes) {
        arglist = Py_BuildValue("(Oy#)", get_enum_texttype(type), text, size);
    } else {
        arglist = Py_BuildValue("(Os#)", get_enum_texttype(type), text, size);
    }
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
    PyObject *input_obj;
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
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "OOOOOO:parse", kwlist,
                &input_obj,
                &cb_data.enter_block_callback,
                &cb_data.leave_block_callback,
                &cb_data.enter_span_callback,
                &cb_data.leave_span_callback,
                &cb_data.text_callback)) {
        return NULL;
    }

    // Extract contents of str or bytes
    if (PyBytes_AsStringAndSize(input_obj, (char **) &input, &in_size) < 0) {
        // str
        PyErr_Clear();
        input = PyUnicode_AsUTF8AndSize(input_obj, &in_size);
        if (input == NULL) {
            return NULL;
        }
        cb_data.is_bytes = false;
    } else {
        // bytes
        cb_data.is_bytes = true;
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

    // Make callback and input references owned
    Py_INCREF(input_obj);
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

    // Return callback and input references
    Py_DECREF(input_obj);
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
        "parse(markdown, enter_block_callback, leave_block_callback, "
        "enter_span_callback, leave_span_callback, text_callback)\n"
        "\n"
        "Parse a Markdown document using the provided callbacks for output\n"
        "\n"
        "Callbacks must all accept two parameters. The first describes the "
        "type of block, inline, or text. The second is a dict with details "
        "about the block or inline or a string/bytes containing the text "
        "itself. See :ref:`callbacks` for more information.\n"
        "\n"
        "If a callback raises :class:`StopParsing`, parsing will abort with "
        "no error. Any other exception will abort parsing and propagate back "
        "to the caller of this method.\n"
        "\n"
        ":param markdown: The Markdown text to parse. If provided as a "
        ":class:`bytes`, it must be UTF-8 encoded.\n"
        ":type markdown: str or bytes\n"
        ":param enter_block_callback: Callback to be called when the parser "
        "enters a new block element\n"
        ":type enter_block_callback: function or callable\n"
        ":param leave_block_callback: Callback to be called when the parser "
        "leaves a block element\n"
        ":type leave_block_callback: function or callable\n"
        ":param enter_span_callback: Callback to be called when the parser "
        "enters a new inline element\n"
        ":type enter_span_callback: function or callable\n"
        ":param leave_span_callback: Callback to be called when the parser "
        "leaves a inline element\n"
        ":type leave_span_callback: function or callable\n"
        ":param text_callback: Callback to be called when the parser has text "
        "to add to the current block or inline element\n"
        ":type text_callback: function or callable\n"
        ":raises ParseError: if there is a runtime error while parsing\n"
    },
    {NULL}
};

/*
 * GenericParser type object
 */
PyTypeObject GenericParserType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "md4c._md4c.GenericParser",
    .tp_doc = "GenericParser(parser_flags, **kwargs)\n"
        "\n"
        "SAX-like Markdown parser, implemented in C on top of the bare MD4C "
        "parser.\n"
        "\n"
        ":param parser_flags: Zero or more parser option flags OR'd together. "
        "See :ref:`options`.\n"
        ":type parser_flags: int, optional\n"
        "\n"
        "Option flags may also be specified in keyword-argument form for more "
        "readability. See :ref:`options`.\n",
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

/*
 * lookup_entity() function
 */

static unsigned int char_to_int(char c) {
    switch (c) {
        default:            return 0;
        case '1':           return 1;
        case '2':           return 2;
        case '3':           return 3;
        case '4':           return 4;
        case '5':           return 5;
        case '6':           return 6;
        case '7':           return 7;
        case '8':           return 8;
        case '9':           return 9;
        case 'A': case 'a': return 10;
        case 'B': case 'b': return 11;
        case 'C': case 'c': return 12;
        case 'D': case 'd': return 13;
        case 'E': case 'e': return 14;
        case 'F': case 'f': return 15;
    }
}

PyObject * lookup_entity(PyObject *self, PyObject *args) {
    // Parse arguments
    const char *entity;
    Py_ssize_t entity_size;
    if (!PyArg_ParseTuple(args, "s#", &entity, &entity_size)) {
        return NULL;
    }

    // Following code adapted from render_entity() in md4c-html.c
    PyObject *result;
    if (entity_size > 3 && entity[1] == '#') {
        // Numeric entity
        Py_UCS4 codepoint = 0;

        if (entity[2] == 'x' || entity[2] == 'X') {
            // Hex entity
            for (Py_ssize_t i = 3; i < entity_size - 1; i++) {
                codepoint = 16 * codepoint + char_to_int(entity[i]);
            }
        } else {
            // Decimal entity
            for (Py_ssize_t i = 2; i < entity_size - 1; i++) {
                codepoint = 10 * codepoint + char_to_int(entity[i]);
            }
        }

        result = PyUnicode_New(1, codepoint);
        if (result == NULL) {
            return NULL;
        }
        if (PyUnicode_WriteChar(result, 0, codepoint) < 0) {
            Py_DECREF(result);
            return NULL;
        }
        return result;
    } else {
        // Named entity
        const struct entity *ent = entity_lookup(entity, entity_size);
        if (ent == NULL) {
            // Not a valid entity
            result = PyTuple_GetItem(args, 0);
            Py_XINCREF(result);
            return result;
        } else if (ent->codepoints[1] == 0) {
            // Single-codepoint named entity
            result = PyUnicode_New(1, ent->codepoints[0]);
            if (result == NULL) {
                return NULL;
            }
            if (PyUnicode_WriteChar(result, 0, ent->codepoints[0]) < 0) {
                Py_DECREF(result);
                return NULL;
            }
            return result;
        } else {
            // Two-codepoint named entity
            unsigned int max_cp = (ent->codepoints[0] > ent->codepoints[1]) ?
                                  ent->codepoints[0] : ent->codepoints[1];
            result = PyUnicode_New(2, max_cp);
            if (result == NULL) {
                return NULL;
            }
            if (PyUnicode_WriteChar(result, 0, ent->codepoints[0]) < 0) {
                Py_DECREF(result);
                return NULL;
            }
            if (PyUnicode_WriteChar(result, 1, ent->codepoints[1]) < 0) {
                Py_DECREF(result);
                return NULL;
            }
            return result;
        }
    }
}
