import ruamel.yaml

class YamlParser:
    def __init__(self):
        pass
            
    def remove_offset_and_type_and_size(self, data):
        if isinstance(data, dict):
            if 'offset' in data:
                del data['offset']
            if 'type' in data:
                del data['type']
            if 'size' in data:
                del data['size']
            for key, value in data.items():
                self.remove_offset_and_type_and_size(value)
                

    def read_yaml(self, input_file):
        yaml = ruamel.yaml.YAML()
        with open(input_file, 'r') as f:
            yaml_data = yaml.load(f)
        return yaml_data
    
    def write_yaml(self, output_file, yaml_data):
        yaml = ruamel.yaml.YAML()
        yaml.default_flow_style = False
        with open(output_file, 'w') as f:
            yaml.dump(yaml_data, f)