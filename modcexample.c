// Include required definitions first.
#include "py/obj.h"
#include "py/objint.h"
#include "py/runtime.h"


//
// FUNCTION
//

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


//
// CONSTANTS
//

enum {
    Undefined        = 0x00,
    BeforeSend       = 0x01,
    AfterSend        = 0x02,
    FreeRunning      = 0x04
};


//
// CLASS
//

mp_obj_t mp_obj_new_polar_point(mp_float_t radius, mp_float_t theta);

typedef struct {
    mp_obj_base_t base;
    mp_float_t radius;
    mp_float_t theta;
} mp_obj_polar_point_t;

STATIC mp_obj_t polar_point_make_new(const mp_obj_type_t *type_in, size_t n_args, size_t n_kw, const mp_obj_t *args) {
    (void)type_in;
    mp_arg_check_num(n_args, n_kw, 0, 2, false);

    switch (n_args) {
        case 2: {
            mp_float_t radius = mp_obj_get_float(args[0]);
            mp_float_t theta = mp_obj_get_float(args[1]);
            return mp_obj_new_polar_point(radius, theta);
        }
        case 0:
        default:
            return mp_obj_new_polar_point(0, 0);
    }
}

STATIC mp_obj_t polar_point_set_radius(mp_obj_t self_in, mp_obj_t arg_in) {
    mp_obj_polar_point_t *self = MP_OBJ_TO_PTR(self_in);
    self->radius = mp_obj_get_float(arg_in);
    return mp_const_none;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_2(polar_point_set_radius_obj, polar_point_set_radius);

STATIC const mp_rom_map_elem_t polar_point_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR_set_radius), MP_ROM_PTR(&polar_point_set_radius_obj) },
};

STATIC MP_DEFINE_CONST_DICT(polar_point_locals_dict, polar_point_locals_dict_table);

STATIC void polar_point_attr(mp_obj_t self_in, qstr attr, mp_obj_t *dest);

const mp_obj_type_t mp_type_polar_point = {
    { &mp_type_type },
    .name = MP_QSTR_PolarPoint,
    .make_new = polar_point_make_new,
    .attr = polar_point_attr,
    .locals_dict = (mp_obj_dict_t*)&polar_point_locals_dict,
};

STATIC void polar_point_attr(mp_obj_t self_in, qstr attr, mp_obj_t *dest) {
    if (dest[0] != MP_OBJ_NULL) {
        // not load attribute
        return;
    }
    mp_obj_polar_point_t *self = MP_OBJ_TO_PTR(self_in);
    if (attr == MP_QSTR_radius) {
        dest[0] = mp_obj_new_float(self->radius);
    } else if (attr == MP_QSTR_theta) {
        dest[0] = mp_obj_new_float(self->theta);
    } else {
        mp_obj_type_t *type = mp_obj_get_type(self);
        mp_map_t *locals_map = &(type->locals_dict->map);
        mp_map_elem_t *elem = mp_map_lookup(locals_map, MP_OBJ_NEW_QSTR(attr), MP_MAP_LOOKUP);
        if (elem != NULL) {
            dest[0] = mp_obj_new_bound_meth(elem->value, self);
        }
    }
}

mp_obj_t mp_obj_new_polar_point(mp_float_t radius, mp_float_t theta) {
    mp_obj_polar_point_t *o = m_new_obj(mp_obj_polar_point_t);
    o->base.type = &mp_type_polar_point;
    o->radius = radius;
    o->theta = theta;
    return MP_OBJ_FROM_PTR(o);
}


//
// MODULE
//

// Define all properties of the example module
// All identifiers and strings are written as MP_QSTR_xxx and will be
// optimized to word-sized integers by the build system (interned strings).
STATIC const mp_rom_map_elem_t example_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_example) },

    // functions
    { MP_ROM_QSTR(MP_QSTR_double), MP_ROM_PTR(&example_double_obj) },

    // constants
    { MP_ROM_QSTR(MP_QSTR_Undefined), MP_ROM_INT(Undefined) },
    { MP_ROM_QSTR(MP_QSTR_BeforeSend), MP_ROM_INT(BeforeSend) },
    { MP_ROM_QSTR(MP_QSTR_AfterSend), MP_ROM_INT(AfterSend) },
    { MP_ROM_QSTR(MP_QSTR_FreeRunning), MP_ROM_INT(FreeRunning) },

    // classes
    { MP_ROM_QSTR(MP_QSTR_PolarPoint), MP_ROM_PTR(&mp_type_polar_point) },
};


STATIC MP_DEFINE_CONST_DICT(example_module_globals, example_module_globals_table);


// Define module object.
const mp_obj_module_t example_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&example_module_globals,
};
