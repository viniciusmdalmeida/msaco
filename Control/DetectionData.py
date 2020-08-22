class DetectionData:
    distance = 0
    myDirection = (0,0,0)
    otherDirection = (0,0,0)
    relativeDirection = (0,0,0)
    myPossition = (0,0,0)
    otherPosition = (0,0,0)

    def __init__(self,distance=None,myDirection=None,relativeDirection=None,
                 otherDirection=None,myPosition=None,otherPosition=None):
        self.distance = distance
        self.myDirection = myDirection
        self.relativeDirection = relativeDirection
        self.myPosition = myPosition
        self.otherPosition = otherPosition

        if otherDirection is None:
            self.otherDirection = self.calcOtherDirection()
        else:
            self.otherDirection = otherDirection

    def calcOtherDirection(self):
        pass