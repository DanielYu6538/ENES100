import time
from machine import I2C
from struct import unpack, pack

class VL53L1X:
    # Selected Register Addresses
    SOFT_RESET = 0x0000
    I2C_SLAVE_DEVICE_ADDRESS = 0x0001
    FIRMWARE_SYSTEM_STATUS = 0x00E5
    IDENTIFICATION_MODEL_ID = 0x010F
    
    # Distance Modes
    SHORT = 1
    MEDIUM = 2
    LONG = 3
    
    def __init__(self, i2c, address=0x29):
        self.i2c = i2c
        self.address = address
        self.distance_mode = None
        self.osc_calibrate_val = 0
        self.fast_osc_frequency = 0
        self.calibrated = False
        self.saved_vhv_init = 0
        self.saved_vhv_timeout = 0
        self.timing_budget_us = 0

    # --- Low Level I/O ---

    def _write_reg(self, reg, value):
        self.i2c.writeto_mem(self.address, reg, bytes([value]), addrsize=16)

    def _write_reg_16bit(self, reg, value):
        data = pack('>H', value) # Big-endian 16-bit
        self.i2c.writeto_mem(self.address, reg, data, addrsize=16)

    def _write_reg_32bit(self, reg, value):
        data = pack('>I', value) # Big-endian 32-bit
        self.i2c.writeto_mem(self.address, reg, data, addrsize=16)

    def _read_reg(self, reg):
        return self.i2c.readfrom_mem(self.address, reg, 1, addrsize=16)[0]

    def _read_reg_16bit(self, reg):
        data = self.i2c.readfrom_mem(self.address, reg, 2, addrsize=16)
        return unpack('>H', data)[0]

    # --- Sensor Methods ---

    def init(self):
        if self._read_reg_16bit(self.IDENTIFICATION_MODEL_ID) != 0xEACC:
            return False

        # Software Reset
        self._write_reg(self.SOFT_RESET, 0x00)
        time.sleep_us(100)
        self._write_reg(self.SOFT_RESET, 0x01)
        time.sleep_ms(1)

        # Poll for boot completion
        start = time.ticks_ms()
        while (self._read_reg(self.FIRMWARE_SYSTEM_STATUS) & 0x01) == 0:
            if time.ticks_diff(time.ticks_ms(), start) > 100:
                return False

        # Data Init
        self.fast_osc_frequency = self._read_reg_16bit(0x0006)
        self.osc_calibrate_val = self._read_reg_16bit(0x00DE)

        # Static Init (Tuning parms)
        self._write_reg_16bit(0x0024, 0x0A00) # DSS_CONFIG__TARGET_TOTAL_RATE_MCPS
        self._write_reg(0x0031, 0x02)         # GPIO__TIO_HV_STATUS
        self._write_reg(0x0036, 8)            # SIGMA_ESTIMATOR__EFFECTIVE_PULSE_WIDTH_NS
        self._write_reg(0x0037, 16)           # SIGMA_ESTIMATOR__EFFECTIVE_AMBIENT_WIDTH_NS
        self._write_reg(0x0039, 0x01)         # ALGO__CROSSTALK_COMPENSATION_VALID_HEIGHT_MM
        self._write_reg(0x003E, 0xFF)         # ALGO__RANGE_IGNORE_VALID_HEIGHT_MM
        self._write_reg(0x003F, 0)            # ALGO__RANGE_MIN_CLIP
        self._write_reg(0x0040, 2)            # ALGO__CONSISTENCY_CHECK__TOLERANCE
        self._write_reg_16bit(0x0050, 0x0000) # SYSTEM__THRESH_RATE_HIGH
        self._write_reg_16bit(0x0052, 0x0000) # SYSTEM__THRESH_RATE_LOW
        self._write_reg(0x0057, 0x38)         # DSS_CONFIG__APERTURE_ATTENUATION
        self._write_reg_16bit(0x0064, 360)    # RANGE_CONFIG__SIGMA_THRESH
        self._write_reg_16bit(0x0066, 192)    # RANGE_CONFIG__MIN_COUNT_RATE_RTN_LIMIT_MCPS
        self._write_reg(0x0071, 0x01)         # SYSTEM__GROUPED_PARAMETER_HOLD_0
        self._write_reg(0x007C, 0x01)         # SYSTEM__GROUPED_PARAMETER_HOLD_1
        self._write_reg(0x007E, 2)            # SD_CONFIG__QUANTIFIER
        self._write_reg(0x0082, 0x00)         # SYSTEM__GROUPED_PARAMETER_HOLD
        self._write_reg(0x0077, 1)            # SYSTEM__SEED_CONFIG
        self._write_reg(0x0081, 0x8B)         # SYSTEM__SEQUENCE_CONFIG
        self._write_reg_16bit(0x0054, 200 << 8) # DSS_CONFIG__MANUAL_EFFECTIVE_SPADS_SELECT
        self._write_reg(0x004F, 2)            # DSS_CONFIG__ROI_MODE_CONTROL

        self.set_distance_mode(self.LONG)
        self.set_timing_budget(50000)
        return True

    def set_distance_mode(self, mode):
        if mode == self.SHORT:
            self._write_reg(0x0060, 0x07) # VCSEL_PERIOD_A
            self._write_reg(0x0063, 0x05) # VCSEL_PERIOD_B
            self._write_reg(0x0069, 0x38) # VALID_PHASE_HIGH
            self._write_reg(0x0078, 0x07) # WOI_SD0
            self._write_reg(0x0079, 0x05) # WOI_SD1
            self._write_reg(0x007A, 6)    # INITIAL_PHASE_SD0
            self._write_reg(0x007B, 6)    # INITIAL_PHASE_SD1
        elif mode == self.MEDIUM:
            self._write_reg(0x0060, 0x0B)
            self._write_reg(0x0063, 0x09)
            self._write_reg(0x0069, 0x78)
            self._write_reg(0x0078, 0x0B)
            self._write_reg(0x0079, 0x09)
            self._write_reg(0x007A, 10)
            self._write_reg(0x007B, 10)
        elif mode == self.LONG:
            self._write_reg(0x0060, 0x0F)
            self._write_reg(0x0063, 0x0D)
            self._write_reg(0x0069, 0xB8)
            self._write_reg(0x0078, 0x0F)
            self._write_reg(0x0079, 0x0D)
            self._write_reg(0x007A, 14)
            self._write_reg(0x007B, 14)
        self.distance_mode = mode

    def start_continuous(self, period_ms):
        inter_measurement = int(period_ms * self.osc_calibrate_val)
        self._write_reg_32bit(0x006C, inter_measurement)
        self._write_reg(0x0086, 0x01) # Interrupt Clear
        self._write_reg(0x0087, 0x40) # Start Timed Ranging

    def read(self):
        # Poll for data ready
        while (self._read_reg(0x0031) & 0x01) != 0:
            time.sleep_ms(1)

        # Read result buffer (17 bytes starting at 0x0089)
        res = self.i2c.readfrom_mem(self.address, 0x0089, 17, addrsize=16)
        range_status = res[0]
        stream_count = res[2]
        dss_actual_spads = unpack('>H', res[3:5])[0]
        ambient_rate = unpack('>H', res[7:9])[0]
        raw_range = unpack('>H', res[13:15])[0]
        peak_rate = unpack('>H', res[15:17])[0]

        # Apply correction gain (approx 98%)
        corrected_range = (raw_range * 2011 + 0x0400) >> 11
        
        self._write_reg(0x0086, 0x01) # Clear interrupt
        return corrected_range, range_status

    def set_timing_budget(self, budget_us):
        # Simplified port of the C++ timing budget logic
        if budget_us < 20000: return False
        self.timing_budget_us = budget_us
        # For a basic port, we leave the detailed macro-period math 
        # to the default LONG mode settings or the user can expand this.
        return True