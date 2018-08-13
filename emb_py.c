#include <stdio.h>

#include "emb.h"

#include <Python.h>

static wchar_t *program;
static PyObject *dict;


static void print_exception() {
    PyObject *exception, *value, *tb;
    PyErr_Fetch(&exception, &value, &tb);
    if (exception == NULL)
        return;
    PyErr_NormalizeException(&exception, &value, &tb);
    if (exception == NULL)
        return;
    PyObject *type = (PyObject *) Py_TYPE(value);
    const char *className = PyExceptionClass_Name(type);
    fprintf(stderr, "%s\n", className);
    PyErr_Clear();
    Py_XDECREF(exception);
    Py_XDECREF(value);
    Py_XDECREF(tb);
}


int setup(int argc, char *argv[]) {
    program = Py_DecodeLocale(argv[0], NULL);
    if (program == NULL) {
        fprintf(stderr, "%s\n", "Fatal error: cannot decode argv[0]");
        return 1;
    }
    Py_SetProgramName(program);  /* optional but recommended */
    Py_Initialize();
    PyObject *module;
    module = PyImport_AddModule("__main__");
    if (module == NULL)
        return -1;
    dict = PyModule_GetDict(module);
    return 0;
}


int teardown() {
    if (Py_FinalizeEx() < 0)
        return 120;
    PyMem_RawFree(program);
    return 0;
}


int execute(const char* const command) {
    PyObject *v = PyRun_StringFlags(command, Py_file_input, dict, dict, NULL);
    if (v == NULL) {
        print_exception();
        return -1;
    }
    Py_DECREF(v);
    return 0;
}
