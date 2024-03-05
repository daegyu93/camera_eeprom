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


def read_distortion_parameter_in_eeprom(output_config_path, config_yaml='config.yaml'):
    eeprom = I2cDevice(bus=I2C_BUS, dev_addr=EEPROM_ADDRESS)
    yaml_parser = YamlParser() 

    yaml_data = yaml_parser.read_yaml(config_yaml)

    cal_param_dict = {}
    for content in yaml_data['Data']['calibration']:
        offset = yaml_data['Data']['calibration'][content]['offset']
        type = yaml_data['Data']['calibration'][content]['type']
        size = yaml_data['Data']['calibration'][content]['size']
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
        
        cal_param_dict[content] = value

    focal_length = (cal_param_dict['focal_length__fx']+ cal_param_dict['focal_length__fy'])/2
    k0 = cal_param_dict['radial_distortion__k1']
    k1 = cal_param_dict['radial_distortion__k2']
    k2 = cal_param_dict['radial_distortion__k3']
    p0 = cal_param_dict['tangential_distortion__p1']
    p1 = cal_param_dict['tangential_distortion__p2']
    cx = cal_param_dict['principal_point__cx']
    cy = cal_param_dict['principal_point__cy']

    f = open(output_config_path, 'w')
    # [property]
    # output-width=1920
    # output-height=1080
    # num-batch-buffers=1
    f.write('[property]\n')
    f.write('output-width=1920\n')
    f.write('output-height=1080\n')
    f.write('num-batch-buffers=1\n')
    f.write('\n')

    # [surface0]
    # projection-type=3
    # width=1920
    # height=1080
    # focal-length=733.1000
    # distortion= -0.2725762476997752;0.06077245841636788;-0.0055581754220842446;-0.0005782749923515222;0.000701124461693587
    # src-x0=936.337
    # src-y0=580.864
    f.write('[surface0]\n')
    f.write('projection-type=3\n')
    f.write('width=1920\n')
    f.write('height=1080\n')
    f.write('focal-length=' + str(focal_length) + '\n')
    f.write('distortion=' + str(k0) + ';' + str(k1) + ';' + str(k2) + ';' + str(p0) + ';' + str(p1) + '\n')
    f.write('src-x0=' + str(cx) + '\n')
    f.write('src-y0=' + str(cy) + '\n')

    f.close()


