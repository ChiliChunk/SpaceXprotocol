class Robot:
    def __init__(self , name):
        self.name = name
        self.x = None
        self.y = None
        self.ressources = {}
        self.isPaused = False

    def addRessources (self,ressources):
        for res in ressources:
            if res in self.ressources:
                self.ressources[res] += 1
            else:
                self.ressources[res] = 1

    def __str__(self):
        return f"{self.name} {'PAUSED' if self.isPaused else 'In_Acivity'} ({self.x},{self.y}) {self.ressources}"