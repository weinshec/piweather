import logging
import time
from ctypes import c_int16, c_uint16
from piweather.sensors import Sensor


class BMP280(Sensor):

    DEFAULT_I2C_ADDR = 0x77

    OSRS = {
        "x1":  0b001,
        "x2":  0b010,
        "x4":  0b011,
        "x8":  0b100,
        "x16": 0b101,
    }

    FILTER = {
        "OFF": 0,
        "2":   1,
        "4":   2,
        "8":   3,
        "16":  4,
    }

    ADDR_CAL = 0x88
    ADDR_CFG = 0xF5
    ADDR_CTRL = 0xF4
    ADDR_DATA = 0xF7

    CMD_READ = 0x02

    FILTER_MASK = 0b00011100  # t_sb[0:2] | filter[0:2] | _[0:1] | spi3w_en[0]

    def __init__(
        self,
        i2c_addr=DEFAULT_I2C_ADDR,
        osrs_p=OSRS["x4"],
        osrs_t=OSRS["x1"],
        filtr=FILTER["OFF"],
        *args,
        **kwargs
    ):
        super(BMP280, self).__init__(*args, **kwargs)

        try:
            import smbus
        except ImportError:
            logging.warning("Module 'smbus' not found. "
                            "Not able to read i2c devices.")

        self._i2c_addr = i2c_addr
        self._bus = smbus.SMBus(1)  # TODO: Make this selectable

        self.osrs_p = osrs_p
        self.osrs_t = osrs_t
        self.filtr = filtr

        self._get_calibration()

    @property
    def i2c_addr(self):
        return self._i2c_addr

    @property
    def osrs_p(self):
        return self._osrs_p

    @osrs_p.setter
    def osrs_p(self, osrs):
        if osrs not in BMP280.OSRS.values():
            raise ValueError(
                "Invalid pressure oversampling value {:b}".format(osrs))
        self._osrs_p = osrs

    @property
    def osrs_t(self):
        return self._osrs_t

    @osrs_t.setter
    def osrs_t(self, osrs):
        if osrs not in BMP280.OSRS.values():
            raise ValueError(
                "Invalid temperature oversampling value {:b}".format(osrs))
        self._osrs_t = osrs

    @property
    def filtr(self):
        cfg_reg = self._bus.read_byte_data(BMP280.ADDR_CFG)
        filtr = cfg_reg & BMP280.FILTER_MASK
        logging.debug("BMP280: read filter setting: {:8b}".format(filtr))
        return filtr

    @filtr.setter
    def filtr(self, filtr):
        if filtr not in BMP280.FILTER.values():
            raise ValueError(
                "Invalid filter value {:b}".format(filtr))

        cfg_reg = self._bus.read_byte_data(BMP280.ADDR_CFG)
        logging.debug("BMP280: read ADDR_CFG register: {:8b}".format(cfg_reg))

        INV_FILTER_MASK = BMP280.FILTER_MASK ^ 0xFF
        cfg_reg = (cfg_reg & INV_FILTER_MASK) | (filtr << 2)

        logging.debug("BMP280: set ADDR_CFG register: {:8b}".format(cfg_reg))
        self._bus.write_byte_data(self.i2c_addr, BMP280.ADDR_CFG, cfg_reg)

    @staticmethod
    def to_short(byte_list):
        # Little Endian
        lsb, msb = byte_list[0], byte_list[1]
        return c_int16((msb << 8) + lsb).value

    @staticmethod
    def to_ushort(byte_list):
        # Little Endian
        lsb, msb = byte_list[0], byte_list[1]
        return c_uint16((msb << 8) + lsb).value

    def read(self):
        read_cmd = (self.osrs_t << 5) + (self.osrs_p << 2) + BMP280.CMD_READ
        self._bus.write_byte_data(self.i2c_addr, BMP280.ADDR_CTRL, read_cmd)

        self._wait_measurement_time()

        data_reg = self._bus.read_i2c_block_data(
            self.i2c_addr, BMP280.ADDR_DATA, 6)
        raw_p = (data_reg[0] << 12) | (data_reg[1] << 4) | (data_reg[2] >> 4)
        raw_T = (data_reg[3] << 12) | (data_reg[4] << 4) | (data_reg[5] >> 4)

        T = self._compensated_temperature(raw_T)
        p = self._compensated_pressure(raw_p, T)

        return p

    def _get_calibration(self):
        cal_reg = self._bus.read_i2c_block_data(self.i2c_addr,
                                                BMP280.ADDR_CAL,
                                                24)
        self.calibration = dict()
        self.calibration["T1"] = self.to_ushort(cal_reg[0:2])
        self.calibration["T2"] = self.to_short(cal_reg[2:4])
        self.calibration["T3"] = self.to_short(cal_reg[4:6])
        self.calibration["P1"] = self.to_ushort(cal_reg[6:8])
        self.calibration["P2"] = self.to_short(cal_reg[8:10])
        self.calibration["P3"] = self.to_short(cal_reg[10:12])
        self.calibration["P4"] = self.to_short(cal_reg[12:14])
        self.calibration["P5"] = self.to_short(cal_reg[14:16])
        self.calibration["P6"] = self.to_short(cal_reg[16:18])
        self.calibration["P7"] = self.to_short(cal_reg[18:20])
        self.calibration["P8"] = self.to_short(cal_reg[20:22])
        self.calibration["P9"] = self.to_short(cal_reg[22:24])

    def _wait_measurement_time(self):
        if self.osrs_p == BMP280.OSRS["x1"]:
            time.sleep(0.007)
        elif self.osrs_p == BMP280.OSRS["x2"]:
            time.sleep(0.009)
        elif self.osrs_p == BMP280.OSRS["x4"]:
            time.sleep(0.014)
        elif self.osrs_p == BMP280.OSRS["x8"]:
            time.sleep(0.023)
        elif self.osrs_p == BMP280.OSRS["x16"]:
            time.sleep(0.044)

    def _compensated_temperature(self, raw_T):
        cal = self.calibration

        var1 = (raw_T/16384. - cal["T1"]/1024.) * cal["T2"]
        var2 = (raw_T/131072. - cal["T1"]/8192.)**2 * cal["T3"]
        T = (var1 + var2) / 5120.

        logging.debug("  raw_T = {}".format(raw_T))
        logging.debug("   var1 = {}".format(var1))
        logging.debug("   var2 = {}".format(var2))
        logging.debug("      T = {}".format(T))

        return T

    def _compensated_pressure(self, raw_p, T):
        cal = self.calibration

        var1 = T*2560. - 64000.
        var2 = var1**2 * cal["P6"] / 32768.
        var2 = var2 + var1 * cal["P5"] * 2.
        var2 = var2/4. + cal["P4"]*65536.
        var1 = (cal["P3"] * var1**2 / 524288. + cal["P2"] * var1) / 524288.
        var1 = (1. + var1/32768.) * cal["P1"]
        p = 1048576. - raw_p
        p = (p - var2/4096.) * 6250. / var1
        var1 = cal["P9"] * p**2 / 2147483648.
        var2 = p * cal["P8"] / 32768.
        p = p + (var1 + var2 + cal["P7"]) / 16.

        logging.debug("  raw_p = {}".format(raw_p))
        logging.debug("   var1 = {}".format(var1))
        logging.debug("   var2 = {}".format(var2))
        logging.debug("      p = {}".format(p))

        return p
