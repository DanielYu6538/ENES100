#include "py/runtime.h"
#include "py/obj.h"
#include "py/mphal.h"
#include <math.h>

// The Drivetrain structure
typedef struct _mp_obj_drivetrain_t {
    mp_obj_base_t base;
    
    // References to your Python objects
    mp_obj_t motor_left;
    mp_obj_t motor_right;
    mp_obj_t imu;

    // We can also store PID variables here later
    mp_float_t kp;
    mp_float_t target_heading;
} mp_obj_drivetrain_t;

static mp_obj_t drivetrain_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *args) {
    // We expect 3 arguments: left motor, right motor, and IMU
    mp_arg_check_num(n_args, n_kw, 3, 4, false);

    // Allocate the Drivetrain object on the heap
    mp_obj_drivetrain_t *self = mp_obj_malloc(mp_obj_drivetrain_t, type);

    // Store the Python objects directly into our structgem
    // args[0] = Motor object 1
    // args[1] = Motor object 2
    // args[2] = BNO055 object
    // args[3] = kp val
    self->motor_left = args[0];
    self->motor_right = args[1];
    self->imu = args[2];

    // Initialize some default PID values
    if (n_args == 4) {
        self->kp = mp_obj_get_float(args[3]);
    } else {
        self->kp = 1.5f;
    }
    self->target_heading = 0.0f;

    return MP_OBJ_FROM_PTR(self);
}


static void set_motor(mp_obj_t motor_obj, int speed) {
    mp_obj_t dest[4];
    mp_load_method(motor_obj, MP_QSTR_move, dest);
    int abs_speed = speed;
    int direction = 1;
    if (speed < 0) {
        abs_speed = -speed;
        direction = 2;
    }
    if (abs_speed > 100) {
        abs_speed = 100;
    }

    dest[2] = mp_obj_new_int(direction);
    dest[3] = mp_obj_new_int(abs_speed);

    mp_call_method_n_kw(2, 0, dest);
}

static mp_float_t get_current_heading(mp_obj_t imu_obj) {
    mp_obj_t dest[2];
    mp_load_method(imu_obj, MP_QSTR_euler, dest);
    mp_obj_t tuple = mp_call_method_n_kw(0, 0, dest);
    
    // Euler returns a 3-item tuple: (heading, roll, pitch)
    mp_obj_t heading_obj = mp_obj_subscr(tuple, mp_obj_new_int(0), MP_OBJ_SENTINEL);
    
    return mp_obj_get_float(heading_obj);
}

