import json, pprint
from ConcertOfNations import *

print("Test.py TEST PROCEDURE FOR CONCERT OF NATIONS\n*****\n")

#REMINDERS:
print("-----\nREMINDERS:\n")
print("Make Nation take modifiers into account!\n")
print("Calculate supply lines!\n")
print("Make it so that disabled projects can be re-enabled immediately within the same turn, i.e. \"Disabling\" until the turn is done! Do similarly for destroying.\n")
print("Consider switching over to month-based incomes rather than yearly-based\n")
print("-----\n")

def makeTestGame():
    Mapping.testTestGame() #Makes a test map

    testGame = FileHandling.newGame("Test", "0", "Test", 1, 1, "Test Map.json", "Test Dictionary.json") #Creates a test saveGame

    testGame["TestA"] = GameObjects.Nation("TestA") #Creates the nation "TestA"

    with open("Maps/Test Map.json") as f: #Loads the map made earlier
        testMap = FileHandling.loadObject(json.load(f))

    #Annex vertices in testMap to test Nation(s)
    for vertex in testMap.vertices.keys():
        vert = testMap[vertex]
        
        newTerr = GameObjects.Territory.fromDict(FileHandling.saveObject(vert))
        testGame["TestA"].annexTerritory(newTerr, testGame)
        
    with open("Savegames/Test - Test - 0.json", 'w') as f: #Saves the SaveGame to a new file
        json.dump(FileHandling.saveObject(testGame), f, indent = 4)
        
    with open("Savegames/Test - Test - 0.json") as f:
        testGame = FileHandling.loadObject(json.load(f))
        
    for territory in testGame["TestA"].territories.keys():
        testGame["TestA"].territories[territory].demographics["Test Demographic 1"] = GameObjects.Demographic("Test Demographic 1", [10000, 0.01], [0, 0])
        
    return testGame

def makeTestGame_fromImage():
    Mapping.mapFromImage("Testing/Test Map.png") #Makes a test map

    testGame = FileHandling.newGame("Test", "0", 1, 1, "mapFromImage.json", "Test Dictionary.json") #Creates a test saveGame
    testGame.players = {"246808378913849345": "TestA"}

    testGame["TestA"] = GameObjects.Nation("TestA") #Creates the nation "TestA"
    testGame["TestB"] = GameObjects.Nation("TestB") #Creates the nation "TestB"

    with open("Maps/mapFromImage.json") as f: #Loads the map made earlier
        testMap = FileHandling.loadObject(json.load(f))

    #Annex vertices in testMap to test Nation(s)
    for vertex in testMap.vertices.keys():
        if ("TestB" in vertex):
            newTerr = GameObjects.HabitableTerritory.fromDict(FileHandling.saveObject(testMap[vertex]))
            testGame["TestB"].annexTerritory(newTerr, testGame)
        
        elif ("Colonizable" not in vertex):
            vert = testMap[vertex]
            
            if (vert.details["type"] == "SeaTerritory"):
                newTerr = GameObjects.Territory.fromDict(FileHandling.saveObject(vert))
                
            else:
                newTerr = GameObjects.HabitableTerritory.fromDict(FileHandling.saveObject(vert))
            
            testGame["TestA"].annexTerritory(newTerr, testGame)
            
    for terr in testGame["TestB"].territories:
        testGame.saveGameData["DiscoveredBy"][terr] = ["TestA"]
        
    with open("Savegames/Test - Test - 0.json", 'w') as f: #Saves the SaveGame to a new file
        json.dump(FileHandling.saveObject(testGame), f, indent = 4)
        
    with open("Savegames/Test - Test - 0.json") as f:
        testGame = FileHandling.loadObject(json.load(f))
    
    map = testGame.getMap()
    
    for territory in testGame["TestA"].territories.keys():
        if (map[territory].details["type"] == "LandTerritory"):
            testGame["TestA"].territories[territory].demographics["Test Demographic 1"] = GameObjects.Demographic("Test Demographic 1", [1000, 0.01], [0, 0])
        
    return testGame

#At end:
def end(testGame):
    with open(f"Savegames/{testGame.name} - {testGame.ID}.json", 'w') as f: #Saves the SaveGame to a new file
        json.dump(FileHandling.saveObject(testGame), f, indent = 4)
        
    with open(f"Savegames/{testGame.name} - {testGame.ID}.json") as f:
        testGameDict = json.load(f)
        testGame = FileHandling.loadObject(testGameDict)
    
    return testGame

