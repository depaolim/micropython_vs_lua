#include <iostream>

#include <math.h>
#include <string.h>

extern "C" {
#include "py/obj.h"
#include "py/compile.h"
#include "py/runtime.h"
#include "py/gc.h"
#include "py/stackctrl.h"
}

#ifdef MP_CPP_DEBUG_ON
#include <csignal>
#define MP_CPP_DEBUG(msg)  std::cout << "DEBUG: " << msg << std::endl;
#else
#define MP_CPP_DEBUG(msg)
#endif

#define MP_CPP_DEFINE_CONST_FUN_OBJ_1(obj_name, fun_name) \
    const mp_obj_fun_builtin_fixed_t obj_name = \
        {&mp_type_fun_builtin_1, {_1: fun_name}};

static const long heap_size = (1024 * 1024) * (sizeof(mp_uint_t) / 4);
static const char* PROMPT = "> ";

STATIC void stderr_print_strn(void *env, const char *str, size_t len) {
    std::cerr << std::string(str, len);
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

MP_CPP_DEFINE_CONST_FUN_OBJ_1(log_10_obj, log_10);

mp_obj_t execute_from_str(const std::string& str) {
#ifdef MP_CPP_DEBUG_ON
    // usefull for gdb
    std::raise(SIGINT);
#endif

    nlr_buf_t nlr;
    if (nlr_push(&nlr) == 0) {
        mp_lexer_t *lex = mp_lexer_new_from_str_len(0/*MP_QSTR_*/, str.c_str(), str.length(), false);
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

// the following functions are duplicated (see ports/unix/main.c)
// see https://stackoverflow.com/a/37521541/2405599
// in short: an .o file in a lib is promoted to necessary if any function in it is necessary

int main(void) {
    std::cout << "micropython shell 0.0.1" << std::endl;
    std::cout << "Use Ctrl-D to exit" << std::endl;

    // Initialized stack limit
    mp_stack_set_limit(40000 * (BYTES_PER_WORD / 4));

    // Initialize heap
    char* heap = (char*) malloc(heap_size);
    gc_init(heap, heap + heap_size);

    // Initialize interpreter
    mp_init();

    MP_DECLARE_CONST_FUN_OBJ_1(log_10);
    mp_store_global(QSTR_FROM_STR_STATIC("log_10"), MP_OBJ_FROM_PTR(&log_10_obj));

    std::string line;
	std::cout << PROMPT;

    while (std::getline(std::cin, line)) {
        MP_CPP_DEBUG(line)
        if (execute_from_str(line)) {
            MP_CPP_DEBUG("CRASH")
            return 1;
        }
		std::cout << PROMPT;
    }

	std::cout << std::endl;

    gc_sweep_all();
    mp_deinit();
    free(heap);

    return 0;
}

mp_import_stat_t mp_import_stat(const char *path) {
    return MP_IMPORT_STAT_NO_EXIST;
}

void nlr_jump_fail(void *val) {
    printf("FATAL: uncaught NLR %p\n", val);
    exit(1);
}
