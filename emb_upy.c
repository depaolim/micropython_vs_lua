#include "emb.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "py/obj.h"
#include "py/compile.h"
#include "py/runtime.h"
#include "py/gc.h"
#include "py/stackctrl.h"

static const long heap_size = (1024 * 1024) * (sizeof(mp_uint_t) / 4);
static char* heap;

STATIC void stderr_print_strn(void *env, const char *str, size_t len) {
    fwrite(str, 1, len, stderr);
}

const mp_print_t mp_stderr_print = {NULL, stderr_print_strn};

STATIC int handle_uncaught_exception(mp_obj_base_t *exc) {
    // Report all exceptions
    mp_obj_print_exception(&mp_stderr_print, MP_OBJ_FROM_PTR(exc));
    return 1;
}

STATIC mp_obj_t log_10(mp_obj_t x_obj) {
    mp_float_t x = mp_obj_get_float(x_obj);
    mp_float_t res = log10(x);
    return mp_obj_new_float(res);
    // return mp_const_none;
}

MP_DEFINE_CONST_FUN_OBJ_1(log_10_obj, log_10);

mp_obj_t execute_from_str(const char* const str) {
    nlr_buf_t nlr;
    if (nlr_push(&nlr) == 0) {
        mp_lexer_t *lex = mp_lexer_new_from_str_len(0/*MP_QSTR_*/, str, strlen(str), false);
        mp_parse_tree_t pt = mp_parse(lex, MP_PARSE_FILE_INPUT);
        mp_obj_t module_fun = mp_compile(&pt, lex->source_name, MP_EMIT_OPT_NONE, false);
        mp_call_function_0(module_fun);
        nlr_pop();
        return 0;
    } else {
        // uncaught exception
        handle_uncaught_exception((mp_obj_base_t*) nlr.ret_val);
        return (mp_obj_t)nlr.ret_val;
    }
}


int setup(int argc, char *argv[]) {
    // Initialized stack limit
    mp_stack_set_limit(40000 * (BYTES_PER_WORD / 4));

    // Initialize heap
    heap = (char*) malloc(heap_size);
    gc_init(heap, heap + heap_size);

    // Initialize interpreter
    mp_init();

    mp_store_global(QSTR_FROM_STR_STATIC("log_10"), MP_OBJ_FROM_PTR(&log_10_obj));
    
    return 0;
}


int execute(const char* const command) {
    if (execute_from_str(command)) {
        return 1;
    }
    return 0;
}


int teardown() {
    gc_sweep_all();
    mp_deinit();
    free(heap);
    return 0;
}


// the following functions are duplicated (see ports/unix/main.c)
// see https://stackoverflow.com/a/37521541/2405599
// in short: an .o file in a lib is promoted to necessary if any function in it is necessary

mp_import_stat_t mp_import_stat(const char *path) {
    return MP_IMPORT_STAT_NO_EXIST;
}


void nlr_jump_fail(void *val) {
    printf("FATAL: uncaught NLR %p\n", val);
    exit(1);
}