#For testing territory annexation
def testAnnexingTerritory(testGame, nation):

    testTerrWithBarracks = {
        "__class__": "Territory",
        "__module__": "GameObjects",
        "name": "Test 10",
        "status": "Local Focus",
        "type": "Land",
        "projects": {
            "TestBarracks": {
                "__class__": "Building",
                "__module__": "GameObjects",
                "name": "TestBarracks",
                "status": "Active"
            }
        },
        "demographics": {
            "Test Demographic 1": {
                "__class__": "Demographic",
                "__module__": "GameObjects",
                "name": "Test Demographic 1",
                "populationData": [
                    976,
                    0.01
                ],
                "unrestData": [
                    0,
                    0
                ]
            }
        },
        "modifiers": {
            "Territorial": {
                "Cumulative": {
                    "Supply": 10,
                    "Ease of Travel": 0,
                    "Army Maintenance": 0,
                    "Army Attack": 0,
                    "Army Defense": 0,
                    "Army Speed": 0,
                    "Infantry Effectiveness": 0,
                    "Cavalry Effectiveness": 0,
                    "Artillery Effectiveness": 0,
                    "Building Effectiveness": 0
                },
                "Exponential": {
                    "Revenue": 1,
                    "Resource Output": 1,
                    "Army Maintenance": 1,
                    "Building Maintenance": 1
                },
                "Temporary": {}
            },
            "Army": {
                "Cumulative": {
                    "Army Attack": 0,
                    "Army Defense": 0,
                    "Army Speed": 0,
                    "Infantry Effectiveness": 0,
                    "Cavalry Effectiveness": 0,
                    "Artillery Effectiveness": 0
                },
                "Exponential": {
                    "Army Maintenance": 1,
                    "Infantry Maintenance": 1,
                    "Cavalry Maintenance": 1,
                    "Artillery Maintenance": 1
                },
                "Temporary": {}
            },
            "Fleet": {
                "Cumulative": {
                    "Attack": 0,
                    "Defense": 0,
                    "Speed": 0
                },
                "Exponential": {
                    "Maintenance": 1
                },
                "Temporary": {}
            },
            "Demographic": {
                "Cumulative": {
                    "Unrest Cap": 0
                },
                "Exponential": {
                    "Growth": 1,
                    "Tax Modifier": 1,
                    "Unrest": 1
                },
                "Temporary": {}
            }
        }
    }

    testTerrWithBarracks = FileHandling.loadObject(testTerrWithBarracks)
    testGame[nation].annexTerritory(testTerrWithBarracks, testGame)

def testRevenue(testGame, nation):
    economicSize = testGame[nation].revenue(testGame)
    print(f"Revenue in Money of {nation}: ${economicSize}")

def testTrade(testGame, nationA, nationB):
    trade = {
        nationA: {
            "Relations": ["Military Access"],
                
            "Territories": ["Territory (127,118)"],

            "Resources": {"Iron": 20}
        },
        
        nationB: {
            "Relations": ["Military Access"],
                
            "Territories": ["TestB Territory (100,104)"],

            "Resources": {"Money": 5}
        }
    }
    
    testGame[nationB].mailbox["Trade Offers"][nationA] = trade
    testGame[nationB].respondToTrade(nationA, "ACCEPT", testGame)
    
    trade = {
        nationA: {
            "Relations": ["Alliance"],
                
            "Territories": [],

            "Resources": {}
        },
        
        nationB: {
            "Relations": ["Alliance"],
                
            "Territories": [],

            "Resources": {}
        }
    }
    
    testGame[nationB].mailbox["Trade Offers"][nationA] = trade
    testGame[nationB].respondToTrade(nationA, "ACCEPT", testGame)

#For testing detaching and disabling undersupplied units
def testDetachingUnitsArmy(testGame, nation, territory):
    
    testArmy = {
        "__class__": "Army",
        "__module__": "ConcertOfNations.GameObjects",
        "name": "TestArmy(Detaching Units)",
        "status": "Active",
        "composition": {
            "TestInfantry": {
                "__class__": "Division",
                "__module__": "ConcertOfNations.GameObjects",
                "name": "TestInfantry",
                "status": "Active",
                "unitType": "TestInfantry",
                "size": 1000,
                "speed": 750,
                "homeTerritory": "Test 1",
                "attack": 2,
                "defense": 2,
                "weight": 1
            },
            "TestTank": {
                "__class__": "Division",
                "__module__": "ConcertOfNations.GameObjects",
                "name": "TestTank",
                "status": "Active",
                "unitType": "TestTank",
                "size": 100,
                "speed": 750,
                "homeTerritory": "Test 1",
                "attack": 2,
                "defense": 2,
                "weight": 10
            }
        },
        "territory": territory
    }
    testArmy = FileHandling.loadObject(testArmy)
    testGame[nation].unitGroups[testArmy.name] = testArmy
    
    #Pass time to test
    for i in range(12):
        testGame.advance(4)

