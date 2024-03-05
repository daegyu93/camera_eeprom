import util 
import argparse
import ruamel.yaml
import sys


def main():
    parser = argparse.ArgumentParser(description='A simple program to demonstrate argument parsing')
    parser.add_argument('-w', '--write', type=str, default=None, help='Path to the yaml file for write eeprom')
    parser.add_argument('-r', '--read', type=str, default=None, help='Path to the yaml file for read eeprom')
    parser.add_argument('-c', '--config', type=str, default='config.yaml', help='Path to the yaml file for config eeprom')
    parser.add_argument('-p' , '--print_result', action='store_true', help='Print the result')

    args = parser.parse_args()

    result = ''
    if args.write:
        result = util.import_yaml_and_write_eeprom(args.write, args.config)
    elif args.read:
        result = util.read_eeprom_and_export_yaml(args.read, args.config)

    if args.print_result:
        yaml = ruamel.yaml.YAML()
        yaml.dump(result, sys.stdout)

if __name__ == "__main__":
    main()
