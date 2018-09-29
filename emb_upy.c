#include "emb.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "py/obj.h"
#include "py/compile.h"
#include "py/persistentcode.h"
#include "py/runtime.h"
#include "py/gc.h"
#include "py/stackctrl.h"

static const long heap_size = (1024 * 1024) * (sizeof(mp_uint_t) / 4);
static char* heap;

static int g_argc;
static char** g_argv;

STATIC void stderr_print_strn(void *env, const char *str, size_t len) {
    fwrite(str, 1, len, stderr);
}

static
const mp_print_t mp_stderr_print = {NULL, stderr_print_strn};

STATIC int handle_uncaught_exception(mp_obj_base_t *exc) {
    // Report all exceptions
    mp_obj_print_exception(&mp_stderr_print, MP_OBJ_FROM_PTR(exc));
    return 1;
}

//
// GLOBAL FUNCTION
//

STATIC mp_obj_t log_10(mp_obj_t x_obj) {
    mp_float_t x = mp_obj_get_float(x_obj);
    mp_float_t res = log10(x);
    return mp_obj_new_float(res);
    // return mp_const_none;
}

MP_DEFINE_CONST_FUN_OBJ_1(log_10_obj, log_10);

//
// GLOBAL DATA
//

typedef struct {
    int m_int_1;
    int m_int_2;
} GlobalStruct;

static
GlobalStruct g_global_struct = {
    .m_int_1 = 10,
    .m_int_2 = 20,
};

//
// UTILITIES
//

typedef struct {
    byte *bytes;
    long size;
} buffer;

static
void buffer_read_from_file(buffer *pBuffer, const char* const filename) {
    FILE* f = fopen(filename, "r");
    fseek(f, 0, SEEK_END);
    pBuffer->size = ftell(f);
    fseek(f, 0, SEEK_SET);
    pBuffer->bytes = malloc(pBuffer->size + 1 * sizeof(byte));
    fread(pBuffer->bytes, pBuffer->size, 1, f);
    fclose(f);
}

static
void buffer_free(buffer *pBuffer) {
    free(pBuffer->bytes);
}

static
void buffer_dump(buffer *pBuffer, FILE* f) {
    for (int i = 0; i < pBuffer->size; i++) {
        fprintf(f, "\\x%2.2x", pBuffer->bytes[i]);
    }
    fprintf(f, "\n");
}

//
// INTERPRETER
//

static
mp_parse_tree_t py_parse(const char* const str, long size) {
    qstr src_name = 1/*MP_QSTR_*/;
    mp_lexer_t *lex = mp_lexer_new_from_str_len(src_name, str, size, false);
    return mp_parse(lex, MP_PARSE_FILE_INPUT);
}

static
void save_mpy(mp_parse_tree_t pt, const char* const filename) {
    qstr src_name = 1/*MP_QSTR_*/;
    mp_raw_code_t *rc = mp_compile_to_raw_code(&pt, src_name, MP_EMIT_OPT_BYTECODE, false);
    mp_raw_code_save_file(rc, filename);
}

static
mp_obj_t load_mpy(buffer *pBuffer) {
    mp_raw_code_t *rc_loaded = mp_raw_code_load_mem(pBuffer->bytes, pBuffer->size);
    return mp_make_function_from_raw_code(rc_loaded, MP_OBJ_NULL, MP_OBJ_NULL);
}

static
mp_obj_t execute_mpy(mp_obj_t module_fun) {
    nlr_buf_t nlr;
    if (nlr_push(&nlr) == 0) {
        mp_call_function_0(module_fun);
        nlr_pop();
        return 0;
    } else {
        // uncaught exception
        handle_uncaught_exception((mp_obj_base_t*) nlr.ret_val);
        return (mp_obj_t)nlr.ret_val;
    }
}

static
mp_obj_t execute_py(const char* const str) {
    mp_parse_tree_t pt = py_parse(str, strlen(str));
    qstr src_name = 1/*MP_QSTR_*/;
    mp_obj_t module_fun = mp_compile(&pt, src_name, MP_EMIT_OPT_NONE, false);
    return execute_mpy(module_fun);
}

