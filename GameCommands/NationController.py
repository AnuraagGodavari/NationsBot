import json, pprint
#Tries to import from own package. If its not working, this file is being run as the main file.
from ConcertOfNations import *

#View a nation's info
def nationalInfo(saveGame, nationName):
    nation = saveGame[nationName]
    
    rtnDict = {
        "Nation": nationName,
        "Forces": nation.unitGroups,
        "Territories": nation.territories,
        "Bureaucracy": nation.bureaucracy,
        "Resources": nation.resources
    }
    return rtnDict

#Send a Trade Offer
def offerTrade(saveGame, nationName0, nationName1, trade):
    
    saveGame[nationName1].mailbox["Trade Offers"][nationName0] = trade

#Respond to a Trade Offer
def respondToTrade(saveGame, nationB, nationA):

    saveGame[nationB].respondToTrade(nationA, "ACCEPT", saveGame)

#Send a message
def sendMessage(saveGame, nationName0, nationName1, message):

    saveGame[nationName1].mailbox["Mail"][nationName0] = message

#Read a message
def readMessage(saveGame, nationName0, nationName1):

    return saveGame[nationName1].mailbox["Messages"][nationName0]

#Declare War
def declareWar(saveGame, nationName0, nationName1):
    
    saveGame.breakRelations(nationName0, nationName1)
    saveGame.relateNations("War", nationName0, nationName1)
    
#----------

#Get a unitGroup
def getUnitGroup(saveGame, nationName, unitGroupName):
    return saveGame[nationName].unitGroups[unitGroupName]

#See Armies
def armiesInfo(saveGame, nationName):

    forces = nationalInfo(saveGame, nationName)["Forces"]
    armies = {}
    
    for force in forces.keys():
        if (forces[force].__class__.__name__ == "Army"):
            armies[force] = forces[force]
            
    return armies

#See Fleets
def fleetsInfo(saveGame, nationName):

    forces = nationalInfo(saveGame, nationName)["Forces"]
    fleets = {}
    
    for force in forces.keys():
        if (forces[force].__class__.__name__ == "Fleet"):
            fleets[force] = forces[force]
            
    return fleets

#Build a Unit Group
def trainUnitGroup(saveGame, nation, forceType, unit, size, territory):
    return saveGame[nation].trainForce(forceType, unit, size, territory, saveGame)
    
#Move a Unit Group
def moveUnitGroup(saveGame, nation, unitGroup, destination):
    return saveGame[nation].unitGroups[unitGroup].moveTo(destination, saveGame)
    
#Combine Unit Groups
def mergeUnitGroups(saveGame, nation, coreUnitGroup, *groupsToMerge):
    mergeWith = []
    coreGroup = saveGame[nation].unitGroups[coreUnitGroup]
    
    for group in groupsToMerge:
        mergeWith.append(saveGame[nation].unitGroups[group])
        
    for group in mergeWith:
        if ((group.__class__ != coreGroup.__class__) or (group.territory != coreGroup.territory)):
            return False

    coreGroup.merge(saveGame, *mergeWith)
    return coreGroup

#Split a Unit Group
def splitUnitGroup(saveGame, nation, originalUnitGroup, *unitNames):
    saveGame[nation].unitGroups[originalUnitGroup].split(*unitNames, nation, saveGame)

#Mobilize/Demobilize a Unit Group
def toggleMobilization(saveGame, nation, unitGroupName):
    unitGroup = saveGame[nation].unitGroups[unitGroupName]
    
    if (unitGroup.isActive()):
        unitGroup.demobilize(saveGame, nation)
        
    else:
        unitGroup.enable()

#Delete a Unit Group
def deleteUnitGroup(saveGame, nation, unitGroupToDelete):
    unitGroup = saveGame[nation].unitGroups.pop(unitGroupToDelete)
    unitGroup.onDelete(saveGame, nation)

#----------

#See Territories
def allTerritories(saveGame, nationName = None):
    if (nationName):
        return nationalInfo(saveGame, nationName)["Territories"]

#See all Territories that can be traversed by a nation
def traversableTerritories(saveGame, nationName):
    return saveGame.traversableTerritories(nationName)

#See Individual Territory Info
def getTerritory(saveGame, nationName, territoryName):

    if territoryName in saveGame[nationName].territories:
        return saveGame[nationName].territories[territoryName]
        
    return False

#Build Project in a Territory
def buildProject(saveGame, nationName, projectName, territoryName):
    saveGame[nationName].buildProject(projectName, territoryName, saveGame)

#Toggle a Project in a Territory
def toggleProject(saveGame, nation, projectName, territory):
    if (project.isActive()):
        saveGame[nation].disableObject(f"{territory}:{projectName}", saveGame)
    else:
        project.enable()

#Destroy a Project in a Territory
def destroyProject(saveGame, nation, project, territory):
    saveGame[nation].destroyProject(self, projectName, territory, saveGame)

#See a map of all territories in the game colored by nation
def mapImage(saveGame, nation = None):
    return saveGame.saveMapImage(nation)

#----------
#'''
def testProcedure():
    print("-----\nNationController.testProcedure() Started!\n-----")

    import ConcertOfNationsTest
    testGame = ConcertOfNationsTest.testProcedure()
    
    #shit to do with the testGame
    
    testGame.saveMapImage()
    testGame.saveMapImage("TestB")
    
    #Save the game
    with open("Savegames/Test - 0.json", 'w') as f: #Saves the SaveGame to a new file
        json.dump(FileHandling.saveObject(testGame), f, indent = 4)
    
    print("-----\nNationController.testProcedure() Complete!\n-----")
    
testProcedure()

#'''

#Bottom



















#Bottom 2 Electric Boogaloo