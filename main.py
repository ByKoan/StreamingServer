from os         import getcwd, mkdir
from os.path    import exists, join
from sys        import exit, argv
from src.main   import main
from json       import dumps, loads
from pathlib    import Path

class LoadConfig:
    def __init__(self, name_file, path=join(getcwd(), "conf")):
        self.path = path
        self.name_file = name_file
        
    def load(self):
        with open(join(self.path, self.name_file), "r") as file:
            # si el archivo no existe a de saltar error de tipo lectura
            self.data = file.read().replace('\\', '/')
            
        # si lo datos tiene error de sintaxis, aqui debe saltar error
        self.data = loads(self.data)

        return self.data
    
    def init(self):
        if not exists(self.path):
            mkdir(self.path)

        self.data = {
            "port": 80,
            "music_folder": "",
        }

        if not exists(join(self.path, self.name_file)):
            with open(join(self.path, self.name_file), "w") as file:
                file.write(dumps(data, indent=4, ensure_ascii=False))

if __name__ == '__main__':
    load_config = LoadConfig("config.conf")
    load_config.init()
    data = load_config.load()
    
    print(data)
    if not exists(data["music_folder"]):
        print(f"La carpeta de música({data['music_folder']}) no existe, revise {join(load_config.path, load_config.name_file)}")
        exit(1)

    if len(argv) == 1: main(data["music_folder"], data["port"])
    else: main(data["music_folder"])