/*
 * PyMD4C
 * Python bindings for MD4C
 *
 * pymd4c.c - md4c._md4c module
 * Contains the parser and renderer classes that interface directly with MD4C
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

#include <stdlib.h>
#include <string.h>
#include <errno.h>

#include <md4c.h>
#include <md4c-html.h>

/*
 * Name of enums module to import
 */
static const char *enums_module = "md4c._enums";

/*
 * Exception objects
 */
static PyObject *ParseError;
static PyObject *StopParsing;

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
    unsigned int renderer_flags = 0;
    
    static char *kwlist[] = {"parser_flags", "renderer_flags", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|II", kwlist,
            &parser_flags, &renderer_flags)) {
        return -1;
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
static PyObject * HTMLRenderer_parse(HTMLRendererObject *self, PyObject *args) {
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
        "Parse a Markdown document and return the rendered HTML"
    },
    {NULL}
};

/*
 * HTMLRenderer type object
 */
static PyTypeObject HTMLRendererType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "md4c._md4c.HTMLRenderer",
    .tp_doc = "HTML MD4C Parser\n\n"
        "Parse markdown documents with MD4C and render them in HTML",
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
 * MD4C generic parsing-only class                                            *
 ******************************************************************************/

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
    
    static char *kwlist[] = {"parser_flags", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|I", kwlist, &parser_flags)) {
        return -1;
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
                    "is_tight", PyBool_FromLong(((MD_BLOCK_UL_DETAIL *) detail)->is_tight),
                    "mark", ((MD_BLOCK_UL_DETAIL *) detail)->mark);
            break;
        case MD_BLOCK_OL:
            arglist = Py_BuildValue("(O{s:i,s:N,s:C})",
                    get_enum_blocktype(type),
                    "start", ((MD_BLOCK_OL_DETAIL *) detail)->start,
                    "is_tight", PyBool_FromLong(((MD_BLOCK_OL_DETAIL *) detail)->is_tight),
                    "mark_delimiter", ((MD_BLOCK_OL_DETAIL *) detail)->
                        mark_delimiter);
            break;
        case MD_BLOCK_LI:
            if (((MD_BLOCK_LI_DETAIL *) detail)->is_task) {
                arglist = Py_BuildValue("(O{s:O,s:C,s:i})", get_enum_blocktype(type),
                        "is_task", Py_True,
                        "task_mark", ((MD_BLOCK_LI_DETAIL *) detail)->task_mark,
                        "task_mark_offset", ((MD_BLOCK_LI_DETAIL *) detail)->
                            task_mark_offset);
            } else {
                arglist = Py_BuildValue("(O{s:O})", get_enum_blocktype(type),
                        "is_task", Py_False);
            }
            break;
        case MD_BLOCK_H:
            arglist = Py_BuildValue("(O{s:i})", get_enum_blocktype(type),
                    "level", ((MD_BLOCK_H_DETAIL *) detail)->level);
            break;
        case MD_BLOCK_CODE:
            if (((MD_BLOCK_CODE_DETAIL *) detail)->fence_char == NULL) {
                arglist = Py_BuildValue("(O{s:O,s:O})", get_enum_blocktype(type),
                        "info", GenericParser_md_attribute(
                            &((MD_BLOCK_CODE_DETAIL *) detail)->info),
                        "lang", GenericParser_md_attribute(
                            &((MD_BLOCK_CODE_DETAIL *) detail)->lang));
            } else {
                arglist = Py_BuildValue("(O{s:O,s:O,s:C})", get_enum_blocktype(type),
                        "info", GenericParser_md_attribute(
                            &((MD_BLOCK_CODE_DETAIL *) detail)->info),
                        "lang", GenericParser_md_attribute(
                            &((MD_BLOCK_CODE_DETAIL *) detail)->lang),
                        "fence_char", ((MD_BLOCK_CODE_DETAIL *) detail)->
                            fence_char);
            }
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

static PyTypeObject GenericParserType = {
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

/******************************************************************************
 * Module-wide code                                                           *
 ******************************************************************************/

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
            "Raised when an error occurs during parsing.", NULL, NULL);
    Py_XINCREF(ParseError);
    if (PyModule_AddObject(m, "ParseError", ParseError) < 0) {
        Py_XDECREF(ParseError);
        Py_CLEAR(ParseError);
        Py_DECREF(m);
        return NULL;
    }
    // Add the ParseError exception to the module
    StopParsing = PyErr_NewExceptionWithDoc("md4c._md4c.StopParsing",
            "Raised to stop parsing before complete.", NULL, NULL);
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
