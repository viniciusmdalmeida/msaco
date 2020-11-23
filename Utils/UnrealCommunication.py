import yaml

class UnrealCommunication:
    def __init__(self,
                 config_path="config.yml",
                 path=None,
                 file_name=None):
        if path is None and file_name is None:
            with open(config_path, 'r') as file_config:
                self.config = yaml.full_load(file_config)
                path = self.config['unreal']['path']
                file_name = self.config['unreal']['file']
        self.file_path = path+'/'+file_name

    def reset_plane(self,location = None,rotation = None):
        print("Reset Plane")
        file = open(self.file_path,'w')
        text_file = 'status:reset\n'
        if location:
            text_file += "X:" + str(location[0]) + '\n'
            text_file += "Y:" + str(location[1]) + '\n'
            text_file += "Z:" + str(location[2]) + '\n'
        if rotation:
            text_file += "Pitch:" + str(rotation[0]) + '\n'
            text_file += "Yaw:" + str(rotation[1]) + '\n'
            text_file += "Roll:" + str(rotation[2]) + '\n'
        file.write(text_file)
        file.close()

    def start_plane(self):
        file = open(self.file_path, 'w')
        file.write('status:start')
        file.close()
    """
    def stop_plane(self):
        file = open(self.file_path, 'w')
        file.write('status:stop')
        file.close()
    """