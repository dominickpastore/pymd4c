#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <errno.h>

// For mutex support
#if defined(_WIN32)
#include <windows.h>
#elif defined(__unix__)
#include <unistd.h>
#elif defined(unix) || defined(__unix)
#define __unix__
#include <unistd.h>
#endif

#include <md4c.h>
#include <md4c_html.h>

static PyObject *ParseError;

/******************************************************************************
 * Cross-platform synchronization                                             *
 ******************************************************************************/

//pthreads
#define MUTEX_OBJ pthread_mutex_t

pthread_mutex_t mutex;
//All return zero on success, errno on fail
pthread_mutex_init(&mutex, NULL);
pthread_mutex_destroy(&mutex); //must be unlocked
pthread_mutex_lock(&mutex);
pthread_mutex_unlock(&mutex);

//win32
#define MUTEX_OBJ CRITICAL_SECTION

CRITICAL_SECTION mutex;
//All return nothing
InitializeCritialSection(&mutex);
DeleteCriticalSection(&mutex); //must be unlocked
EnterCriticalSection(&mutex);
LeaveCriticalSection(&mutex);

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
    const char *output;
    Py_ssize_t out_size;
#if defined(_WIN32)
    CRITICAL_SECTION out_mutex;
#elif defined(__unix__)
    pthread_mutex_t out_mutex;
#endif
} HTMLRendererObject;

/*
 * HTMLRenderer __init__
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

#if defined(_WIN32)
    InitializeCriticalSection(&self->out_mutex);
#elif defined(__unix__)
    int sts = pthread_mutex_init(&self->out_mutex);
    if (sts != 0) {
        errno = sts;
        PyErr_SetFromErrno(PyExc_OSError);
        return -1;
    }
#endif
}

static void HTMLRenderer_parse_callback(const char *output,
        MD_SIZE out_size, void *self_void) {
    HTMLRendererObject *self = self_void;
    self->output = output;
    self->out_size = out_size;
}

/*
 * HTMLRenderer.parse(input: str) -> str
 * Parse a Markdown document and return the rendered HTML
 */
static PyObject * HTMLRenderer_parse(HTMLRendererObject *self, PyObject *args) {
    PyThreadState *_save;
    int mutex_sts;

    // Parse arguments
    const char *input;
    Py_ssize_t in_size;
    if (!PyArg_ParseTuple(args, "s#", &input, &in_size)) {
        return NULL;
    }

    // Lock the mutex
#if defined(_WIN32)
    Py_UNBLOCK_THREADS
    EnterCriticalSection(&self->out_mutex);
#elif defined(__unix__)
    Py_UNBLOCK_THREADS
    mutex_sts = pthread_mutex_lock(&self->out_mutex);
    if (mutex_sts != 0) {
        Py_BLOCK_THREADS
        errno = mutex_sts;
        PyErr_SetFromErrno(PyExc_OSError);
        return NULL;
    }
#endif

    // Do the parse
    int sts = md_html(input, in_size, HTMLRenderer_parse_callback,
            self, self->parser_flags, self->renderer_flags);
    // Store values before unlocking mutex
    const char *output = self->output;
    Py_ssize_t out_size = self->out_size;

    // Unlock the mutex
#if defined(_WIN32)
    LeaveCriticalSection(&self->out_mutex);
    Py_BLOCK_THREADS
#elif defined(__unix__)
    mutex_sts = pthread_mutex_unlock(&self->out_mutex);
    if (mutex_sts != 0) {
        Py_BLOCK_THREADS
        errno = mutex_sts;
        PyErr_SetFromErrno(PyExc_OSError);
        Py_DECREF(result);
        return NULL;
    }
    Py_BLOCK_THREADS
#endif

    // Return
    if (sts < 0) {
        PyErr_SetString(ParseError, "Could not parse markdown");
        return NULL;
    }
    PyObject *result = Py_BuildValue("s#", self->output, self->out_size);
    if (result == NULL) {
        return NULL;
    }
    return result;
}

/*
 * HTMLRenderer helpers for garbage collection
 */
static int HTMLRenderer_traverse(HTTPRenderer *self, visitproc visit,
        void *arg) {
    return 0;
}
static int HTMLRenderer_clear(HTMLRenderer *self) {
    return 0;
}

/*
 * HTMLRenderer destructor
 */
static void HTMLRenderer_dealloc(HTMLRendererObject *self) {
    // Free mutex
#if defined(_WIN32)
    DeleteCriticalSection(&self->out_mutex);
#elif defined(__unix__)
    pthread_mutex_destroy(&self->out_mutex);
#endif

    PyObject_GC_UnTrack(self);
    HTMLRenderer_clear(self);
    Py_TYPE(self)->tp_free((PyObject *) self);
}

static PyMethodDef HTMLRenderer_methods[] = {
    {"parse", (PyCFunction) HTMLRenderer_parse, METH_NOARGS,
        "Parse a Markdown document and return the rendered HTML"
    },
    {NULL}
}

/*
 * HTMLRenderer type object
 */