static mp_obj_t drivetrain_drive_cont(mp_obj_t self_in, mp_obj_t speed_obj) {
    mp_obj_drivetrain_t *self = MP_OBJ_TO_PTR(self_in);
    
    int base_speed = mp_obj_get_int(speed_obj);
    
    if (base_speed > 100) base_speed = 100;
    if (base_speed < -100) base_speed = -100;

    set_motor(self->motor_left, base_speed);
    set_motor(self->motor_right, -base_speed);

    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_2(drivetrain_drive_cont_obj, drivetrain_drive_cont);

static mp_obj_t drivetrain_stop(mp_obj_t self_in) {
    mp_obj_drivetrain_t *self = MP_OBJ_TO_PTR(self_in);

    set_motor(self->motor_left, 0);
    set_motor(self->motor_right, 0);

    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_1(drivetrain_stop_obj, drivetrain_stop);

static mp_obj_t drivetrain_drive(mp_obj_t self_in, mp_obj_t speed_obj, mp_obj_t duration_obj) {
    mp_obj_drivetrain_t *self = MP_OBJ_TO_PTR(self_in);
    
    int base_speed = mp_obj_get_int(speed_obj);
    if (base_speed > 80) {
        base_speed = 80;
    }
    else if (base_speed < -80) {
        base_speed = -80;
    }
    mp_float_t duration = mp_obj_get_float(duration_obj);
    uint32_t duration_ms = (uint32_t) (fabs(duration) * 1000.0);
    
    uint32_t start = mp_hal_ticks_ms();
    mp_float_t target_heading = get_current_heading(self->imu); 

    while (mp_hal_ticks_ms() - start < duration_ms) {
        mp_float_t current = get_current_heading(self->imu); 

        mp_float_t error = target_heading - current;
        while (error > MICROPY_FLOAT_CONST(180.0)) error -= MICROPY_FLOAT_CONST(360.0);
        while (error < MICROPY_FLOAT_CONST(-180.0)) error += MICROPY_FLOAT_CONST(360.0);

        mp_float_t correction = error * self->kp;

        // 4. Calculate final motor speeds (bounded 0-100)
        int left_v = base_speed + (int) correction;
        int right_v = -(base_speed - (int) correction);

        set_motor(self->motor_left, left_v);
        set_motor(self->motor_right, right_v);

        mp_hal_delay_ms(10); // Run at 100Hz ⚡
    }

    set_motor(self->motor_left, 0);
    set_motor(self->motor_right, 0);

    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_3(drivetrain_drive_obj, drivetrain_drive);

static mp_obj_t drivetrain_turn(mp_obj_t self_in, mp_obj_t angle_obj, mp_obj_t speed_obj) {
    mp_obj_drivetrain_t *self = MP_OBJ_TO_PTR(self_in);

    int base_speed = mp_obj_get_int(speed_obj);
    base_speed = (base_speed < 0) ? -base_speed : base_speed;
    if (base_speed < 10) {
        base_speed = 10;
    }

    mp_float_t angle = mp_obj_get_float(angle_obj);
    mp_float_t start_heading = get_current_heading(self->imu);
    mp_float_t target_heading = start_heading + angle;
    while (target_heading > MICROPY_FLOAT_CONST(360.0)) target_heading -= MICROPY_FLOAT_CONST(360.0);
    while (target_heading < MICROPY_FLOAT_CONST(0.0)) target_heading += MICROPY_FLOAT_CONST(360.0);

    mp_float_t error = 180.0;
    const mp_float_t tolerance = 0.5;

    while (fabs(error) > tolerance) {
        angle = get_current_heading(self->imu);
        error = target_heading - angle;
        // mp_printf(MP_PYTHON_PRINTER, "Error: %f\n", error); // TESTING
        while (error > MICROPY_FLOAT_CONST(180.0)) error -= MICROPY_FLOAT_CONST(360.0);
        while (error < MICROPY_FLOAT_CONST(-180.0)) error += MICROPY_FLOAT_CONST(360.0);

        int turn_speed = error > 0 ? base_speed : -base_speed;
        set_motor(self->motor_left, turn_speed);
        set_motor(self->motor_right, turn_speed);
        
        mp_hal_delay_ms(10);
    }
    
    set_motor(self->motor_left, 0);
    set_motor(self->motor_right, 0);

    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_3(drivetrain_turn_obj, drivetrain_turn);


// 1. Define the "Menu" of methods
static const mp_rom_map_elem_t drivetrain_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR_drive_cont), MP_ROM_PTR(&drivetrain_drive_cont_obj) },
    { MP_ROM_QSTR(MP_QSTR_stop), MP_ROM_PTR(&drivetrain_stop_obj) },
    { MP_ROM_QSTR(MP_QSTR_drive), MP_ROM_PTR(&drivetrain_drive_obj) },
    { MP_ROM_QSTR(MP_QSTR_turn), MP_ROM_PTR(&drivetrain_turn_obj) }
};
static MP_DEFINE_CONST_DICT(drivetrain_locals_dict, drivetrain_locals_dict_table);

// 2. Define the Type Object (the "Class")
MP_DEFINE_CONST_OBJ_TYPE(
    drivetrain_type,
    MP_QSTR_Drivetrain,
    MP_TYPE_FLAG_NONE,
    make_new, drivetrain_make_new,
    locals_dict, &drivetrain_locals_dict
);

// 3. Register the Module itself
static const mp_rom_map_elem_t drivetrain_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_drivetrain) },
    { MP_ROM_QSTR(MP_QSTR_Drivetrain), MP_ROM_PTR(&drivetrain_type) },
};
static MP_DEFINE_CONST_DICT(drivetrain_module_globals, drivetrain_module_globals_table);

const mp_obj_module_t drivetrain_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&drivetrain_module_globals,
};

// 4. Register the module globally
MP_REGISTER_MODULE(MP_QSTR_drivetrain, drivetrain_user_cmodule);