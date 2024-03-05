from time import sleep
from i2cdevice import I2cDevice
from yaml_parser import YamlParser
import struct
import sys

EEPROM_ADDRESS = 0x50
I2C_BUS = 31

def read_eeprom_and_export_yaml(output_yaml, config_yaml):
    eeprom = I2cDevice(bus=I2C_BUS, dev_addr=EEPROM_ADDRESS)
    yaml_parser = YamlParser() 

    yaml_data = yaml_parser.read_yaml(config_yaml)

    for item in yaml_data['Data']:
        if item == 'checksum':
            continue
        for content in yaml_data['Data'][item]:
            offset = yaml_data['Data'][item][content]['offset']
            type = yaml_data['Data'][item][content]['type']
            size = yaml_data['Data'][item][content]['size']
            
            byte_list = eeprom.read_burst(offset, size)
            
            value = ''
            if type == 'hex':
                value = '0x' + ''.join(format(x, '02x') for x in reversed(byte_list))
            elif type == 'dec':
                value = int.from_bytes(byte_list, byteorder='little')
            elif type == 'float':
                byte_data = bytes(byte_list)
                value = struct.unpack('f', byte_data)[0]
            elif type == 'string':
                value = ''.join(chr(byte) if byte != 255 else ' ' for byte in byte_list)
            yaml_data['Data'][item][content] = value

    byte_list = eeprom.read_burst(yaml_data['Data']['checksum']['offset'], yaml_data['Data']['checksum']['size'])
    checksum = int.from_bytes(byte_list, byteorder='little')
    yaml_data['Data']['checksum'] = checksum
    
    yaml_parser.remove_offset_and_type_and_size(yaml_data)
    yaml_parser.write_yaml(output_yaml, yaml_data)
    return yaml_data

def import_yaml_and_write_eeprom(input_yaml, config_yaml):
    eeprom = I2cDevice(bus=I2C_BUS, dev_addr=EEPROM_ADDRESS)
        
    config_yaml_parser = YamlParser() 
    input_yaml_parser = YamlParser()

    config_yaml_data = config_yaml_parser.read_yaml(config_yaml)
    input_yaml_data = input_yaml_parser.read_yaml(input_yaml)

    checksum = 0
    for item in config_yaml_data['Data']:
        if item == 'checksum':
            continue
        for content in config_yaml_data['Data'][item]:
            offset = config_yaml_data['Data'][item][content]['offset']
            type = config_yaml_data['Data'][item][content]['type']
            size = config_yaml_data['Data'][item][content]['size']
            value = input_yaml_data['Data'][item][content] 
            data_list = []
            if type == 'string':
                data_list = list(value.encode())
            elif type == 'float':
                data_list = list(struct.pack('f', value))
            else:
                if type == 'hex':
                    try:
                        value = int(value, 16)
                    except:
                        pass
                for i in range(size):
                    data_list.append(value & 0xFF)
                    value = value >> 8
            eeprom.write_burst(offset, data_list)
            checksum += sum(data_list)

    eeprom.write_burst(config_yaml_data['Data']['checksum']['offset'], list(checksum.to_bytes(2, byteorder='little')))
    return input_yaml_data