static PyTypeObject HTMLRendererType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "md4c.HTMLRenderer",
    .tp_doc = "HTML MD4C Parser\n\n"
        "Parse markdown documents with MD4C and render them in HTML",
    .tp_basicsize = sizeof(HTMLRendererObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC,
    .tp_new = PyType_GenericNew,
    .tp_init = (initproc) HTMLRenderer_init,
    .tp_dealloc = (destructor) HTMLRenderer_dealloc,
    .tp_methods = HTMLRenderer_methods,
};

/******************************************************************************
 * MD4C parsing-only class. TODO Accept callables for all the callbacks that  *
 *   MD4C accepts and call them when the C callbacks are called.              *
 *                                                                            *
 * TODO Make HTMLRenderer a subclass of this.                                 *
 * TODO Produce another subclass that instead of accepting callables,         *
 *   produces a MD4CDocument. Call it DocumentParser                           *
 ******************************************************************************/

/* TODO Below is a very basic version of this class. It needs to be reviewed
 * and made into a superclass of MD4C_HTMLRenderer.

typedef struct {
    PyObject_HEAD
    //TODO Parser flags
} GenericParserObject;

statuc PyTypeObject GenericParserType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "md4c.GenericParser",
    .tp_doc = "Generic MD4C Parser\n\n"
        "Parse Markdown documents using MD4C. This is the base parser-only\n"
        "class that requires callables to be used as callbacks. This is\n"
        "the slowest but most flexible way to parse.",
    .tp_basicsize = sizeof(GenericParserObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_new = PyType_GenericNew,
};
*/

/******************************************************************************
 * Module-wide code                                                           *
 ******************************************************************************/

/*
 * Module Definition
 */
static PyModuleDef md4c_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "md4c",
    .m_doc = "Python bindings for MD4C (https://github.com/mity/md4c)",
    .m_size = -1,
};

/*
 * Module initialization function
 */
PyMODINIT_FUNC PyInit_md4c(void)
{
    // Initialize the types in the module
    if (PyType_Ready(&HTMLRendererType) < 0) {
        return NULL;
    }

    // Create the module object
    PyObject *m;
    m = PyModule_Create(&md4c_module);
    if (m == NULL) {
        return NULL;
    }

    // Add the flag constants to the module
    if (PyModule_AddIntConstant(m, "MD_FLAG_COLLAPSEWHITESPACE",
                MD_FLAG_COLLAPSEWHITESPACE) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_PERMISSIVEATXHEADERS",
                MD_FLAG_PERMISSIVEATXHEADERS) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_PERMISSIVEURLAUTOLINKS",
                MD_FLAG_PERMISSIVEURLAUTOLINKS) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_PERMISSIVEEMAILAUTOLINKS",
                MD_FLAG_PERMISSIVEEMAILAUTOLINKS) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_NOINDENTEDCODEBLOCKS",
                MD_FLAG_NOINDENTEDCODEBLOCKS) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_NOHTMLBLOCKS",
                MD_FLAG_NOHTMLBLOCKS) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_NOHTMLSPANS",
                MD_FLAG_NOHTMLSPANS) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_TABLES",
                MD_FLAG_TABLES) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_STRIKETHROUGH",
                MD_FLAG_STRIKETHROUGH) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_PERMISSIVEWWWAUTOLINKS",
                MD_FLAG_PERMISSIVEWWWAUTOLINKS) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_TASKLISTS",
                MD_FLAG_TASKLISTS) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_LATEXMATHSPANS",
                MD_FLAG_LATEXMATHSPANS) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_WIKILINKS",
                MD_FLAG_WIKILINKS) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_UNDERLINE",
                MD_FLAG_UNDERLINE) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_PERMISSIVEAUTOLINKS",
                MD_FLAG_PERMISSIVEAUTOLINKS) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddIntConstant(m, "MD_FLAG_NOHTML",
                MD_FLAG_NOHTML) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddIntConstant(m, "MD_DIALECT_COMMONMARK",
                MD_DIALECT_COMMONMARK) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddIntConstant(m, "MD_DIALECT_GITHUB",
                MD_DIALECT_GITHUB) < 0) {
        Py_DECREF(m);
        return NULL;
    }

    // Add the HTML renderer flags to the module
    if (PyModule_AddIntConstant(m, "MD_HTML_FLAG_DEBUG",
                MD_HTML_FLAG_DEBUG) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddIntConstant(m, "MD_HTML_FLAG_VERBATIM_ENTITIES",
                MD_HTML_FLAG_VERBATIM_ENTITIES) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    if (PyModule_AddIntConstant(m, "MD_HTML_FLAG_SKIP_UTF8_BOM",
                MD_HTML_FLAG_SKIP_UTF8_BOM) < 0) {
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

    // Add the ParseError exception to the module
    ParseError = PyErr_NewException("md4c.ParseError", NULL, NULL);
    Py_XINCREF(ParseError);
    if (PyModule_AddObject(m, "ParseError", ParseError) < 0) {
        Py_XDECREF(ParseError);
        Py_CLEAR(ParseError);
        Py_DECREF(&HTMLRendererType);
        Py_DECREF(m);
        return NULL;
    }

    return m;
}
