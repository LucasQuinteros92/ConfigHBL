import json




class Config():
    def __init__(self) -> None:
        try:
            with open("Clases/config.json") as fp:
                self.data = json.load(fp)
            
        except:
            raise Exception("No se encuentra el archivo de cfg")
        
        self.HBLfolder = self.data["HBLfolder"]