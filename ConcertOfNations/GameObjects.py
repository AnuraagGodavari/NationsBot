#CONCERT OF NATIONS: GAME OBJECTS.py
'''
>>> This code consists of all the buildable objects used by the Concert of Nations games and any modded versions.
>>> Each object and non-self-explanatory method will have a comment explaining their purpose.
>>> Hopefully you have fun with all this, I know I certainly did!
'''
#Copyright 2020, Anuraag Godavari, All rights reserved. Code may be used with credit to Anuraag Godavari

'''
Some references:
https://medium.com/python-pandemonium/json-the-python-way-91aac95d4041 (For using JSON to encode and decode custom objects)
'''

import json, math, pprint, time, random
from ConcertOfNations import Util, GameObjects, FileHandling, Mapping

#globalModifiers is the list of modifiers that an object can have. Cumulative modifiers are added on to, Exponential effects are multiplied.
globalModifiers = {
    "Nation": {
        "National": {
            "Cumulative": {
                "Economic Capacity": 5,
                "Military Capacity": 5,
                "Naval Capacity": 5,
                "Industrial Capacity": 5,
                "Governance Capacity": 5,
                "Infrastructure Capacity": 5,
                "Colonial Capacity": 0
            }, 
            "Exponential": {
                "Money Income": 1,
                "Technology Cost": 1,
                "Policy Cost": 1,
                "Income Modifier": 1,
                "Building Cost": 1,
                "ColonialBuilding Cost": 1,
                "Army Cost": 1,
                "Fleet Cost": 1
            },
            "Temporary": {
                "Disabled": []
            }
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
            "Exponential" : {
                "Maintenance": 1
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
                "Maintenance": 1,
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
        },
    },

    "Territory": {
        "Territorial": {
            "Cumulative": {
                "Supply": 0,
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
            "Temporary": {
            }
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
            "Exponential" : {
                "Maintenance": 1
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
                "Maintenance": 1,
            },
            "Temporary": {}
        }
    },
    
    "HabitableTerritory":  {
        "Territorial": {
            "Cumulative": {
                "Supply": 0,
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
            "Temporary": {
            }
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
            "Exponential" : {
                "Maintenance": 1
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
                "Maintenance": 1,
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

globalSettings = {
    "Nation": {
        "Projects prioritized for disabling": False
    }
}

globalBureaucracy = {
    "Economic Bureaucracy": [0, 5],
    "Military Bureaucracy": [0, 5],
    "Naval Bureaucracy": [0, 5],
    "Industrial Bureaucracy": [0, 5],
    "Governance Bureaucracy": [0, 5],
    "Infrastructure Bureaucracy": [0, 5],
    "Colonial Bureaucracy": [0, 0]
}

globalTradeTemplate = {
    "Relations": [],
        
    "Territories": [],

    "Resources": {}
}

globalRelations = ("Alliance", "Defensive Pact", "Military Access", "Trading", "War")

globalUnitRelations = Util.TwoWayDict(("Division", "Ship"), ("Army", "Fleet"))

globalSaveGameData = {

    "NationColors": {},
    
    #Territories not owned by a nation that it has knowledge of.
    "DiscoveredBy": {},

}

#A SaveGame holds all the data for one Game, including all nations, the map and gameDict being used, etc.
class SaveGame:

    def __init__ (self, name, ID, date, map, gameDict, nations = None, players = None, diplomaticRelations = None, saveGameData = None):
        self.name = name
        self.ID = ID
        self.date = date
        self.map = map
        self.gameDict = gameDict
        self.nations = nations or {}
        self.players = players or {}
        self.diplomaticRelations = diplomaticRelations or Util.RelationalMatrix(keys = self.nations.keys())
        self.saveGameData = saveGameData or globalSaveGameData
    
    #Gets the associated map object
    def getMap(self):
        if (self.map.__class__.__name__ == "Map"): return self.map #If it is a Map object, return the map itself
        
        with open(f"Maps/{self.map}") as f: #Otherwise assume it is a string for a filename
            return FileHandling.loadObject(json.load(f))
    
    #Saves an image of the current game map, returns the filename.
    def saveMapImage(self, nationToMap = None):
        colorData = {}
        
        for nation in self.nations.keys():
            colorData[nation] = {}
            colorData[nation]["Color"] = self.saveGameData["NationColors"][nation]
            colorData[nation]["Territories"] = list(self[nation].territories.keys())
        
        if (nationToMap): 
            self.getMap().toImage(f"Nation_{nationToMap}_Game_{self.name}_Date_{str(self.date).replace('/', '_')}", colorData, self.knownTerritories(nationToMap))
            return f"Maps/Nation_{nationToMap}_Game_{self.name}_Date_{str(self.date).replace('/', '_')}.png"
        
        else:
            self.getMap().toImage(f"Game {self.name} on Date {str(self.date).replace('/', '_')}", colorData)
            return f"Maps/Game {self.name} on Date {str(self.date).replace('/', '_')}.png"
    
    #Gets a list of all territories known of by a nation.
    def knownTerritories(self, nation):
        knownTerritories = []
        
        for territory in self.saveGameData["DiscoveredBy"]:
            if (nation in self.saveGameData["DiscoveredBy"][territory]): knownTerritories.append(territory)
        
        knownTerritories += list(self[nation].territories.keys())
        
        return knownTerritories
        
    #Gets a list of all territories that can be traversed by a nation.
    def traversableTerritories(self, nation):
        traversableTerritories = []
        
        for territory in self.saveGameData["DiscoveredBy"]:
            if (nation in self.saveGameData["DiscoveredBy"][territory]): 
                owner = self.getTerritoryOwner(territory)
                
                if (owner == None): traversableTerritories.append([territory])
                
                else: 
                    if (owner in self.diplomaticRelations[nation].relations):
                        if any(validRelation in ("Military Access", "War", "Alliance") for relation in self.diplomaticRelations[nation][owner]):
                            traversableTerritories.append(territory)
            
        traversableTerritories += list(self[nation].territories.keys())
    
    #Gets a list of all territories visible by a nation that it does not own.
    def visibleTerritories(self, nation):
        map = self.getMap()
        visibleTerritories = []
        
        #Go through all the neighbors of each territory in the nation
        for territory in self[nation].territories.keys():
            vert = map[territory]
            for neighbor in vert.edges.keys():
                #If this vertex is not already owned or known to be visible
                if (neighbor not in (list(self[nation].territories.keys()) + visibleTerritories)):
                    visibleTerritories.append(neighbor)
                    
        for unitGroup in self[nation].unitGroups.values():
            vert = map[unitGroup.territory]
            for neighbor in vert.edges.keys():
                if (neighbor not in (list(self[nation].territories.keys()) + visibleTerritories)):
                    visibleTerritories.append(neighbor)
        
        return visibleTerritories
    
    #Discovers all previously unknown territories adjacent to ones owned by or being traversed by a nation
    def discoverAdjacentTerritories(self, territory, nation):
        map = self.getMap()
        #Go through each neighbor of the province
        for neighbor in map[territory].edges:
            if (neighbor in self.saveGameData["DiscoveredBy"]):
                #Skip this one if its already been discovered by the nation.
                if (nation in self.saveGameData["DiscoveredBy"][neighbor]): continue
                
            else: self.saveGameData["DiscoveredBy"][neighbor] = []
                
            self.saveGameData["DiscoveredBy"][neighbor].append(nation)
    
    #Returns territory object if it exists in a nation, or a new territory object based on the corresponding vertex in the map.
    def getTerritory(self, territoryName):
        for nation in self.nations.values():
            if territoryName in nation.territories:
                return nation.territories[territoryName]
        
        mapTerr = FileHandling.saveObject(self.getMap()[territoryName])
        
        #If not owned by any nation:
        if (mapTerr["details"]["type"] == "LandTerritory"):
            return ColonialTerritory.fromDict(mapTerr)
            
        else:
            return Territory.fromDict(mapTerr)
        
    #Gets a territory from the saveGame map
    def getTerritoryFromMap(self, territoryName):
        return Territory.fromDict(FileHandling.saveObject(self.getMap()[territoryName]))
    
    #Gets a territory from whichever nation it belongs to. OBSOLETE?
    def getTerritoryFromNations(self, territoryName):
        for nation in self.nations.values():
            if territoryName in nation.territories:
                return nation.territories[territoryName]
        return None
    
    #Defines the diplomatic relations between two nations.
    def relateNations(self, relation, *nations):
        self.diplomaticRelations.relate(relation, *nations)
        
    def breakRelations(self, *nations, relation = None):
        if (relations): self.diplomaticRelations.clearRelations(*nations)
        else: self.diplomaticRelations.removeRelation(relation, *nations)
    
    #Gets the relation between two nations
    def relation(self, nation0, nation1):
        return self.diplomaticRelations[nation0][nation1]
    
    #Sends resources, cede territories, establishes relations between two nations
    def trade(self, arg0, arg1, trade):
        for relation in trade[arg0]["Relations"]:
            self.relateNations(relation, arg0, arg1)
            
        for counter in range(2):
            givingNationName = (arg0, arg1)[counter]
            
            recievingNation = self[(arg1, arg0)[counter]]
            
            for territory in trade[givingNationName]["Territories"]:
                recievingNation.annexTerritory(self[givingNationName].cedeTerritory(territory, self), self)
            
            for resource in trade[givingNationName]["Resources"]:
                #Remove the resource from the giving nation's inventory
                self[givingNationName].resources[resource] -= trade[givingNationName]["Resources"][resource]
                #Add the resource to the recieving nation's inventory.
                recievingNation.resources[resource] += trade[givingNationName]["Resources"][resource]
            
    #Gets the gameDict json dictionary
    def getGameDict(self):
        if isinstance(self.gameDict, dict): return self.gameDict #If it is a dictionary, return the game dictionary itself

        with open(f"Dictionaries/{self.gameDict}") as f: #Otherwise assume it is a string for a filename
            return json.load(f).copy()
    
    #Advances the ingame date
    def advance(self, numMonths): 
        oldYear = self.date.year #Year value of the current date
        self.date.advance(numMonths)
        
        if self.date.year > oldYear: #If more than a year has passed:
            self.onNewYear(self.date.year - oldYear) #Perform the onNewYear function
            
        else:
            self.onNewTurn(numMonths) #Perform regular newTurn function
    
    #Whenever a new year has happened
    def onNewYear(self, numNewYears):
        for nation in self.nations.keys(): #Perform each nation's onNewYear
            self[nation].onNewYear(self.date, numNewYears, self)
    
    #Whenever a new non-year turn has happened
    def onNewTurn(self, numMonths):
        for nation in self.nations.keys(): #Perform each nation's onNewTurn
            self[nation].onNewTurn(self)
    
    #Add a nation to the saveGame
    def addNation(self, index, nation = None, mapColors = None):
        self.nations[index] = nation or Nation(index)
        self.saveGameData["NationColors"][index] = mapColors or [random.randint(1, 255), random.randint(1, 255), random.randint(1, 255), 255]
        
        self.diplomaticRelations.addRelation(index)
        
        if self.nations[index].resources == {}:
        
            #FOR POSSIBLE REFERENCE: self.nations[index].resources = { resource : 0 for resource in self.getGameDict()["Basic Resources"].copy()} #Gives the nation a list of resources all equal to 0 from a list of resources
            self.nations[index].resources = Util.combineDicts (self.getGameDict()["Basic Resources"].copy(), self.getGameDict()["Manufactured Resources"].copy())
            
            if "Money" not in self.nations[index].resources.keys(): #Money is an optional entry in the resources dictionary: If it is in the dictionary, then it is only to get a default value.
                self.nations[index].resources["Money"] = 5000
    
            for resource in self.nations[index].resources.keys(): #Generates income modifiers for all the ingame resources
                self.nations[index].modifiers["National"]["Exponential"][f"{resource} Income"] = 1
    
    #Find who owns a specific territory
    def getTerritoryOwner(self, territory):
        for nation in self.nations.values():
            if (territory in nation.territories.keys()): return nation.name
        
        return None
    
    #Checks if there is any unitGroup in the passed territory
    def unitGroupsInTerritory(self, territory, *excludedNations):
        unitGroups = {}
        for nation in self.nations.keys():
            
            if (nation in excludedNations): continue
            
            for unitGroup in self[nation].unitGroups.values():
                if (unitGroup.territory == territory):
                    if (nation not in unitGroups.keys()): unitGroups[nation] = []
                
                    unitGroups[nation].append(unitGroup)
                    
        return unitGroups
    
    #Get a nation from SaveGame easily
    def __getitem__ (self, item): #Calling this would look like: nationExample = saveGame[item]
        #If item is a playerID, redefine item to the nation associated with the player ID.
        if (item in self.players.keys()): item = self.players[item]
        
        return self.nations[item] #Returns a nation object from the saveGame's nations object
    
    #Set a nation from SaveGame easily
    def __setitem__(self, index, value = None): #Similar to __getitem__, where a nation is set to a new value.
        self.addNation(index, value)

#A Nation object, more or less the same thing as a player.
class Nation: 
    def __init__ (self, name, resources = None, bureaucracy = None, territories = None, modifiers = None, unitGroups = None, loans = None, technologies = None, policies = None, creditScore = 0, mailbox = None, settings = None):
        #name is the full name of the nation.
        self.name = name 
        #resources is the dictionary of all resources, with the keys being their names and the values being lists of the format [{Amount in reserves}, {Growth amount}]
        self.resources = resources or {}
        #bureaucracy is a dictionary of 2-entry lists. The keys are categories for government bureaucracy/projects (Military, Economic, etc.) and the values look like [current project space taken up, maximum project space]
        self.bureaucracy = bureaucracy or globalBureaucracy.copy()
        #territories is a dictionary of all the territories owned by the nation.
        self.territories = territories or {}
        #modifiers modify certain values in the nation. For example. modifiers["Exponential"]["Revenue"] is a multiplier for the monetary income of the nation.
        self.modifiers = modifiers or globalModifiers["Nation"].copy()
        #unitgroups is a dictionary of unit group objects. Each unit group has a number of units specific to its type: for example, an army unit group has infantry, cavalry and artillery units.
        self.unitGroups = unitGroups or {}
        #loans is a list of loan objects that the nation has taken on - a representation of the nation's current debt. 
        self.loans = loans or []
        #technologies is a list of the names of technologies that the nation has unlocked.
        self.technologies = technologies or []
        #policies is a list of the names of laws passed by the nation.
        self.policies = policies or []
        #credit score is a measure of how often a country pays back its loan payments, from -100 to 100.
        self.creditScore = creditScore or 0
        #mailbox is a collection of all messages and trade offers from other nations.
        self.mailbox = mailbox or {"Mail": {}, "Trade Offers": {}}
        #settings is a dictionary of player-toggled settings for the nation.
        self.settings = settings or globalSettings["Nation"].copy()
    
    #All events that happen on a new turn, irrespective of it being a new year
    def onNewTurn(self, saveGame):
        newDate = saveGame.date
        gameDict = saveGame.getGameDict()
        
        newTurnEffects = {"Effects": {"Nation": {}}}
        for territory in self.territories.values():
            #If this is a colonial territory and the colonial progress is >= 100, convert it to a regular territory.
            if (territory.__class__ == ColonialTerritory):
                if (territory.colonialProgress[0] >= territory.colonialProgress[1]):
                    convertedTerr = HabitableTerritory.fromColonialTerritory(self.territories.pop(territory.name))
                    self.territories[convertedTerr.name] = convertedTerr
        
            else: newTurnEffects = Util.combineDicts(newTurnEffects, territory.onNewTurn(newDate, gameDict))
            
        self.applyEffects(newTurnEffects.pop("Effects"))
        
        for unitGroup in self.unitGroups.values():
            newTurnEffects = unitGroup.onNewTurn(newTurnEffects, saveGame)
        
        for category in newTurnEffects.keys():
            self.bureaucracy[f"{category} Bureaucracy"][0] -= newTurnEffects[category]
    
    #All events in the nation when a new year occurs.
    def onNewYear(self, newDate, numNewYears, saveGame):
        
        self.onNewTurn(saveGame)
        
        gameDict = saveGame.getGameDict()
        map = saveGame.getMap()
        
        newYearEffects = {"Maintenance": {}, "Revenue": {}}
        
        for territory in self.territories.keys():
        
            newYearEffects = Util.combineDicts(newYearEffects, self.territories[territory].onNewYear(newDate, self.modifiers, gameDict, map))
        
        for unitGroup in self.unitGroups.values():
            territoryModifiers = saveGame.getTerritory(unitGroup.territory).modifiers
            
            unitGroupEffects = unitGroup.onNewYear(gameDict, self.modifiers, territoryModifiers)
            
            newYearEffects = Util.combineDicts(newYearEffects, unitGroupEffects)
        
        #Removes resources due to maintenance
        for resource in newYearEffects["Maintenance"].keys():
            self.resources[resource] -= newYearEffects["Maintenance"][resource] * numNewYears * self.modifiers["National"]["Exponential"][f"{resource} Income"]
        
        #Adds resources due to revenue
        for resource in newYearEffects["Revenue"].keys():
            self.resources[resource] += newYearEffects["Revenue"][resource] * numNewYears * self.modifiers["National"]["Exponential"][f"{resource} Income"]
        
        self.handleLoans(saveGame)
        
        #Checks if any resource is in a deficit
        for resource in self.resources.keys():
            if self.resources[resource] < 0:
                
                if resource == "Money": #If the resource is money, take on a loan based on the deficit.
                    loanAmount = self.resources["Money"] * -2
                    
                    self.takeOnLoan(loanAmount, newDate, 60)
                    
                else:
                    self.handleDeficits(resource, newYearEffects, saveGame)
                    
        self.creditScore = Util.bound(-100, self.creditScore, 100)
    
    #Gets the total economic size of the nation
    def revenue(self, saveGame):
        gameDict = saveGame.getGameDict()
        revenue = 0
        
        for territory in self.territories.keys():
            revenue += self.territories[territory].revenue(gameDict)
            
        return revenue
    
    #Gets all the revenues of all resources of the nation.
    def resourceRevenue(self, saveGame):
        gameDict = saveGame.getGameDict()
        revenues = {resource: 0 for resource in self.resources.keys()}
        
        for territory in self.territories.keys():
            revenues = Util.combineDicts(revenues, self.territories[territory].resourceRevenue(gameDict))
            
        return revenues
    
    #Responds with "ACCEPT" or "DENY" to a nation's trade request.
    def respondToTrade(self, targetNation, response, saveGame):
        if (response == "ACCEPT"):
            saveGame.trade(self.name, targetNation, self.mailbox["Trade Offers"].pop(targetNation))
            
        elif (response == "DENY"):
            self.mailbox["Trade Offers"].pop(targetNation)
    
    ''' TRADE OFFER FUNCTION
    #Offers a trade to another nation. Concessions/Gains formatted similarly to: ("MilitaryAccess", "DefensivePact", "Territory1", ("Iron": 1))
    def offerTrade(self, tradeConcessions, targetNation, tradeGains, saveGame):
        tempTuple = (tradeConcessions, tradeGains)
        tradeDict = globalTradeTemplate.copy()
        
        for counter in range(2):
            trade = tempTuple[counter]
            
            #Goes through each item in the trade and assigns it by category
            for tradeItem in trade:
                #If it is a type of diplomatic relation
                if (tradeItem in globalRelations):
                    trade["Relations"].append(tradeItem)
                
                #If it is a territory owned by one of the two nations
                elif (tradeItem in (self, saveGame[targetNation])[counter].territories.keys()):
                    trade["Territories"].append(tradeItem)
                
                #If it is a tuple (it's probably a resource
                elif (isinstance(tradeItem, tuple)): 
                    #Check to see if tuple[0] is a resource
                    if tradeItem[0] in self.resources:
                        #Check to see if the trade is affordable
                        if (self.resources[tradeItem[0]] > tradeItem[1]):
                            trade["Resources"][tradeItem[0]] = tradeItem[1]
    '''
    
    #Goes through each of the loans in the nation and makes a payment if possible
    def handleLoans(self, saveGame):
            loansToKeep = []
            
            for loanIndex in range(len(self.loans)):
                loan = self.loans[loanIndex]
                paymentRequired = loan.minimumPayment()
                
                if(loan.status == "DEFAULTED"):
                    self.creditScore -= max(0, 100*(loan.originalBalance/(self.revenue(saveGame))))
                    self.creditScore = Util.bound(-100, self.creditScore, 100)
                    continue
                
                if (self.resources["Money"] >= paymentRequired):
                    self.resources["Money"] -= paymentRequired
                    loan.makePayment(paymentRequired)
                    
                else:
                    loan.addStrike()
                
                #If the loan has not been fully repaid, make sure to keep it
                if (loan.balancePaid < loan.originalBalance):
                    loansToKeep.append(loan)
                
                #If the loan HAS been repaid, add an amouunt to the national credit score.
                else:
                    self.creditScore += max(0, 100*(loan.originalBalance/(self.revenue(saveGame) * 2)))
                
                if (loan.strikes() > 3):
                    self.creditScore -= 100*(loan.minimumPayment()/self.revenue(saveGame))
                    self.foreclosures(loan, saveGame, loan.minimumPayment())
                    
                elif (loan.__class__.__name__ == "TimelyLoan"):
                    if (loan.dueDate > saveGame.date):
                         self.foreclosures(loan, saveGame, loan.originalBalance - loan.balancePaid)
            
            self.loans = loansToKeep
        
    #Gives the nation a loan based on a loan amount, its credit score and (possibly) the current date.
    def takeOnLoan(self, loanAmount, startDate, loanTime = None):
        interestRate = Loan.calculateInterest(self.creditScore)
        
        loanID = f"{self.name} LOAN:{startDate}"
        
        if (loanTime):
            self.loans.append(TimelyLoan(loanID, loanAmount, interestRate, startDate.newDate(0), startDate.newDate(loanTime)))
            
        else:
            self.loans.append(IndefiniteLoan(loanID, loanAmount, interestRate, startDate))
        
        self.resources["Money"] += loanAmount
        
        self.creditScore = Util.bound(-100, self.creditScore - 10, 100)
    
    #Destroys projects to pay for a loan this turn. mode can be "Full Balance" or "Monthly Balance"
    def foreclosures(self, inLoan, saveGame, paymentRequired):
        undersuppliedProjects = self.disableableProjects("Money", saveGame).inorder()
        
        #If there are no deletable projects, exit the function
        if not(undersuppliedProjects):
            return 0
        
        counter = 0
        #While there is a balance remaining and both undersupplied lists have been exhausted
        while((paymentRequired > 0) & (counter < len(undersuppliedProjects))):
            info = undersuppliedProjects[counter].split(':')
            
            foreclosureInfo = self.territories[info[0]].foreclose(info[1], saveGame)
            
            paymentRequired -= foreclosureInfo["Money from Foreclosure"]
            self.applyEffects(foreclosureInfo["Nation"], "REMOVE")
            self.territories[info[0]].applyEffects(foreclosureInfo["Territory"], "REMOVE")
            
            counter += 1
            
        if (paymentRequired > 0):
            print(f"NO MORE PROJECTS TO FORECLOSE FOR LOAN <{inLoan.loanID}>")
            inLoan.status = "DEFAULTED"
        
        else: inLoan.removeStrike()
    
    #Performs resource deficit actions
    def handleDeficits(self, resource, newYearEffects, saveGame):
        gameDict = saveGame.getGameDict()
        
        #Current resource deficit = the amount of that resource in the negative. Must be able to recoup losses next turn.
        deficit = self.resources[resource]
        
        if (resource in newYearEffects["Maintenance"].keys()): deficit -= newYearEffects["Maintenance"][resource]
        
        if (resource in newYearEffects["Revenue"].keys()):
            deficit += newYearEffects["Revenue"][resource]
        
        #All revenue this turn
        nationRevenues = newYearEffects["Revenue"]
        
        undersuppliedUnits = self.disableableUnitGroups(resource, saveGame)
        undersuppliedProjects = self.disableableProjects(resource, saveGame)
        
        #Algorithm to disable projects and armies
        traversing = None #Current list of deletable projects/armies
        keepGoing = 2 #When keepGoing = 0, stop loop.
        
        if (self.settings["Projects prioritized for disabling"]): traversing = undersuppliedProjects.inorder()
        else: traversing = undersuppliedUnits.inorder()
        
        #If there are no deletable projects, set deficit = 1 to avoid the loop altogether
        if not(undersuppliedProjects or undersuppliedUnits):
            keepGoing = False
        
        #Loop to delete projects and armies, based on if deficit is still negative
        #-------------------------------------------------------------------------
        #
        #
        #
        
        counter = 0
        while((deficit < 0) & (keepGoing > 0)):
        
            #If traversing has been fully traversed:
            if (counter >= len(traversing)):
                if not(keepGoing): break
                
                keepGoing -= 1 #Goes down every time traversing is emptied, meaning twice. When the second time hits, the loop will stop after this.
                counter = 0 #resets the counter
                
                #If we should delete projects first, it means that traversing has deleted all resource-lacking projects.
                if (self.settings["Projects prioritized for disabling"]):
                    traversing = undersuppliedUnits.inorder()
                
                #If we should delete armies first, it means that traversing has deleted all resource-undersupplied armies.
                else:
                    traversing = undersuppliedProjects.inorder()
                    
                continue
            
            #Add things to the resource-lacking objects list
            deficitInfo = self.disableObject(traversing[counter], saveGame, resource)
            deficit += deficitInfo["Cost"]
            
            counter += 1
    
    #Gets BinDescTree of all projects in the entire nation that require a specific resource
    def disableableProjects(self, resource, saveGame):
        gameDict = saveGame.getGameDict()
        undersuppliedProjects = Util.BinDescTree()
        
        #Go through each project in each territory, add to "undersuppliedProjects" if it requires the resource at a deficit
        for territory in self.territories.values():
            #For each project in each territory, add to undersuppliedProjects if it requires this resource.
            for project in territory.projects.values(): 
                #Skip this project if it is already disabled
                if (project.status == "Disabled"): continue
            
                requiredResources = project.getData(gameDict)["Maintenance Costs"]
                
                #If this project requires this resource, add it to the Binary Descriptor Tree.
                if ((resource in requiredResources.keys()) & (f"{territory.name}:{project.name}" not in self.modifiers["National"]["Temporary"]["Disabled"])): 
                    
                    #avgRatio will be the average percentage of revenue this project provices for each resource it earns in revenue.
                    avgRatio = 0
                    #nationRevenues is the amount of each resource gained in revenue by the nation last turn.
                    nationRevenues = self.resourceRevenue(saveGame)
                    numResources = 0
                    
                    revenues = project.getData(gameDict)["Revenue"]
                    for revenue in revenues.keys():
                        if not(revenue == resource):
                            
                            #Add to avgRatio the ratio of this projects revenue in a resource to the overall national revenue in that resource. Will divide avgRatio by numResources at the end.
                            avgRatio += (revenues[revenue] / (nationRevenues[revenue] or 1))
                            numResources += 1
                    
                    if (numResources): avgRatio /= numResources
                    
                    #projectWeight = (resourceCost - (avgRatio/resourceCost))
                    undersuppliedProjects.insert(requiredResources[resource] - (avgRatio / requiredResources[resource]), f"{territory.name}:{project.name}")
        
        return undersuppliedProjects
    
    #Gets BinDescTree of all units belonging to the each of the Nation's unit groups that require a specific resource.
    def disableableUnitGroups(self, resource, saveGame):
        gameDict = saveGame.getGameDict()
        undersuppliedUnits = Util.BinDescTree()
        #Go through each unitGroup and add to "undersuppliedUnits" if it requires the resource at a deficit
        for unitGroup in self.unitGroups.values():
        
            #Skip this unitGroup if it is already disabled
            if ((unitGroup.status == "Disabled") or (unitGroup.name in self.modifiers["National"]["Temporary"]["Disabled"])):
                continue
            
            for unit in unitGroup.composition.values(): #For each unit in each unitGroup, add to undersuppliedProjects if it requires this resource.
                requiredResources = unit.getData(gameDict)["Maintenance Costs"]
                
                if (resource in requiredResources.keys()): #If this project requires this resource, add it to the Binary Descriptor Tree.
                    
                    #unitGroupWeight = (size - (resourceCost/size))
                    undersuppliedUnits.insert(unit.size - (requiredResources[resource]/unit.size), f"{unitGroup.name}:{unit.name}")
                    
        return undersuppliedUnits
    
    #Disables a GameObject owned by the nation.
    def disableObject(self, objectName, saveGame, resource = None):
        
        #If this is a project, info[0] is the territory and info[1] is the project name
        info = objectName.split(':')
        rtnInfo = {}
        
        if (info[0] in self.unitGroups.keys()): #If this object is a unitGroup, detach the resource-intensive unit from the army and disable.
            
            #obj is the actual instance to which objectName refers.
            obj = self.unitGroups[info[0]]
            rtnInfo = obj.disableUnit(info[1], saveGame, self.name, resource)
            
            
            if ("Disabled Unit" in rtnInfo.keys()):
                #Get new Unit Group name for the new object
                objectName = self.getNewForceName(self.unitGroups[info[0]].__class__.__name__)
                
                #Brute-forced blueprint for the new unit
                blueprint = {
                    "__class__": self.unitGroups[info[0]].__class__.__name__,
                    "__module__": "ConcertOfNations.GameObjects",
                    "name": objectName,
                    "composition": {rtnInfo["Disabled Unit"].name: rtnInfo["Disabled Unit"]},
                    "territory": self.unitGroups[info[0]].territory,
                    "status": "Disabled"
                }
                self.unitGroups[objectName] = FileHandling.loadObject(blueprint)
                
            else:
                objectName = info[0]
            
        else: #This object is a project
            obj = self.territories[info[0]]
            rtnInfo["Cost"] = obj.projects[info[1]].disable(saveGame, resource)
            
            oldEffects = obj.projects[info[1]].getData(saveGame.getGameDict())["Completion Effects"]
            self.applyEffects(oldEffects["Nation"], "REMOVE")
            obj.applyEffects(oldEffects["Territory"], "REMOVE")
        
        #Adds the object's name to a list of nationally disabled objects.
        self.modifiers["National"]["Temporary"]["Disabled"].append(objectName)
        
        return rtnInfo
    
    #Builds a GameObject in a territory in the nation.
    def buildProject(self, project, territory, saveGame):
        currentDate = saveGame.date
        gameDict = saveGame.getGameDict()
        
        for objectType in gameDict["Game Objects"]: #gameDicts are structured in a way similar to this: gameDict["Game Objects]["Buildings"]["Barracks"]. This key would return the project blueprints for "Barracks".
            if project in gameDict["Game Objects"][objectType]:
                blueprint = gameDict["Game Objects"][objectType][project].copy()
                break
                
        if (self.canBuildProject(blueprint, territory, saveGame)): #If the project is practically buildable:
        
            #if objectType in ("Divisions", "Ships"): #If it is a type of unit, then this method was called by trainForce, so return True to that method. IS THIS NECESSARY?
                #return True
               
            #If the method has reached this point, project is a building
            self.territories[territory].buildProject(blueprint, currentDate)
            
            #Subtracts all required resources.
            for resource in blueprint["buildingCosts"]["resourceCosts"]:
                self.resources[resource] -= blueprint["buildingCosts"]["resourceCosts"][resource] * self.modifiers["National"]["Exponential"]["Building Cost"]
            
            category = blueprint["category"]
            self.bureaucracy[f"{category} Bureaucracy"][0] += blueprint["buildingCosts"]["size"]
    
    #Destroys a named project in a territory.
    def destroyProject(self, projectName, territory, saveGame):
        project = self.territories[territory].projects.pop(projectName)
        
        oldEffects = project.getData(saveGame.getGameDict())["Completion Effects"]
        self.applyEffects(oldEffects["Nation"], "REMOVE")
        self.territories[territory].applyEffects(oldEffects["Territory"], "REMOVE")
    
    #Starts building an army comprised entirely of one unit, if possible
    def trainForce(self, unitGroupType, unitType, unitSize, territory, saveGame):
        currentDate = saveGame.date
        gameDict = saveGame.getGameDict()
        
        for unitName in gameDict["Game Objects"]: #gameDicts are structured in a way similar to this: gameDict["Game Objects]["Buildings"]["Barracks"]. This key would return the project blueprints for "Barracks".
            if unitType in gameDict["Game Objects"][unitName]:
                
                blueprint = gameDict["Game Objects"][unitName][unitType].copy()
                
                if (unitGroupType == "Army"):
                    blueprint["unitManpowerSize"] = unitSize
                    
                elif (unitGroupType == "Fleet"):
                    blueprint["unitManpowerSize"] = unitSize * blueprint["buildingCosts"]["manpowerCost"]
                break
        
        if self.canBuildProject(blueprint, territory, saveGame):
            newName = self.getNewForceName(unitGroupType)
            
            blueprint["unitType"] = unitType
            blueprint["homeTerritory"] = territory
            
            #If the unitGroup is an Army, add size in number of people to blueprint
            if (unitGroupType == "Army"):
                blueprint["size"] = unitSize
                self.territories[territory].recruitForUnitGroup(unitSize)
            
            #If the unitGroup is a Fleet, add unitList as a list of healths of the ships.
            elif (unitGroupType == "Fleet"):
                blueprint["unitList"] = [100] * unitSize
                self.territories[territory].recruitForUnitGroup(unitSize * blueprint["buildingCosts"]["manpowerCost"])
                
                
            #name, composition, territory, status = "Active"
            groupBlueprint = {
                "__class__": unitGroupType,
                "__module__": "ConcertOfNations.GameObjects",
                "name": newName,
                "nation": self.name,
                "composition": {unitType: FileHandling.loadObject(blueprint)},
                "territory": territory
            }
            
            self.unitGroups[newName] = FileHandling.loadObject(groupBlueprint)
            
            self.unitGroups[newName].addProcess(f"Building {unitSize} of {unitType}", currentDate.newDate(blueprint["buildTime"]))
            
            #Subtracts all required resources.
            for resource in blueprint["buildingCosts"]["resourceCosts"]:
                costModifier = self.modifiers["National"]["Exponential"][unitGroupType + " Cost"]
                self.resources[resource] -= blueprint["buildingCosts"]["resourceCosts"][resource] * costModifier
            
            category = blueprint["category"]
            self.bureaucracy[f"{category} Bureaucracy"][0] += blueprint["buildingCosts"]["size"]
            
            return self.unitGroups[newName]
        
        else: return False #UnitGroup cannot be built
        
    #Recruits a colonial expedition from a territory's population
    def recruitColonists(self, numColonists, territory, saveGame):
        #If the colonial bureaucracy has enough space
        if ((self.bureaucracy["Colonial Bureaucracy"][1] - self.bureaucracy["Colonial Bureaucracy"][0]) > 0):
            #Gets all the demographics from the population that will be part of the new colony
            demographicComposition = self.territories[territory].recruitColonists(numColonists, saveGame)
            #If colonists were able to be recruited
            if (demographicComposition):
                colonist = Colonist(f"{territory} Colonist", numColonists, "SPEED", self.name, demographicComposition)
                colonialExpedition = Expedition(self.getNewForceName("Colonial Expedition"), {colonist.name: colonist}, territory)
                self.unitGroups[colonialExpedition.name] = colonialExpedition
    
    #If the specified expedition is in an uncolonized territory, it settles down in that territory.
    def settleTerritory(self, expeditionName, saveGame):
        expedition = self.unitGroups.pop(expeditionName)
        
        #If the territory has no owner
        if not(saveGame.getTerritoryOwner(expedition.territory)):
            territory = saveGame.getTerritory(expedition.territory)
            
            for unit in expedition.composition.values():
                if (unit.__class__ == SpecialistTeam):
                    print("Nation.settleTerritory(): DO SPECIALISTS WHEN SETTLING")
                elif (unit.__class__ == Colonist):
                    territory.demographics = Util.combineDicts(territory.demographics, unit.demographicComposition)
            
            self.annexTerritory(territory, saveGame)
            
        else:
            self.unitGroups[expedition.name] = expedition
    
    #Returns a new name for a new forceType (Army, Fleet, etc.) using getNewForceNum.
    def getNewForceName(self, forceType, num = 1):
        #Returns a new automatically-generated army name's number.
        def getNewForceNum(self, forceType, num = 1):
            if (len(self.unitGroups) > 0 & num == 1): #When the recursion starts, by default the starting number will be the number of unit groups.
                for unitGroup in self.unitGroups: 
                    if unitGroup.__class__.__name__ == forceType: #Goes through all unitGroups in self.unitGroups matching the group type, and num = the number of them + 1.
                        num += 1
                    
            for group in self.unitGroups.values(): #Recursion: Goes through the matching unitGroups and, if the number is in any army's name, it raises the number by 1 and calls the function recursively.
                if group.name == f"{self.name} {forceType} {num}":
                    return getNewForceNum(self, forceType, num+1)
            return num
            
        num = getNewForceNum(self, forceType, num)
        return f"{self.name} {forceType} {num}"
    
    #Checks if a country is able to build a requested project.
    def canBuildProject(self, blueprint, territory, saveGame):
        #Checks if the required technology is either unlocked by the nation or is None.
        unlockedTech = blueprint["buildingCosts"]["techRequirement"] in (None, self.technologies)
        
        #Checks to see if the nation's bureaucracy is not over-filled
        category = blueprint["category"]
        enoughSpace = blueprint["buildingCosts"]["size"] <= self.bureaucracy[f"{category} Bureaucracy"][1] - self.bureaucracy[f"{category} Bureaucracy"][0]
        
        #Calls the target territory's canBuild method to see if it can be built there
        if territory in self.territories: territoryCanBuild = self.territories[territory].canBuild(blueprint, saveGame)
        else: return False
        
        #Assume that we have enough resources unless one of the resource costs exceeds the reserves of that resource in the nation.
        enoughResources = True
        for resource in blueprint["buildingCosts"]["resourceCosts"]:
            if blueprint["__class__"] in Unit.subclasses: 
                #Modifier for cost if it is a unit (i.e. Army Cost, Fleet Cost modifiers)
                costModifier = self.modifiers["National"]["Exponential"][globalUnitRelations[blueprint["__class__"]] + " Cost"]\
                
            else: costModifier = self.modifiers["National"]["Exponential"][blueprint["__class__"] + " Cost"]
                
            if (blueprint["buildingCosts"]["resourceCosts"][resource] > (self.resources[resource] * costModifier)):
                enoughResources = False
                break
        
        #print(unlockedTech, enoughSpace, territoryCanBuild, enoughResources)
        return (unlockedTech & enoughSpace & territoryCanBuild & enoughResources)
        
    def applyEffects(self, effects, mode = "ADD"):
        if not(effects): return 0
        if (mode == "ADD"):
            self.modifiers = Util.combineDicts(self.modifiers, effects["Nation"])
            
        elif (mode == "REMOVE"):
            #effects[effectType] may represent a case, for example, where effects is overallEffects["Nation"] and effectType is "National"
            for effectType in effects:
            
                for modifier in effects[effectType]["Cumulative"]:
                    self.modifiers[effectType]["Cumulative"][modifier] -= effects[effectType]["Cumulative"][modifier]
                    
                for modifier in effects[effectType]["Exponential"]:
                    self.modifiers[effectType]["Exponential"][modifier] -= effects[effectType]["Exponential"][modifier]
                    
        #Reloads the National bureaucracy to meet the modifiers.
        for category in self.bureaucracy:
            self.bureaucracy[category][1] = self.modifiers["National"]["Cumulative"][f"{category.split()[0]} Capacity"]
        
    def annexTerritory(self, territory, saveGame):
        self.territories[territory.name] = territory
        self.applyEffects(territory.retrieveEffects(saveGame))
        
        saveGame.discoverAdjacentTerritories(territory.name, self.name)
        
        #If any project in the territory is disabled, add to the national list of disabled objects
        for project in territory.projects.values():
            if (project.status == "Disabled"): 
                self.modifiers["National"]["Temporary"]["Disabled"].append(f"{territory.name}:{project.name}")
        
        #If the territory was known to the nation, remove it from "DiscoveredBy" dictionary.
        if (territory.name in saveGame.saveGameData["DiscoveredBy"]):
            if (self.name in saveGame.saveGameData["DiscoveredBy"][territory.name]):
                saveGame.saveGameData["DiscoveredBy"][territory.name].remove(self.name)
        
    def cedeTerritory(self, territory, saveGame):
        if (isinstance(territory, str)): territory = self.territories[territory]
        
        self.applyEffects(territory.retrieveEffects(saveGame), "REMOVE")
        
        newDisabledList = []
        #Remove all disabled objects in this territory (NOTE: This could probably be done better with a map and lambda or something but idc)
        for disabledObject in self.modifiers["National"]["Temporary"]["Disabled"]:
            #If the disabled entry is not in the territory being ceded
            if not(disabledObject.split(':')[0] == territory.name):
                newDisabledList.append(disabledObject)
                
        self.modifiers["National"]["Temporary"]["Disabled"] = newDisabledList
        
        if (territory.name not in saveGame.saveGameData["DiscoveredBy"]): saveGame.saveGameData["DiscoveredBy"][territory.name] = []
        saveGame.saveGameData["DiscoveredBy"][territory.name].append(self.name)
        
        return self.territories.pop(territory.name)
    
#A date object that can advance itself
class Date:
    def __init__(self, month, year):
        self.month = month
        self.year = year
    
    #Number of Months from year 0
    def numMonths(self):
        return self.month + (self.year*12)

    #Advance the date by a number of months
    def advance(self, amtMonths):
        self.month += amtMonths
        if self.month > 12:
            numNewYears = int(self.month/12)
            self.year += numNewYears
            self.month = 1
        return self
    
    #Get a copy of this date but advanced by a certain amount
    def newDate(self, amtMonths):
        return Date(self.month, self.year).advance(amtMonths)
        
    def fromStr(dateString):
        return Date(int(dateString.split('/')[0]), int(dateString.split('/')[1])) 
    
    def __str__(self): #conversion to a string
        return f"{self.month}/{self.year}"
        
    #Date Comparators:
    def __eq__(self, other):
        return (self.numMonths() == other.numMonths())

    def __ne__(self, other):
        return (self.numMonths() != other.numMonths())

    def __lt__(self, other):
        return (self.numMonths() < other.numMonths())

    def __le__(self, other):
        return (self.numMonths() <= other.numMonths())

    def __gt__(self, other):
        return (self.numMonths() > other.numMonths())

    def __ge__(self, other):
        return (self.numMonths() >= other.numMonths())

#A loan is an amount of money lent to a government that must be paid back over time or through interest.
class Loan:
    def __init__(self, loanID, originalBalance, interestRate, status = "Good Standing", balancePaid = 0):
        self.loanID = loanID
        self.originalBalance = originalBalance
        self.interestRate = interestRate
        self.status = status
        self.balancePaid = balancePaid
    
    #The amount of money that is required to be paid every year while the loan is in effect
    def minimumPayment(self):
        return 0
    
    #Pays off at least part of the interest and anything beyond that goes towards paying off the balance.
    def makePayment(self, amount):
        #If it is more than or equal to the interest payment, pay off the interest and if possible at least part of the balance
        if (amount  >= self.minimumPayment()):
            self.removeStrike()
            
            self.balancePaid += amount
            
            if (self.originalBalance - self.balancePaid <= 0):
                print(f"LOAN <{self.loanID}> PAID OFF!")
        
    #Gets the number of strikes on this loan
    def strikes(self):
        if ("Strike" in self.status):
            return int(self.status.split(':')[1])
        return 0
    
    #Adds a strike for missed payment to this loan
    def addStrike(self):
        if ("Strike" in self.status):
            strikes = int(self.status.split(':')[1]) + 1
        else: strikes = 0
        self.status = f"Strike:{strikes}"
        
    #Removes a strike for missed payment to this loan
    def removeStrike(self):
        if ("Strike" in self.status):
            strikes = int(self.status.split(':')[1]) - 1
            #If there are more than 0 strikes, just subtract the number of strikes
            if (strikes > 0): self.status = f"Strike:{strikes}"
            #Else, make it "Good Standing"
            else: self.status = "Good Standing"
    
    #Not tied to any specific instance. calculates interest from a credit score.
    def calculateInterest(creditScore):
        return (0.000003 * (creditScore**2)) - (0.0012 * creditScore) + 0.1
    
#A loan without a due date
class IndefiniteLoan(Loan):
    def __init__ (self, loanID, originalBalance, interestRate, status = "Good Standing", balancePaid = 0):
        Loan.__init__(self, loanID, originalBalance, interestRate, status, balancePaid)
        
    def minimumPayment(self):
        return self.originalBalance * self.interestRate

#A loan with a due date
class TimelyLoan(Loan):
    def __init__ (self, loanID, originalBalance, interestRate, creationDate, dueDate, status = "Good Standing", balancePaid = 0):
        Loan.__init__(self, loanID, originalBalance, interestRate, status, balancePaid)
        self.creationDate = creationDate
        self.dueDate = dueDate
        
    def minimumPayment(self):
        return (self.originalBalance / max(self.dueDate.year - self.creationDate.year, 1)) #max prevents from dividing by 0

#Any physical object on the game map.
class GameObject:
    def __init__(self, name, status = "Active", **extraDictData):
        self.name = name
        #A string containing the current operating info of the object.
        self.status = status
    
    #Does New Turn effects for the object
    def onNewTurn(self, newDate, gameDict):
        if (self.checkProcess("Building", newDate) or self.checkProcess("Re-enabling", newDate)): #If it was being built and has been completed, or has been  add the completion effects.
            data = self.getData(gameDict)
            return {"Effects": data["Completion Effects"], data["category"]: data["buildingCosts"]["size"]}
        return {}
    
    #Does New Year effects for the object
    def onNewYear(self, gameDict):
        if (self.isActive()):
            return {"Maintenance": self.getData(gameDict)["Maintenance Costs"], "Revenue": self.getData(gameDict)["Revenue"]}
        
        return {"Maintenance": {}, "Revenue": {}}
    
    #Changes the status to an ordered process
    def addProcess(self, processName, completionDate): #Example: g = GameObject("g").addProcess(self, "Building", {someDate})
        if (self.isActive()):
            self.status = f"{processName}:{str(completionDate)}"
        return self
    
    #Changes the status to a countdown timer
    def addCountdown(self, countdownName, numTurns):
        if (self.isActive()):
            self.status = f"{countdownName}:{numTurns} Turns"
        return self
    
    #Sees if the project has an ongoing process/countdown or is disabled
    def isActive(self):
        if ((self.status == "Disabled") or (self.status == "Foreclosed")):
            return False
        
        # the ':' symbol is used for process- and countdown-defining
        if (':' in self.status):
            return False
            
        return True
    
    #Checks the status for an ongoing process or countdown
    def checkProcess(self, processName, currentDate):
        if processName in self.status:
            
            #If it is a countdown (has "# Turns" in status)
            if ("Turns" in self.status):
                #Turns "Countdown:x Turns" into ("Countdown", "x")
                splitStatus = self.status.split()[0].split(':')
                
                #If 0 turns to go for countdown to end
                if (int(splitStatus[1]) == 0):
                    self.status = "Active"
                    return True #Countdown is done
                
                splitStatus[1] = int(splitStatus[1]) - 1
                self.status = f"{splitStatus[0]}:{splitStatus[1]} Turns"
                return False #Countdown is ongoing
        
            completionDate = Date.fromStr(self.status.split(':')[1]) #A process would look like: {process}:{month}/{year}, so this isolates {month}/{year}
            if (completionDate <= currentDate):
                self.status = "Active"
                return True
        return False #Either the process doesn't exist or is not complete
    
    #Disables the object for some time.
    def disable(self, saveGame, resource = None):
        self.status = "Disabled"
        if (resource):
            return self.getData(saveGame.getGameDict())["Maintenance Costs"][resource]
    
    #Sets the project to be re-enabled on the next turn
    def enable(self):
        self.addCountdown("Re-enabling", 1)
    
    def getData(self, gameDict):
        return gameDict["Game Objects"][f"{self.__class__.__name__}s"][self.name].copy()

#A buildable, stationary project
class Building(GameObject):
    def __init__(self, name, status, **extraDictData):
        GameObject.__init__(self, name, status)

#A building object specifically used for colonization
class ColonialBuilding(Building):
    def __init__(self, name, status, colonialProgressValue, **extraDictData):
        Building.__init__(self, name, status)
        self.colonialProgressValue = colonialProgressValue

#A group of units that can move around on the map and perform combat.
class UnitGroup(GameObject):
    territoryTypes = ()
    def __init__(self, name, nation, composition, territory, status = "Active", morale = 100):
        GameObject.__init__(self, name, status)
        self.nation = nation
        self.composition = composition
        self.territory = territory
        self.morale = 100
    
    #Puts the unit on a path of traversal towards the destination territory
    def moveTo(self, destination, saveGame):
        map = saveGame.getMap()
        path = map.traverse(self.territory, destination, self.__class__.territoryTypes, saveGame.traversableTerritories(self.nation))
        
        #If there is a path and the army is active:
        if (bool(path) & self.isActive()):
            pathStr = ""
            previousTerr = self.territory
            arrivalDate = saveGame.date
            #Goes through each territory in the path, meaning each territory on the path to the destination
            for currentTerr in str(path).split(">>"):
                if (currentTerr == previousTerr): continue
                
                pathStr += currentTerr + ";"
                #Gets a new date of arrival based on distance between current and previous territories (km) divided by the speed of the army and rounded up.
                arrivalDate = arrivalDate.newDate(math.ceil( map[previousTerr][currentTerr] / self.getSpeed()))
                pathStr += (str(arrivalDate))
                
                pathStr += ">>"
                
                previousTerr = currentTerr
            
            self.status = f"Moving:{pathStr}"
        else:
            print(f"MOVING \"{self.name}\" TO \"{destination}\" FAILED")
    
    #Check if this unitGroup is moving and then move forward if it is.
    def checkMoving(self, saveGame):
        newDate =  saveGame.date
        
        if ("Moving" in self.status):
            splitStatus = self.status.split(':')
            path = splitStatus[1].split(">>")[:-1]
            
            for waypoint in path.copy():
                date = Date.fromStr(waypoint.split(';')[1])
                if (newDate >= date):
                    path.remove(waypoint)
                    self.territory = waypoint.split(';')[0]
                    
                    #Gets all the unitGroups in this new territory, including this one
                    unitGroupsInTerritory = saveGame.unitGroupsInTerritory(waypoint)
                    
                    #If there is more than one nation with unitGroups in the territory (meaning not just this unitGroup's nation)
                    for nation in unitGroupsInTerritory:
                        if ("War" in saveGame.diplomaticRelations[self.nation].relations):
                            self.status = f"In Combat against {nation}"
                            print(f"COMBAT HAPPENING BETWEEN {self.nation} and {nation}")
                            break
                    
                else: break
            
            if (path):
                self.status = "Moving:"
                for waypoint in path:
                    self.status += waypoint + ">>"
            
            else: self.status = "Active"
    
    def merge(self, *mergeWith, saveGame):
        for otherGroup in mergeWith:
            for unit in otherGroup.composition.values():
                #If this unit matches an existing one in the composition, combine them
                if (unit.name in self.composition.keys()):
                    self.composition[unit.name] += unit
                #Otherwise, make a new unit for it
                else:
                    self.composition[unit.name] = unit
                    
    def split(self, *unitNames, nation, saveGame):
        splitComp = {}
        for unitName in unitNames:
            if (unitName in self.composition.keys()):
                splitComp[unitName] = self.composition.pop(unitName)
        
        groupBlueprint = {
            "__class__": self.__class___.__name__,
            "__module__": "ConcertOfNations.GameObjects",
            "name": saveGame[nation].getNewForceName(self.__class___.__name__),
            "composition": splitComp,
            "territory": territory
        }
        
        saveGame[nation].unitGroups[groupBlueprint["name"]] = FileHandling.loadObject(groupBlueprint)
    
    def getSize(self):
        size = 0
        
        for unit in self.composition.values():
            size += unit.size
            
        return size
    
    def rawSize(self):
        size = 0
        
        for unit in self.composition.values():
            size += unit.size
            
        return size
            
    def getSpeed(self):
        speed = None
        for unit in self.composition.values():
            speed = unit.speed or min(speed, unit.speed)
            
        return speed
    
    def onNewTurn(self, newTurnEffects, saveGame):
        newDate = saveGame.date
        
        self.checkMoving(saveGame)
        
        if(self.checkProcess("Building", newDate) or self.checkProcess("Remobilizing", newDate)):
            for unit in self.composition.values():
                unitData = unit.getData(saveGame.getGameDict())
                if (unitData["category"] in newTurnEffects): newTurnEffects[unitData["category"]] += unitData["buildingCosts"]["size"]
                
                else: newTurnEffects[unitData["category"]] = unitData["buildingCosts"]["size"]
            
        return newTurnEffects
    
    def onNewYear(self, gameDict, nationModifiers, territoryModifiers):
        
        #Checks if status is "Demobilized" or "Building"
        if not any(illegalStatus in self.status for illegalStatus in ("Demobilized", "Building")):
        
            rtnDict = {"Maintenance": {}}
            
            for unit in self.composition.values():
                rtnDict["Maintenance"] = Util.combineDicts(rtnDict["Maintenance"], unit.getData(gameDict)["Maintenance Costs"])
                
                #Apply modifiers
                for modifiers in (nationModifiers, territoryModifiers):
                    if (self.__class__.__name__ in modifiers):
                        for item in rtnDict["Maintenance"].keys():
                            rtnDict["Maintenance"][item] *= modifiers[self.__class__.__name__]["Exponential"]["Maintenance"]
                        
        #Raise the morale of the army bit by bit to a maximum of one hundred
        self.morale = min(100, self.morale+25)
        
        return rtnDict
        
    def getData(self, gameDict):
        rtnDict = {}
        
        for division in self.composition.keys():
            rtnDict[division] = self.composition[division].getData(gameDict)
        
        return rtnDict
    
    def disable(self, saveGame, resource = None):
        self.status = "Disabled"
        totalCost = 0
        if (resource):
            for unit in self.composition.values():
                totalCost += unit.getData(saveGame.getGameDict())["Maintenance Costs"][resource]
        return totalCost

    def enable(self):
        self.addCountdown("Remobilizing", 1)

    def demobilize(self, saveGame, nation):
        self.status = "Demobilized"
        self.morale = 0
        self.onDelete(saveGame, nation)
            
    def disableUnit(self, unitName, saveGame, nationName, resource = None):
        rtnDict = {}
        rtnDict["Cost"] = 0
        #If only one unit in this group:
        if (len(self.composition.keys()) == 1):
            self.onDelete(saveGame, nation)
            return {"Cost": self.disable(saveGame, resource)}
        
        else: #Split off one unit from this one.
            rtnDict["Disabled Unit"] = self.composition.pop(unitName)
            rtnDict["Disabled Unit"].status = "Disabled"
            rtnDict["Disabled Unit"].onDelete(saveGame, nationName)
            
        return rtnDict
    
    def regainManpower(self, saveGame, nation):
        for unit in self.composition.values():
            saveGame[nation].territories[unit.homeTerritory].recruitForUnitGroup(unit.manpower(saveGame.gameDict))
    
    def onDelete(self, saveGame, nation):
        for unit in self.composition.values():
            saveGame[nation].territories[unit.homeTerritory].getDemobilizedSoldiers(unit, unit.manpower(saveGame.getGameDict()))
    
    def isActive(self):
        return ((self.status != "Demobilized") and (GameObject.isActive(self)))
        
#A group of soldiers, cavalry and/or artillery
class Army(UnitGroup):
    territoryTypes = ("LandTerritory")
    def __init__(self, name, nation, composition, territory, status = "Active", morale = 100, **extraDictData):
        UnitGroup.__init__(self, name, nation, composition, territory, status, morale)
        self.size = self.getSize()
    
    #Different from UnitGroup.getSize, since it factors in division weights.
    def getSize(self):
        size = 0
        
        for division in self.composition.values():
            size += division.size * division.weight
            
        return size

#A group of ships and possibly other embarked unitgroups
class Fleet(UnitGroup):
    territoryTypes = ("SeaTerritory")
    def __init__(self, name, nation, composition, territory, status = "Active", morale = 100, embarked = None):
        UnitGroup.__init__(self, name, nation, composition, territory, status, morale)
        self.embarked = embarked or {}
    
    def onNewYear(self, gameDict, nationModifiers, territoryModifiers):
        newYearEffects = UnitGroup.onNewYear(self, gameDict, nationModifiers, territoryModifiers)
        
        for unitGroup in self.embarked.values():
            newYearEffects = Util.combineDicts(newYearEffects, unitGroup.onNewYear(gameDict, nationModifiers, territoryModifiers))
            
        return newYearEffects
    
    #Brings an army aboard onto the fleet, stored in self.embarked.
    def embark(self, embarkingUnitGroup, saveGame):
        if (embarkingUnitGroup.__class__ == Fleet):
            print("Cannot embark fleet onto fleet")
            return embarkingUnitGroup
        
        #Checks if this ship can transport a unitGroup of that size, and they are in the same territory.
        if ((self.transportCapacity(saveGame) >= embarkingUnitGroup.getSize()) and (self.territory == embarkingUnitGroup.territory)):
            
            self.embarked[embarkingUnitGroup.name] = embarkingUnitGroup
            embarkingUnitGroup.status = f"Embarked on {self.name}"
            
        else: return embarkingUnitGroup
    
    #Puts an army down in the territory the fleet is in or a bordering territory
    def disembark(self, unitGroupName, territoryName, saveGame):
        #CHECK IF NATION HAS MILITARY ACCESS
        nationName = saveGame.getTerritoryOwner(territoryName)
        
        map = saveGame.getMap()
        unitGroup = self.embarked.pop(unitGroupName)
        
        #canReachProvince is True if the fleet is in the target territory already or borders it
        canReachProvince = (self.territory == territoryName) or (territoryName in map[self.territory].edges)
        #goodProvinceType is True if the target territory has one of the required territory types of the embarked unitGroup.
        goodProvinceType = (map[territoryName].details["type"] in unitGroup.__class__.territoryTypes)
        
        if(nationName and canReachProvince and goodProvinceType and self.isActive() and ("Moving" not in self.status)):
            unitGroup.status = "Active"
            unitGroup.territory = territoryName
            saveGame[nationName].unitGroups[unitGroupName] = unitGroup
            
        else: self.embarked[unitGroupName] = unitGroup
        
    #Gets the maximum number of people that can be transported by this fleet, minus the size of the armies already embarked.
    def transportCapacity(self, saveGame):
        gameDict = saveGame.getGameDict()
        transportCapacity = 0
        
        for ship in self.composition.values():
            transportCapacity += ship.getData(gameDict)["transportCapacity"] * ship.size
            
        return (transportCapacity * 1000)

    #Sorts each of the subfleets
    def sortFleet(self):
        for subfleet in self.composition.keys():
            self.composition[subfleet].unitList = Util.sortBackwards(self.composition[subfleet].unitList)

#A group of specialists and/or colonists, can attach divisions for security.
class Expedition(UnitGroup):
    territoryTypes = ("LandTerritory")
    def __init__ (self, name, nation, composition, territory, status = "Active", supplies = None):
        UnitGroup.__init__(self, name, nation, composition, territory, status)
        self.supplies = supplies or {"Food": 0}
    
    def onNewTurn(self, newTurnEffects, saveGame):
        self.checkMoving(saveGame)
        return {}
        
    def onNewYear(self, gameDict, nationModifiers, territoryModifiers):
        return {}
    
#An object which represents one division of a unit group. These are the individual parts of a unit group that make the whole.
class Unit(GameObject):
    subclasses = ("Division", "Ship", "Colonist", "SpecialistTeam")
    def __init__(self, name, unitType, size, speed, homeTerritory, status = "Active", **extraDictData):
        GameObject.__init__(self, name, status)
        #unitType is the type of this unit class that this instance is. For example, a Ship of the Line would have the class "Ship" and the unitType "Ship of the Line".
        self.unitType = unitType
        #the size of this unit. Self-explanatory
        self.size = size
        #the speed of the unit in kilometers per month.
        self.speed = speed
        #where the Unit comes from and where it returns to if disbanded.
        self.homeTerritory = homeTerritory
    
    def getData(self, gameDict):
        data = GameObject.getData(self, gameDict)
        
        for resource in data["Maintenance Costs"]:
            data["Maintenance Costs"][resource]*= self.size
            
        return data
    
    def manpower(self, gameDict):
        return self.size
    
    #Divides the unit into multiple different units, returns a tuple of all of them.
    def divide(self, *sizes):
        pass

#A Unit whose composition is made up of lists rather than size numbers.
class UnitList(Unit):
    def manpower(self, gameDict):
        return int(self.getData(gameDict)["buildingCosts"]["manpowerCost"] * sum(self.unitList) / (self.size*100))

#A unit that is specifically part of an Army.    
class Division(Unit):
    def __init__(self, name, unitType, size, weight, attack, defense, speed, homeTerritory, status = "Active", **extraDictData):
        Unit.__init__(self, name, unitType, size, speed, homeTerritory, status)
        #weight is the multiplier that size is multiplied by to get how much space the unit takes up.
        self.weight = weight
        self.attack = attack
        self.defense = defense

#A unit that is specifically part of a fleet, and which has a list of the healths of the ships.    
class Ship(UnitList):
    def __init__(self, name, unitList, speed, homeTerritory, status = "Active", **extraDictData):
        self.name = name
        self.unitList = unitList
        self.size = len(self.unitList)
        self.speed = speed
        self.homeTerritory = homeTerritory
        self.status = status
        
    def getData(self, gameDict):
        data = GameObject.getData(self, gameDict)
        
        for resource in data["Maintenance Costs"]:
            data["Maintenance Costs"][resource]*= len(self.unitList)
            
        return data
    
    #Divides the unit into multiple different units, returns a tuple of all of them.
    def divide(self, *sizes):
        pass

#A unit that is part of any Unit Group but makes up expeditions specifically, representing NCO or officer professional individuals.
class SpecialistTeam(Unit):
    def __init__(self, name, unitType, size, speed, homeTerritory, status = "Active", **extraDictData):
        Unit.__init__(self, name, unitType, size, speed, homeTerritory, status)
        
    def onNewTurn():
        pass
        
    def onNewYear():
        pass
        
    def getData():
        return {}

#A unit made up of demographics which is a core unit of an Expedition and can settle territories.
class Colonist(Unit):
    def __init__(self, name, size, speed, allegiance, demographicComposition, status = "Active", **extraDictData):
        self.name = name
        self.size = size
        self.speed = 500 #km/month
        self.allegiance = allegiance
        self.demographicComposition = demographicComposition
        self.status = status
    
    def settle(self, territory, saveGame):
        pass
        
    def getData(self, gameDict):
        return {"Demographic Composition": self.demographicComposition, "Supply Requirements": {"Food": int(self.size/100)}}

#A Location on the game map. If stored in the savegame, it can be assumed that the territory is in fact ownable by a nation.
class Territory(GameObject):
    def __init__(self, name, type, projects = None, supplyRoutes = None, modifiers = None, status = "Local Focus", **extraDictData):
        GameObject.__init__(self, name, status) #Passive Territory statuses can be "Occupied", "Local Focus", "National Focus", "Scorched"
        self.type = type #Type of territory: e.g. Land, Coastal, Maritime
        self.projects = projects or {}
        self.supplyRoutes = []
        self.modifiers = modifiers or globalModifiers["Territory"].copy()
    
    def onNewTurn(self, newDate, gameDict):
        newTurnEffects = {"Effects": {"Nation": {}, "Territory": {}}}
        for project in self.projects.values():
            newTurnEffects = Util.combineDicts(newTurnEffects, project.onNewTurn(newDate, gameDict))
        return self.applyEffects(newTurnEffects)
    
    def onNewYear(self, newDate, nationalModifiers, gameDict, map):
        
        newYearEffects = {"Maintenance": {}, "Revenue": {"Money": 0}}
        
        for project in self.projects.keys():
            newYearEffects = Util.combineDicts(newYearEffects, self.projects[project].onNewYear(gameDict))
            
        for resource in newYearEffects["Revenue"]:
            
            #If the resource produced by the projects is a mineable resource, the resource income should equal the amount in the territory.
            if ((resource in self.getData(map).details["resources"].keys()) and (resource in gameDict["Basic Resources"])): 
            
                newYearEffects["Revenue"][resource] = self.getData(map).details["resources"][resource] * self.modifiers["Territorial"]["Exponential"]["Resource Output"]
            
            #If it is money, then just multiply by modifier. 
            elif (resource == "Money"): newYearEffects["Revenue"]["Money"] *= self.modifiers["Territorial"]["Exponential"]["Revenue"]
            
            #If it is a manufactured resource, just do nothing.
            elif (resource in gameDict["Manufactured Resources"]): 
                continue
                
            #If none, it = 0.
            else: newYearEffects["Revenue"][resource] = 0
            
        return newYearEffects
    
    #Gets the revenue in money of this territory
    def revenue(self, gameDict):
        revenue = 0
        for project in self.projects.values():
            
            if (project.isActive()):
                data = project.getData(gameDict)
                if ("Money" in data["Revenue"]):
                    revenue += data["Revenue"]["Money"]
            
        return revenue
    
    #Gets all the resources this territory produces
    def resourceRevenue (self, gameDict):
        revenues = {"Money": 0}
        for project in self.projects.values():
            
            if (project.isActive()):
                revenues = Util.combineDicts(revenues, project.getData(gameDict)["Revenue"])
            
        return revenues
        
    #Applies territorial project effects, then returns effects dict without the applied effects
    def applyEffects(self, effects, mode = "ADD"):
        if (mode == "ADD"):
            self.modifiers = Util.combineDicts(self.modifiers, effects["Effects"].pop("Territory"))
            return effects
        
        elif (mode == "REMOVE"):
            
            #effects[effectType] may represent a case, for example, where effects is overallEffects["Nation"] and effectType is "National"
            for effectType in effects:
            
                for modifier in effects[effectType]["Cumulative"]:
                    self.modifiers[effectType]["Cumulative"][modifier] -= effects[effectType]["Cumulative"][modifier]
                    
                for modifier in effects[effectType]["Exponential"]:
                    self.modifiers[effectType]["Exponential"][modifier] -= effects[effectType]["Exponential"][modifier]
    
    #Checks if a project can be built here
    def canBuild(self, blueprint, saveGame):
        if blueprint["__class__"] in Unit.subclasses: #If it is a subclass of Unit, check if the territory's population can be recruited to build it.
            #Check if this is a habitable territory, and if so if the population can be recruited to build this Unit.
            if (self.__class__ == HabitableTerritory):
                enoughManpower = (blueprint["unitManpowerSize"] <= self.recruitablePopulation())
                doesntHaveProject = True
            else: return False
            
        else: 
            enoughManpower = True
            doesntHaveProject = not(blueprint["name"] in self.projects)
        
        terrData = self.getDictData(saveGame.getMap())
        
        #If there is a "Coastal" key in the territory requirements:
        if ("Coastal" in blueprint["territoryRequirements"]):
            #If it is coastal, matchesType = True
            if (blueprint["territoryRequirements"]["Coastal"] & terrData["details"]["Coastal"]):
                matchesType = True
                
        elif (blueprint["__class__"] == "ColonialBuilding"):
            matchesType = (self.__class__ == ColonialTerritory)
        
        else: 
            matchesType = (self.type == blueprint["territoryRequirements"]["type"])
        
        return (enoughManpower and matchesType and doesntHaveProject)
    
    #Get the total population of the territory
    def population(self):
        population = 0
        for demographic in self.demographics.values():
            population += demographic.populationData[0]
        return population
    
    #Adds project to local project dictionary
    def buildProject(self, blueprint, currentDate):
        blueprint["status"] = ("Building:" + str(currentDate.newDate(blueprint["buildTime"]))) #status is something like: "Building:{month}/{date}"
        self.projects[blueprint["name"]] = FileHandling.loadObject(blueprint)
    
    #Forecloses a project - meaning it deletes the object and then adds a temporary unrest modifier.
    def foreclose(self, projectName, saveGame):
        gameDict = saveGame.getGameDict()
        foreclosedProject = self.projects.pop(projectName)
        
        foreclosureInfo = foreclosedProject.getData(gameDict)["Completion Effects"]
        foreclosureInfo["Money from Foreclosure"] = foreclosedProject.getData(gameDict)["buildingCosts"]["resourceCosts"]["Money"]
        return foreclosureInfo
    
    #Creates territory object from a dictionary
    def fromDict(territoryDict):
        territoryDict = territoryDict.copy()
    
        territoryDict["__class__"] = "Territory"
        territoryDict["__module__"] = "ConcertOfNations.GameObjects"
        
        territoryDict = Util.combineDicts(territoryDict.pop("details"), territoryDict)
        
        return FileHandling.loadObject(territoryDict)
    
    def getData(self, map):
        return map[self.name]
    
    def getDictData(self, map):
        return FileHandling.saveObject(map[self.name])
    
    #Gets the effects of having a territory on the nation that owns it
    def retrieveEffects(self, saveGame):
        rtnDict = {}
        gameDict = saveGame.getGameDict()
        
        for project in self.projects.values():
            if (project.isActive()):
                rtnDict = Util.combineDicts(rtnDict, project.getData(gameDict)["Completion Effects"])
        return rtnDict
        
#A territory that has demographics in it. Thus, it is not only movable through and buildable in, but taxable
class HabitableTerritory(Territory):
    def __init__(self, name, type, projects = None, demographics = None, supplyRoutes = None, modifiers = None, status = "Local Focus", **extraDictData):
        Territory.__init__(self, name, type, projects, supplyRoutes, modifiers or globalModifiers["HabitableTerritory"].copy(), status, **extraDictData)
        self.demographics = demographics or {}
        
    def onNewYear(self, newDate, nationalModifiers, gameDict, map):
        
        newYearEffects = {"Maintenance": {}, "Revenue": {"Money": 0}}
        
        for project in self.projects.keys():
            newYearEffects = Util.combineDicts(newYearEffects, self.projects[project].onNewYear(gameDict))
        
        for demographic in self.demographics.keys():
            newYearEffects["Revenue"]["Money"] += self.demographics[demographic].onNewYear(self.modifiers, nationalModifiers)
            
        for resource in newYearEffects["Revenue"]:
            
            #If the resource produced by the projects is a mineable resource, the resource income should equal the amount in the territory.
            if ((resource in self.getData(map).details["resources"].keys()) and (resource in gameDict["Basic Resources"])): 
            
                newYearEffects["Revenue"][resource] = self.getData(map).details["resources"][resource] * self.modifiers["Territorial"]["Exponential"]["Resource Output"]
            
            #If it is money, then just multiply by modifier. 
            elif (resource == "Money"): newYearEffects["Revenue"]["Money"] *= self.modifiers["Territorial"]["Exponential"]["Revenue"]
            
            #If it is a manufactured resource, just do nothing.
            elif (resource in gameDict["Manufactured Resources"]): 
                continue
                
            #If none, it = 0.
            else: newYearEffects["Revenue"][resource] = 0
            
        return newYearEffects
        
    #Subtracts the number of people recruited into a unitGroup from the population
    def recruitForUnitGroup(self, unitManpowerSize):
        for demographic in self.demographics.keys():
            #armyShareRatio is how much of the army is made up of the demographic, calculated as its recruitable population out of the total recruitable population.
            armyShareRatio = self.demographics[demographic].getRecruitablePopulation() / self.recruitablePopulation()
            #Reduces each demographic by a proportional amount to account for unitGroup recruitment
            self.demographics[demographic].recruitPops(unitManpowerSize * armyShareRatio)
    
    #Gets willing colonists from each of the local demographics
    def recruitColonists(self, numColonists, saveGame):
        recruitableTotalPop = self.recruitableForColonization()
        #If that many colonists can be recruited.
        if (numColonists <= recruitableTotalPop):
            demographicComposition = {}
            #Get the number of recruitable colonists from each demographic and add it to the demographic composition
            for demographic in self.demographics.values():
                colonistShareRatio = ((demographic.populationData[0] * (1 - demographic.unrestData[0])) / recruitableTotalPop)
                demographicComposition[demographic.name] = demographic.recruitColonists(numColonists * colonistShareRatio)
            
            return demographicComposition
        #If that many colonists cannot be recruited
        return False
    
    #Amount of the population that can be recruited for colonization
    def recruitableForColonization(self):
        population = 0
        for demographic in self.demographics.values():
            population += (demographic.populationData[0] * (1 - demographic.unrestData[0]))
        return population
    
    #Adds demobilized soldiers back to the territory as population
    def getDemobilizedSoldiers(self, unit, manpowerStrength):
        population = 0
        demographicPops = {}
        #Gets the sizes of each demographic and also calculates the overall population
        for demographic in self.demographics.values():
            thisPop = demographic.populationData[0]
            population += thisPop
            demographicPops[demographic.name] = thisPop
            
        for demographic in demographicPops:
            self.demographics[demographic].populationData[0] += int(manpowerStrength / (demographicPops[demographic]/population))
    
    #Gets the total recruitable population of the territory.
    def recruitablePopulation(self):
        population = 0
        for demographic in self.demographics.values():
            #Recruitable population adds the size of each demographic group, which is either multiplied by 1 - that group's unrest level if its above 0.25, or by 1.
            population += demographic.getRecruitablePopulation()
        return population
    
    #Gets revenue, including from demographics
    def revenue(self, gameDict):
        revenue = Territory.revenue(self, gameDict)
        for demographic in self.demographics.values():
            revenue += demographic.revenue()
        return revenue
    
    def resourceRevenue(self, gameDict):
        revenues = Territory.resourceRevenue(self, gameDict)
        
        for demographic in self.demographics.values():
            revenues["Money"] += demographic.revenue()
            
        return revenues
    
    #Forecloses a project - meaning it deletes the object and then adds a temporary unrest modifier.
    def foreclose(self, projectName, saveGame):
        gameDict = saveGame.getGameDict()
        foreclosedProject = self.projects.pop(projectName)
        
        #Adds a temporary raise to unrest from the foreclosure, equal to the total project space taken up by the foreclosed project.
        self.modifiers["Demographic"]["Temporary"][f"Unrest:Foreclosing {projectName}:{saveGame.date.newDate(12)}"] = foreclosedProject.getData(saveGame.getGameDict())["buildingCosts"]["size"]
        
        foreclosureInfo = foreclosedProject.getData(gameDict)["Completion Effects"]
        foreclosureInfo["Money from Foreclosure"] = foreclosedProject.getData(gameDict)["buildingCosts"]["resourceCosts"]["Money"]
        return foreclosureInfo
        
    #Creates territory object from a dictionary
    def fromDict(territoryDict):
        territoryDict = territoryDict.copy()
    
        territoryDict["__class__"] = "HabitableTerritory"
        territoryDict["__module__"] = "ConcertOfNations.GameObjects"
        
        territoryDict = Util.combineDicts(territoryDict.pop("details"), territoryDict)
        
        return FileHandling.loadObject(territoryDict)
    
    def fromColonialTerritory(colonialTerritory):
        return Territory(colonialTerritory.name, "TEST")

#A territory that is currently being colonized by a nation.
class ColonialTerritory(HabitableTerritory):
    def __init__(self, name, type, projects = None, demographics = None, supplyRoutes = None, modifiers = None, colonialProgress = None, status = "Colonizing", **extraDictData):
        HabitableTerritory.__init__(self, name, type, projects, demographics, supplyRoutes, modifiers, status)
        self.colonialProgress = colonialProgress or [0, 100]
    
    def onNewYear(self, newDate, nationalModifiers, gameDict, map):
        
        newYearEffects = {"Maintenance": {"Money": self.maintenance(gameDict)}, "Revenue": {"Money": 0}}
        
        for project in self.projects.values():
            self.colonialProgress[0] += project.colonialProgressValue
            
        return newYearEffects
    
    #Gets the maintenance in money of this territory
    def maintenance(self, gameDict):
        maintenance = 0
        for project in self.projects.values():
            
            if (project.isActive()):
                data = project.getData(gameDict)
                if ("Money" in data["Maintenance Costs"]):
                    maintenance -= data["Maintenance Costs"]["Money"]
            
        for demographic in self.demographics.values():
            maintenance += demographic.populationData[0]
            
        return maintenance
    
    #Turns this colony into a regular HabitableTerritory.
    def completeColonization(self):
        pass
    
    #Creates territory object from a dictionary
    def fromDict(territoryDict):
        territoryDict = territoryDict.copy()
    
        territoryDict["__class__"] = "ColonialTerritory"
        territoryDict["__module__"] = "ConcertOfNations.GameObjects"
        
        territoryDict = Util.combineDicts(territoryDict.pop("details"), territoryDict)
        
        return FileHandling.loadObject(territoryDict)

#A territory that is under the legal control of another nation but within the military presence of another. COMMENTED BECAUSE OF POSSIBLE INHERITANCE PROBLEMS
#class OccupiedTerritory(Territory):
    #pass
        
#A Demographic group of people
class Demographic:
    baseRecruitmentRate = 0.25
    def __init__(self, name, populationData, unrestData, recruitableRate = None):
        #Name is a string of the format {Social Class} {Religion} {Ethnicity}.
        self.name = name
        #PopulationData is a list [0, 1] where populationData[0] is the demographic population and populationData[1] is the population growth rate.
        self.populationData = populationData
        #UnrestData is a list [0, 1] where unrestData[0] is the demographic unrest and unrestData[1] is the unrest growth rate.
        self.unrestData = unrestData
        #recruitableRate is the percentage of the population that's recruitable.
        self.recruitableRate = recruitableRate or Demographic.baseRecruitmentRate
    
    def __add__(self, other):
        if (self.name == other.name):
            return Demographic(self.name, popData, unrestData, recRate)
        raise ValueError(f"Could not add: Demographics \"{self.name}\" and \"{other.name}\" are different")
    
    def recruitPops(self, amountToRecruit):
        self.recruitableRate = max(0, Util.isSufficient(self.unrestData[0], self.recruitableRate, 1 - self.unrestData[0]) - (amountToRecruit/self.populationData[0]))
        self.populationData[0] -= amountToRecruit
    
    def recruitColonists(self, numColonists):
        self.populationData[0] -= numColonists
        return Demographic(self.name, [numColonists, self.populationData[1]], self.unrestData, self.recruitableRate)
    
    #Gets the amount of the population that can be recruited for war.
    def getRecruitablePopulation(self):
        return self.populationData[0] * Util.isSufficient(self.unrestData[0], self.recruitableRate, 1 - self.unrestData[0])
    
    #Returns the population's revenue
    def revenue(self):
        return (self.populationData[0] * Util.isSufficient(self.unrestData[0], 1, 1-self.unrestData[0]) * 0.1) * 0.25
        
    #Grows the population and unrest, and returns the yearly revenue.
    def onNewYear(self, territoryModifiers, nationalModifiers):
        #Pop size after applying modifiers
        newPopulation = int(self.populationData[0] * (1 + self.populationData[1]))  * nationalModifiers["Demographic"]["Exponential"]["Growth"] * territoryModifiers["Demographic"]["Exponential"]["Growth"]
        
        if (self.recruitableRate < Demographic.baseRecruitmentRate): 
            self.recruitableRate = min(Demographic.baseRecruitmentRate, self.recruitableRate + ((newPopulation -  self.populationData[0]) * Demographic.baseRecruitmentRate)/newPopulation)
        
        self.populationData[0] = newPopulation #Grows population
        
        tempUnrest = 0
        for modifiers in (territoryModifiers["Demographic"]["Temporary"], nationalModifiers["Demographic"]["Temporary"]):
            for modifier in modifiers.keys():
                if (modifier.split(':')[0] == "Unrest"):
                    tempUnrest += modifiers[modifier]
                    
        self.unrestData[0] += (self.unrestData[1] + tempUnrest) * nationalModifiers["Demographic"]["Exponential"]["Unrest"] * territoryModifiers["Demographic"]["Exponential"]["Unrest"]#Grows unrest
        self.unrestData[0] = max(min(self.unrestData[0], 100), 0) #Ensures unrest is at least 0 and at most 100
        
        return self.revenue() * nationalModifiers["Demographic"]["Exponential"]["Tax Modifier"] * territoryModifiers["Demographic"]["Exponential"]["Tax Modifier"]
#Bottom







































#Bottom 2 electric boogaloo