#For testing detaching and disabling undersupplied units FOR A NAVY
def testDetachingUnitsNavy(testGame, nation, territory):
    
    testNavy = {
        "__class__": "Fleet",
        "__module__": "ConcertOfNations.GameObjects",
        "name": "TestA Fleet 1",
        "status": "Active",
        "composition": {
            "TestLightShip": {
                "__class__": "Ship",
                "__module__": "ConcertOfNations.GameObjects",
                "name": "TestLightShip",
                "shipList": [
                    100
                ],
                "size": 1,
                "speed": 100,
                "homeTerritory": territory,
                "status": "Active"
            },
            "TestHeavyShip": {
                "__class__": "Ship",
                "__module__": "ConcertOfNations.GameObjects",
                "name": "TestHeavyShip",
                "shipList": [
                    100
                ],
                "size": 1,
                "speed": 50,
                "homeTerritory": territory,
                "status": "Active"
            }
        },
        "territory": territory,
        "embarked": {}
    }
    testNavy = FileHandling.loadObject(testNavy)
    testGame[nation].unitGroups[testNavy.name] = testNavy
    
    #Pass time to test
    for i in range(12):
        testGame.advance(4)

def testMovingUnitGroup(testGame, nation, unitGroup, destination):
    testGame[nation].unitGroups[unitGroup].moveTo(destination, testGame)

def testEmbark(testGame, nation, fleet, embarkingUnitGroup):
    testGame[nation].unitGroups[fleet].embark(testGame[nation].unitGroups.pop(embarkingUnitGroup), testGame)

def testDisembark(testGame, nation, fleet, disembarkingUnitGroup, territory):
     testGame[nation].unitGroups[fleet].disembark(disembarkingUnitGroup, territory, testGame)

#Self-explanatory
def testBuildingArmy(testGame, nation, forceType, unit, size, territory):
    testGame[nation].trainForce(forceType, unit, size, territory, testGame)

#Self-explanatory
def testBuildingProject(testGame, nation, project, territory):
    testGame[nation].buildProject(project, territory, testGame)

def testColonize(testGame, nation, numColonists, originTerr, destinationTerr):
    testGame[nation].recruitColonists(numColonists, originTerr, testGame)
    
    testGame[nation].unitGroups[f"{nation} Colonial Expedition 1"].moveTo(destinationTerr, testGame)
    
    testAdvance(testGame, 12, 3)
    
    testGame[nation].settleTerritory(f"{nation} Colonial Expedition 1", testGame)
    
    testAdvance(testGame, 12, 3)

#Advances the date by (interval) months a total of (rangeNum) times    
def testAdvance(testGame, rangeNum, interval):
    for i in range(rangeNum):
        testGame.advance(interval)

#THE ACTUAL RUNNING OF THE TEST PROCEDURE
def testProcedure():
    testGame = makeTestGame_fromImage()
    
    #testAdvance(testGame, 12, 3)

    testBuildingProject(testGame, "TestA", "TestTradeCompany", "Territory (40,48)")

    testAdvance(testGame, 12, 3)

    testBuildingArmy(testGame, "TestA", "Army", "TestInfantry", 10, "Territory (30,28)")

    testAdvance(testGame, 120, 3)
    
    testBuildingArmy(testGame, "TestA", "Army", "TestCavalry", 1, "Territory (30,28)")

    testAdvance(testGame, 120, 3)

    testBuildingArmy(testGame, "TestA", "Fleet", "TestLightShip", 1, "Territory (30,28)")

    testAdvance(testGame, 12, 3)
    
    #testTrade(testGame, "TestA", "TestB")

    testGame = end(testGame)
    
    return testGame #FileHandling.loadObject(FileHandling.saveObject(testGame))

'''    
#Tests getting the raw text data of a saveGame
fileTest = open("Savegames/Test - Test - 0.json", "r")

outFile = open("JsonToTextTest.txt", "w+")

outFile.write(fileTest.read())'''

#Bottom



















#Bottom 2 Electric Boogaloo