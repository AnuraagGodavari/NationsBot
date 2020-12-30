import json, pprint
#Tries to import from own package. If its not working, this file is being run as the main file.
from ConcertOfNations import *

#Get all buildable info
def allBuildables(saveGame):
    return saveGame.getGameDict()["Game Objects"]["Buildings"]

#Get the info for one buildable
def buildableInfo(saveGame, buildableName):
    gDict = saveGame.getGameDict()["Game Objects"]["Buildings"]
    
    if (buildableName in gDict): return gDict[buildableName]
    
    return False
