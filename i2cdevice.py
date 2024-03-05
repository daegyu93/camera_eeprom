#!/usr/bin/python3
from time import sleep
import logging, coloredlogs
from smbus2 import SMBus, i2c_msg

class I2cDevice:
    def __init__(self, bus, dev_addr):
        self.__bus = bus
        self.dev_addr = dev_addr
        
    def read(self, reg_addr):
        reg_lsb = reg_addr & 0xff
        reg_msb = (reg_addr>>8) & 0xff
        wr = i2c_msg.write(self.dev_addr , [reg_msb, reg_lsb] )
        rd = i2c_msg.read(self.dev_addr , 1)
        with SMBus(self.__bus) as bus: 
            bus.i2c_rdwr(wr, rd)
        result = int.from_bytes(bytes(rd), "little")
        return result

    def write(self, reg_addr, value:int):
        reg_lsb = reg_addr & 0xff
        reg_msb = (reg_addr>>8) & 0xff
        
        regs = [reg_msb, reg_lsb, value]
        wr = i2c_msg.write(self.dev_addr , regs )
        
        with SMBus(self.__bus) as bus:
            timeout = 10
            while timeout:
                try:
                    bus.i2c_rdwr(wr)
                    break
                except OSError as e:
                    logging.error(f'error {e} {timeout}')
                    if e.errno == 121:
                        timeout -= 1
                        
                    if timeout == 0:
                        raise e               
                    
    def read_burst(self, reg_addr, length):
        data = []
        for i in range(length):
            data.append(self.read(reg_addr+i))
            sleep(0.01)
        
        return data
    
    def write_burst(self, reg_addr, data):
        for i, value in enumerate(data):
            self.write(reg_addr+i, value)
            sleep(0.01)

def set_logging(level='INFO'):
    coloredlogs.install(
        fmt="%(asctime)s %(levelname).1s %(module).8s:%(lineno).3d %(message)s"
        ,field_styles={
            'asctime': {'color': 'green'}
            , 'module': {'color': 'magenta'}
            , 'levelname': {'bold': True, 'color': 'black'}
            , 'lineno': {'color': 'yellow'}
            }
        ,level=level
        )

if __name__ == "__main__":
    set_logging('DEBUG')

    logging.info("I2cDevice")
    bus = 31
    addr = 0x50
    logging.debug(f"bus : {bus}, addr : 0x{addr:x}")

    sleep(1)

    des = I2cDevice(bus=bus, dev_addr=addr)

    print(f'{des.read(0x00):#X}')
    sleep(1)
    des.write(0x00, 0xAB)
    sleep(1)
    print(f'{des.read(0x00):#X}')
