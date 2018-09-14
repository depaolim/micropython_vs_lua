// Include required definitions first.
#include "py/obj.h"
#include "py/objint.h"
#include "py/runtime.h"


// This is the function you will call using example.double(n).
STATIC mp_obj_t example_double(mp_obj_t x_obj) {
    // Check input value and convert it to a C type.
    if (!MP_OBJ_IS_SMALL_INT(x_obj)) {
        mp_raise_ValueError("x is not a small int");
    }
    int x = mp_obj_int_get_truncated(x_obj);

    // Calculate the double, and convert back to MicroPython object.
    return mp_obj_new_int(x + x);
}


STATIC MP_DEFINE_CONST_FUN_OBJ_1(example_double_obj, example_double);


enum {
    Undefined        = 0x00,
    BeforeSend       = 0x01,
    AfterSend        = 0x02,
    FreeRunning      = 0x04
};


// Define all properties of the example module, which currently are the name (a
// string) and a function.
// All identifiers and strings are written as MP_QSTR_xxx and will be
// optimized to word-sized integers by the build system (interned strings).
STATIC const mp_rom_map_elem_t example_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_example) },

    // methods
    { MP_ROM_QSTR(MP_QSTR_double), MP_ROM_PTR(&example_double_obj) },

    // constants
    { MP_ROM_QSTR(MP_QSTR_Undefined), MP_ROM_INT(Undefined) },
    { MP_ROM_QSTR(MP_QSTR_BeforeSend), MP_ROM_INT(BeforeSend) },
    { MP_ROM_QSTR(MP_QSTR_AfterSend), MP_ROM_INT(AfterSend) },
    { MP_ROM_QSTR(MP_QSTR_FreeRunning), MP_ROM_INT(FreeRunning) },
};


STATIC MP_DEFINE_CONST_DICT(example_module_globals, example_module_globals_table);


// Define module object.
const mp_obj_module_t example_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&example_module_globals,
};