//
// SHELL
//

static
mp_obj_t meta_actions(const char* const str) {
    char action = str[0];
    switch(action) {
        // store mpy
        case 's':
            {
                char input[20];
                char output[20];
                sscanf(str + 1, " %s %s", input, output);
                fprintf(stderr, "args: '%s' '%s'\n", input, output);
                buffer py;
                buffer_read_from_file(&py, input);
                save_mpy(py_parse((char*) py.bytes, py.size), output);
                buffer_free(&py);
            }
            break;

        // execute mpy
        case 'e':
            {
                char input[20];
                sscanf(str + 1, " %s", input);
                fprintf(stderr, "args: '%s'\n", input);
                buffer mpy;
                buffer_read_from_file(&mpy, input);
                fprintf(stderr, "bytes:");
                buffer_dump(&mpy, stderr);
                mp_obj_t module_fun = load_mpy(&mpy);
                execute_mpy(module_fun);
                buffer_free(&mpy);
            }
            break;

        default:
            fprintf(stderr, "unknown action\n");
            exit(1);
    }

    return 0;
}

mp_obj_t execute_from_str(const char* const str) {
    if (str[0] == '\\') {
        return meta_actions(str + 1);
    }
    else
        return execute_py(str);
}


//
// PYTHON SETUP COMMANDS
//

static
const char* const commands[] = {
    "import uctypes",
    "buf = uctypes.bytearray_at(global_struct_ptr, global_struct_size)",
    "global_struct = uctypes.struct(uctypes.addressof(buf), {\"int_1\": uctypes.INT32 | 0, \"int_2\": uctypes.INT32 | 4})",
    0,
};


void setup_python() {
    for (const char* const* cmd = commands; *cmd; ++cmd) {
        execute_from_str(*cmd);
    }
}


int setup(int argc, char *argv[]) {
    g_argc = argc;
    g_argv = argv;

    // Initialized stack limit
    mp_stack_set_limit(40000 * (BYTES_PER_WORD / 4));

    // Initialize heap
    heap = (char*) malloc(heap_size);
    gc_init(heap, heap + heap_size);

    // Initialize interpreter
    mp_init();

    // Injects some globals
    mp_store_global(QSTR_FROM_STR_STATIC("log_10"), MP_OBJ_FROM_PTR(&log_10_obj));
    mp_store_global(QSTR_FROM_STR_STATIC("global_struct_ptr"), MP_ROM_INT(&g_global_struct));
    mp_store_global(QSTR_FROM_STR_STATIC("global_struct_size"), MP_ROM_INT(sizeof(g_global_struct)));
    
    setup_python();

    return 0;
}


int execute(const char* const command) {
    if (execute_from_str(command)) {
        return 1;
    }
    return 0;
}


static
int show_globals() {
    // UGLY FUNCTION just to check the final global state
    printf("float globals:\n");
    for (int idx = 1; idx < g_argc; idx++)
    {
        mp_map_elem_t *elem = mp_map_lookup(&mp_globals_get()->map, MP_OBJ_NEW_QSTR(QSTR_FROM_STR_STATIC(g_argv[idx])), MP_MAP_LOOKUP);
        printf("%s = ", g_argv[idx]);
        if (elem)
            printf("%.2f", mp_obj_get_float(elem->value));
        else
            printf("<UNDEF>");
        printf("\n");
    }
    return 0;
}


int teardown() {
    show_globals();
    gc_sweep_all();
    mp_deinit();
    free(heap);
    return 0;
}


// the following functions are duplicated (see ports/unix/main.c)
// see https://stackoverflow.com/a/37521541/2405599
// in short: an .o file in a lib is promoted to necessary if any function in it is necessary
//

mp_import_stat_t mp_import_stat(const char *path) {
    // limited implementation
    return MP_IMPORT_STAT_FILE;
}


void nlr_jump_fail(void *val) {
    printf("FATAL: uncaught NLR %p\n", val);
    exit(1);
}
