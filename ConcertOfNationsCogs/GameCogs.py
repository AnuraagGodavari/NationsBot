import discord
from discord.ext import commands
import json, os, pprint, traceback, datetime
from enum import Enum, IntEnum
from GameCommands import *
from ConcertOfNations import *

print("GameCogs.py GAME MASTER AND NATION COGS FOR CONCERT OF NATIONS BOT\n*****\n")

#REMINDERS:
print("-----\nREMINDERS:\n")
print("Make pages able to evaluate functions (use eval()?)!\n")
print("Check out modifiers['Nation']['National'] and the like!")
print("Do gameDict command for NationCog")
print("-----\n")

#A cache of saveGames being played.
saveGames = {}
#A cache of player statuses, i.e. what commands/menus they are on. Includes: Game they're logged into ("Game ID"), Decision Linked List ("Stack", including either current command names or pages)
playerStatuses = {}

class GameException(Exception): pass

with open("Data/NationsBotData.json") as f:
    gamesData = json.load(f)
     
#Gets a saveGame by ctx attributes
def getGame(ctx):
    #Loads a saveGame by ID
    def loadGame(gameID):
        #Go through all the files in the "Savegames" folder in this directory until a valid saveGame is found.
        for filename in os.listdir("./Savegames"):
            if (filename[:-5].split(" - ")[-1] == gameID):
                with open(f"Savegames/{filename}") as f:
                    saveGame = FileHandling.loadObject(json.load(f))
                    saveGames[gameID] = saveGame
                    return saveGame
    
    player = str(ctx.author.id)
    
    #Try to load by server first
    if (ctx.guild):
        if (str(ctx.guild.id) in gamesData["Servers"]):
            gameID = gamesData["Servers"][str(ctx.guild.id)]["Game ID"]
        
    elif (str(ctx.author.id) in gamesData["Players"]):
        playerData = gamesData["Players"][player]
        #If the player is only in one game
        if (player in playerStatuses): gameID = playerStatuses[player]
        
        elif (len(playerData["Server IDs"]) == 1): 
            gameID = playerData["Server IDs"][0]
            
        else: raise GameException(f"PLAYER <{player}> NOT LOGGED INTO ANY GAME")
    
    else: raise GameException(f"PLAYER <{player}> NOT A PART OF ANY GAME")
    
    if (player not in playerStatuses):
        playerStatuses[player] = {}
    playerStatuses[player]["Game ID"] = gameID
        
    if (gameID in saveGames): return saveGames[gameID]
    else: return loadGame(gameID)

#Gets a nation object from a saveGame.
def getNation(ctx, saveGame):
    return saveGame.players[str(ctx.author.id)]

#Gets a game's info, including the saveGame and specified nation's name, and saves it to a dictionary
def getGameInfo(ctx):
    rtnDict = {}
    rtnDict["Savegame"] = getGame(ctx)
    rtnDict["Nation Name"] = getNation(ctx, rtnDict["Savegame"])
    return rtnDict

def getColor(gameInfo):
    return discord.Color.from_rgb(153, 0, 0)

#Makes an embed page
def makePages(listToPage, embedTitle, embedDesc, fieldNameList, fieldValueList):
    
    #fieldNameList and fieldValueList are lists of the string names of parameters that need to be included in field names and values, respectively
    #if fieldNameList is: ["name", "|", "status" "," "territory"]
    #then the field's name will be f"{thingDict[name]} | {thingDict[status]} , {thingDict[territory]}"
    def strFromList(list, obj):
        #Save the object to a dict for easy reading
        objDict = FileHandling.saveObject(obj)
        rtnStr = ''
        
        #These bools control if either the first or all labels (object attributes) are omitted from the page display.
        omitAllLabels = (list[0] == "OMIT_ALL_LABELS")
        omitFirstLabel = (list[0] == "OMIT_FIRST_LABEL")
        
        if (omitAllLabels or omitFirstLabel):
            list = list[1:]
        
        for thing in list:
            if (thing in objDict.keys()):
                if (omitFirstLabel or omitAllLabels): 
                    rtnStr += str(objDict[thing]) + " "
                    omitFirstLabel = False
                
                #Add capitalized label plus the value
                else: rtnStr += thing[0].upper() + thing[1:] + ": " + str(objDict[thing]) + " "
                
            else:
                rtnStr += thing + ' '
        
        return rtnStr
    
    pages, pageNo = [], 0
    pagedList = Util.pageify(listToPage, 10)
    
    for page in pagedList:
            
        newEmbed = discord.Embed(
                title = f"{embedTitle} || Page {pageNo}/{len(pagedList) - 1}",
                description = f"{embedDesc}\n_Type 'n.page <pageNo>' to go to a specific page._",
                color = discord.Color.from_rgb(153, 0, 0)
            )
            
        for obj in page:
            fieldNameList = ["OMIT_FIRST_LABEL"]*(fieldNameList[0] not in ("OMIT_FIRST_LABEL", "OMIT_ALL_LABELS")) + fieldNameList
            
            nameStr = strFromList(fieldNameList, obj)
            valueStr = strFromList(fieldValueList, obj)
            
            newEmbed.add_field(name = nameStr, value = valueStr, inline = False)
        
        pages.append(newEmbed)
        pageNo += 1
    
    return pages

#The cog that contains game master commands and events
class GameMasterCog(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    #Cog Event
    @commands.Cog.listener()
    async def on_ready(self):
        print("Loaded GameMasterCog.py")
    
    #Test Command
    @commands.command()
    async def gameMasterCogTest(self, ctx):
        nation = getNation(ctx)
        print(nation)
        await ctx.send(f"gameMasterCogTest: {saveGames}")

#The cog that contains nation commands and events
class NationsCog(commands.Cog):

    class Flags(IntEnum):
    
        ARGS = 0
        
        ANY = 1
        ALL = 2
        
        INT = 3
        LIST = 4

    def __init__(self, client):
        self.client = client
    
    #Take a list of input args and assigns values to requested variables based on a varDict that specifes the conditions for the args to be validated
    #noneAllowed is a bool where, if true, variables may have a value of none
    def validateArgs(self, args, varDict, noneAllowed = False):
        
        #Create an empty dict with the keys in varDict to assign values to
        rtnDict = {key: None for key in varDict.keys()}
        
        #flag to stop the arg-interpreting loop
        stopFlag = False
        
        #String of one or more mini-args to create one full arg
        argString = ""
        
        #If the LIST flag is a key in rtnDict, replace it with the variables needed for the list.
        if (int(self.Flags.LIST) in varDict):
            listVars = varDict.pop(int(self.Flags.LIST))
            rtnDict.pop(int(self.Flags.LIST))
            
            for var in listVars:
                varDict[var] = listVars[var]
                rtnDict[var] = list()
        
        for index in range(len(args)):
         
            if (stopFlag): break
            
            arg = args[index]
            
            if (argString != ""): argString += " "
            argString += arg
            
            for var in rtnDict.keys():
                #If the var isn't set
                if (rtnDict[var] == None):
                
                    #If the var is a number and the argString is a string of digits:
                    if (varDict[var] == self.Flags.INT):
                        if (argString.isdigit()):
                            rtnDict[var] = int(argString)
                            argString = ""
                            break
                    
                    #If the varDict value for this var key is a non-string iterable
                    elif (hasattr(varDict[var], '__iter__') and not isinstance(varDict[var], str)): 
                        if (argString in varDict[var]):
                            rtnDict[var] = argString
                            argString = ""
                            break
                    
                    #If the last args are to be combined as one
                    elif (varDict[var] == self.Flags.ALL):
                        unfilledVars = [ var for var in rtnDict.keys() if rtnDict[var] == None]
                        
                        #If all other vars are filled, and if the argString fits
                        if (unfilledVars == []):
                            rtnDict[var] = argString + " " + ' '.join(args[index + 1:])
                            stopFlag = True
                            break
                        
                #If this var is an empty list
                elif(rtnDict[var] == []):
                    
                    unfilledVars = [ var for var in rtnDict.keys() if rtnDict[var] == None]
                    #If all other vars are filled
                    if (unfilledVars == []):
                        
                        #If the object is a non-string iterable, check using "in"
                        if (hasattr(varDict[var], '__iter__') and not isinstance(varDict[var], str)):
                            
                            if (argString in varDict[var]):
                                
                                rtnDict[var].append(argString)
                                argString = ""
                                
                        elif (varDict[var] == self.Flags.ANY):
                            rtnDict[var].append(argString)
                            argString = ""
                        
        #If None isn't allowed for a variable value
        if (not noneAllowed):
            noneVars = []
        
            for var in rtnDict:
                if rtnDict[var] == None:
                    noneVars.append(var)
                    
            if (noneVars): raise GameException(f"VARIABLES <{str(noneVars)}> NOT ASSIGNED PROPERLY\n{json.dumps(rtnDict, indent = 4)}")
                            
        return rtnDict
    
    #Validate only one arg
    def validateArg(self, args, varDict):
    
        rtnDict = {key: None for key in varDict.keys()}
        
        argString = ""
        
        for index in range(len(args)):
            
            arg = args[index]
            
            if (argString != ""): argString += " "
            argString += arg

            for var in rtnDict.keys():
                #If the var isn't set
                if (rtnDict[var] == None):
                    #If the var is a number and the argString is a string of digits:
                    if (varDict[var] == self.Flags.INT):
                        if (argString.isdigit()):
                            rtnDict[var] = int(argString)
                            argString = ""
                    
                    #If the varDict value for the var is a dict or list
                    else: 
                        if (argString in varDict[var]):
                        
                            rtnDict[var] = varDict[var].get(argString)
                            
                            if (index + 1 < len(args)):
                                rtnDict[int(self.Flags.ARGS)] = args[index + 1:]
                            
                            return rtnDict
        
        #Check if the var is none
        noneVars = []
        
        for var in rtnDict:
            if rtnDict[var] == None:
                noneVars.append(var)
                
        if (noneVars): raise GameException(f"VARIABLE <{str(noneVars)}> NOT ASSIGNED PROPERLY\n{json.dumps(rtnDict, indent = 4)}")
        
        #Continue as normal if the var is filled
        rtnDict[int(self.Flags.ARGS)] = args
        return rtnDict
       
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        errorTime = str(datetime.datetime.now())
        
        pprint.pprint(traceback.format_exception(type(error), error, error.__traceback__))
        
        if (ctx.guild):
            serverID = ctx.guild.id
        else:
            serverID = None
        
        errorData = {
            "ctx": {
                "Author ID": ctx.author.id,
                "Server ID": serverID
            },
            "Error Time": errorTime,
            "Exception": str(error),
            "Stack Trace": traceback.format_exception(type(error), error, error.__traceback__)
        }
        
        if (ctx.guild):
            errorData["ctx"]["Server ID"] == ctx.guild.id
        
        if (str(ctx.author.id) in playerStatuses):
            playerStatus = playerStatuses[str(ctx.author.id)]
            pprint.pprint(playerStatus)
            if ("Stack" in playerStatus):
                plate = playerStatus["Stack"].top
                
                while(plate):
                    plate.value = plate.value["State"]
                    plate = plate.below
                
                errorData["Player Status"] = FileHandling.saveObject(playerStatus)
        
        for char in ('-', ':', '.'):
            errorTime = errorTime.replace(char, '')
        
        try:
            with open(f"ErrorLogs/{errorTime}.json", 'w') as json_file:
                json.dump(errorData, json_file, indent = 4)
                
            print(f"Above error has been saved with code <{errorTime}>")
                
        except: 
            with open(f"ErrorLogs/DEEPERROR_{errorTime}.json", 'w') as f:
                f.write("THE FOLLOWING ERROR HAS NOT BEEN HANDLED PROPERLY:\n")
                f.write(str(errorData))
                f.close()
        
        await ctx.send(f"The following error has occurred: \"{str(error)}\"")
        await ctx.send(f"_Error has been logged as <{errorTime}>._")
        
        print(f"Above error has been handled!\n")
    
    #When loaded
    @commands.Cog.listener()
    async def on_ready(self):
        print("Loaded NationsCog.py")
    
    #Log in to a specific game
    @commands.command()
    async def login(self, ctx, gameName):
        noGameFound = True
        for filename in os.listdir("./Savegames"):
            if (filename[:-5].split(" - ")[0] == gameName):
                noGameFound = False
                with open(f"Savegames/{filename}") as f:
                    saveGame = FileHandling.loadObject(json.load(f))
                    saveGames[saveGame.ID] = saveGame
                    break
                    
        if (noGameFound): raise GameException(f"PLAYER <{ctx.author.id}> UNABLE TO LOG INTO GAME <{gameName}>")
        
        player = str(ctx.author.id)
        if (player not in playerStatuses):
            playerStatuses[player] = {}
        playerStatuses[player]["GameID"] = saveGame.ID
        
        await ctx.send(f"Logged in to game: <{gameName}>")
    
    #If the player is on a menu with multiple pages, this turns to the requested page number.
    @commands.command()
    async def page(self, ctx, pageNo):
        if ("Stack" in playerStatuses[str(ctx.author.id)]):
            stack = playerStatuses[str(ctx.author.id)]["Stack"]
            
            try:
                if (int(pageNo) < len(stack.top.value["Pages"])):
                    pageNo = min(len(stack.top.value["Pages"]), max(0, int(pageNo)))
                    await ctx.send(embed = stack.top.value["Pages"][pageNo])
                
                else: 
                    raise GameException(f"PAGE <{pageNo}> OUT OF BOUNDS (max is {len(stack.top.value['Pages']) - 1})")
            
            except: raise GameException(f"PAGE NUMBER IS INVALID (valid page numbers are between 0 and {len(stack.top.value['Pages']) - 1})")
    
    #Brings the player's menu progression back to the previous menu.
    @commands.command()
    async def back(self, ctx):
        if ("Stack" in playerStatuses[str(ctx.author.id)]):
            #Pop the top status (most recent menu)
            popped = playerStatuses[str(ctx.author.id)]["Stack"].pop()
            await ctx.send(f"_Leaving menu for {popped['State']}..._")
            
            #If there is still a top, show the display for top.
            if (playerStatuses[str(ctx.author.id)]["Stack"].top):
                newTop = playerStatuses[str(ctx.author.id)]["Stack"].top
                
                page = min(len(newTop.value["Pages"]), max(0, newTop.value["Page"]))
                await ctx.send(embed = newTop.value["Pages"][page])
    
    #Gets an entry from the game dictionary
    @commands.command()
    async def gameDict(self, ctx, key):
        return None
    
    '''INFORMATION COMMANDS'''
    
    #Main menu for national info
    @commands.command()
    async def nationInfo(self, ctx):
        gameInfo = getGameInfo(ctx)
        
        nationalInfo = NationController.nationalInfo(gameInfo["Savegame"], gameInfo["Nation Name"])
        
        newEmbed = discord.Embed(
            title = f"Nation <{gameInfo['Nation Name']}> Main Menu",
            description = "_Type 'n.exit' to log out of this game at any time._",
            color = discord.Color.from_rgb(153, 0, 0)
        )
        
        newEmbed.add_field(name = f"Military Forces and Expeditions ({len(nationalInfo['Forces'])}):", value = "Type n.armies, n.fleets or n.expeditions for more info", inline = False)
        
        newEmbed.add_field(name = f"Territories ({len(nationalInfo['Territories'].keys())}):", value = "Type n.territories for more info", inline = False)
        
        newEmbed.add_field(name = f"Government:", value = "Type n.government for more info", inline = False)
        
        newEmbed.add_field(name = f"Resources:", value = "Type n.resources for more info", inline = False)
        
        playerStatuses[str(ctx.author.id)]["Stack"] = Util.Stack({"State": "n.nationInfo", "Pages": [newEmbed], "Page": 0})
        playerStatuses[str(ctx.author.id)]["Stack"].push({"State": "testState", "Pages": "test"})
        
        fileName = gameInfo["Savegame"].saveMapImage(gameInfo["Nation Name"])
        
        file = discord.File(fileName, filename = fileName)
        newEmbed.set_image(url = f"attachment://{fileName}")
        
        await ctx.send(file = file, embed = newEmbed)

    #Gets information of all territories or a specific territory
    @commands.command()
    async def territories(self, ctx, *optionalArgs): #optionalArgs is either an territory name or page number
        gameInfo = getGameInfo(ctx)
        
        terrs = NationController.allTerritories(gameInfo["Savegame"], gameInfo["Nation Name"])
        optionalArg = ' '.join(optionalArgs)
        
        if (optionalArg in terrs):
            territory = NationController.getTerritory(gameInfo["Savegame"], gameInfo["Nation Name"], optionalArg)
            
            newEmbed = discord.Embed(
                    title = f"{optionalArg}",
                    description = f"Status: \"{territory.status}\"",
                    color = discord.Color.from_rgb(153, 0, 0)
                )
            newEmbed.add_field(name = f"Projects: {len(territory.projects.keys())}", value = f"_Type n.projects {optionalArg} to view all projects_", inline = False)
            
            if (isinstance(territory, GameObjects.HabitableTerritory)):
                newEmbed.add_field(name = f"Demographics: {len(territory.demographics.keys())}", value = f"_Type n.demographics {optionalArg} to view all projects_", inline = False)
                
            await ctx.send(embed = newEmbed)
        
            if ("Stack" not in playerStatuses[str(ctx.author.id)]):
                playerStatuses[str(ctx.author.id)]["Stack"] = Util.Stack()
            
            playerStatuses[str(ctx.author.id)]["Stack"].push({"State": f"n.territories:{optionalArg}", "Pages": [newEmbed], "Page": 0})
        
        else:
            if (optionalArg.isdigit()): optionalArg = int(optionalArg)
            else: optionalArg = 0
            
            pages = makePages(
                list(terrs.values()),
                f"Nation <{gameInfo['Nation Name']}> Territories",
                "_Type 'n.territories <pageNo>' to go to a specific page, or n.territories <territory name> to get a territory's information._",
                ["name"],
                ["status"] )
        
            await ctx.send(embed = pages[min(len(pages) - 1, max(0, int(optionalArg)))])
        
            if ("Stack" not in playerStatuses[str(ctx.author.id)]):
                playerStatuses[str(ctx.author.id)]["Stack"] = Util.Stack()
            
            playerStatuses[str(ctx.author.id)]["Stack"].push({"State": f"n.territories:{optionalArg}", "Pages": pages, "Page": optionalArg})
    
    #Gets a list of projects in a territory or a specific project
    @commands.command()
    async def projects(self, ctx, *optionalArgs): #requiredArgs is a territory name or specific project
        gameInfo = getGameInfo(ctx)
        optionalArg = ' '.join(optionalArgs)
        
        territory = NationController.getTerritory(gameInfo["Savegame"], gameInfo["Nation Name"], optionalArgs)
        
        pages, pageNo = [], 0
        
        #If this is a territory
        if (territory):
            
            pagedProjects = Util.pageify(list(territory.projects.values()), 10)
            
            for page in pagedProjects:
            
                newEmbed = discord.Embed(
                        title = f"{optionalArg} Projects || Page {pageNo}/{len(pagedProjects) - 1}",
                        description = f"Status: \"{territory.status}\"\n_Type 'n.page <pageNo>' to go to a specific page._",
                        color = discord.Color.from_rgb(153, 0, 0)
                    )
                    
                for project in page:
                    newEmbed.add_field(name = f"{territory.name} ({project.name})", value = f"Status: {project.status}", inline = False)
                
                pages.append(newEmbed)
                pageNo += 1
            
            await ctx.send(embed = pages[0])
            
            if ("Stack" not in playerStatuses[str(ctx.author.id)]):
                playerStatuses[str(ctx.author.id)]["Stack"] = Util.Stack()
            
            playerStatuses[str(ctx.author.id)]["Stack"].push({"State": f"n.projects:{optionalArg}", "Pages": pages, "Page": 0})
        
        #If we want to see the information for a particular buildable rather than all the projects in one territory
        elif (optionalArg):
            buildable = GameDictInfo.buildableInfo(gameInfo["Savegame"], optionalArg)
            
            if (buildable):
                newEmbed = discord.Embed(
                        title = optionalArg + " Information",
                        description = f"Size: {buildable['buildingCosts']['size']}, Category: {buildable['category']}, Build Time: {buildable['buildTime']}",
                        color = discord.Color.from_rgb(153, 0, 0)
                    )
                    
                completionEffects = buildable["Completion Effects"]
                
                #=================
                
                #Put all territory requirements into one string
                territoryRequirements = ">>> "
                
                for requirement in buildable["territoryRequirements"].keys():
                    territoryRequirements += "  " + requirement[:1].upper() + requirement[1:] + ": " + str(buildable["territoryRequirements"][requirement]) + "\n"
                
                #Add territory requirements field
                newEmbed.add_field(name = "**Territory Requirements:**\n", 
                    value = territoryRequirements, 
                    inline = False)
                
                #=================
                    
                #Put all resource costs into one string
                resourceCosts = ">>> "
                
                for resource in buildable["buildingCosts"]["resourceCosts"].keys():
                    resourceCosts += "  " + resource + ": " + str(buildable["buildingCosts"]["resourceCosts"][resource]) + "\n"
                
                #Add resource costs field
                newEmbed.add_field(name = "**Resource Costs:**\n", 
                    value = resourceCosts, 
                    inline = False)
                
                #=================
                
                #Put all maintenance costs into one string
                maintenanceCosts = ">>> "
                
                for resource in buildable["Maintenance Costs"].keys():
                    maintenanceCosts += "  " + resource + ": " + str(buildable["Maintenance Costs"][resource]) + "\n"
                
                #Add maintenance costs field
                newEmbed.add_field(name = "**Maintenance Costs:**\n", 
                    value = maintenanceCosts, 
                    inline = False)
                
                #=================
                
                #Put all national/territorial, cumulative/exponential effects in a string for each
                
                for superEffectLevel in completionEffects.keys():
                    for effectLevel in completionEffects[superEffectLevel].keys():
                        allEffects = ">>> "
                        
                        for effectType in completionEffects[superEffectLevel][effectLevel].keys():
                        
                            for effectName in completionEffects[superEffectLevel][effectLevel][effectType].keys():
                                
                                allEffects += "  " + effectName + ": " + str(completionEffects[superEffectLevel][effectLevel][effectType][effectName]) + "\n"
                    
                            #Add effects fields
                            newEmbed.add_field(name = f"**{effectLevel} {effectType} Effects:**\n", 
                                value = allEffects, 
                                inline = False)
                
                #=================
            
                await ctx.send(embed = newEmbed)
                
                if ("Stack" not in playerStatuses[str(ctx.author.id)]):
                    playerStatuses[str(ctx.author.id)]["Stack"] = Util.Stack()
                
                playerStatuses[str(ctx.author.id)]["Stack"].push({"State": f"n.projects", "Pages": [newEmbed], "Page": 0})
                
            else: await ctx.send(f"Building \"{optionalArg}\" does not exist!")
        
        #If we want to see all buildables
        else:
            allBuildables = GameDictInfo.allBuildables(gameInfo["Savegame"])
            pagedBuildables = Util.pageify(list(allBuildables.values()), 10)
            
            for page in pagedBuildables:
            
                newEmbed = discord.Embed(
                        title = f"{optionalArg} Projects || Page {pageNo}/{len(pagedBuildables) - 1}",
                        description = f"All buildable projects\n_Type 'n.page <pageNo>' to go to a specific page._",
                        color = discord.Color.from_rgb(153, 0, 0)
                    )
                    
                for project in page:
                    
                    newEmbed.add_field(name = f"{project['name']}", 
                        value = f"Size: {project['buildingCosts']['size']}, Category: {project['category']}, Build Time: {project['buildTime']}", 
                        inline = False)
                
                pages.append(newEmbed)
                pageNo += 1
            
            await ctx.send(embed = pages[0])
            
            if ("Stack" not in playerStatuses[str(ctx.author.id)]):
                playerStatuses[str(ctx.author.id)]["Stack"] = Util.Stack()
            
            playerStatuses[str(ctx.author.id)]["Stack"].push({"State": f"n.projects", "Pages": pages, "Page": 0})
    
    #Gets a list of demographics in the nation or in a territory
    @commands.command()
    async def demographics(self, ctx, *optionalArgs): #requiredArgs is a territory name or specific demographic
        gameInfo = getGameInfo(ctx)
        optionalArg = ' '.join(optionalArgs)
        
        #If optionalArg is not specified, get all of the demographic info for the nation
        if not(optionalArg): 
            allDemographics = {}
            
            #Add all national demographic totals
            for territory in gameInfo["Savegame"][gameInfo["Nation Name"]].territories.values():
                if (isinstance(territory, GameObjects.HabitableTerritory)):
                    for demographic in territory.demographics.values():
                        
                        #If this demographic doesn't have an entry, add one
                        if not(demographic.name in allDemographics.keys()):
                            allDemographics[demographic.name] = {
                                "Name": demographic.name,
                                "Population": 0,
                                "Population Growth Percentage": 0,
                                "Population Growth": 0,
                                "Average Unrest": 0,
                                "Average Unrest Growth": 0,
                                "Count": 0 #For calculating averages
                            }
                        
                        allDemographics[demographic.name]["Population"] += demographic.populationData[0]
                        allDemographics[demographic.name]["Population Growth Percentage"] += demographic.populationData[1]
                        allDemographics[demographic.name]["Average Unrest"] += demographic.unrestData[0]
                        allDemographics[demographic.name]["Average Unrest Growth"] += demographic.unrestData[1]
                        allDemographics[demographic.name]["Count"] += 1
            
            #Get averages by dividing by count
            for demographic in allDemographics:
                count = allDemographics[demographic]["Count"]
                
                for key in ("Population", "Population Growth", "Average Unrest", "Average Unrest Growth"):
                    
                    #Get averages
                    if (key in ("Population Growth", "Average Unrest", "Average Unrest Growth")): allDemographics[demographic][key] /= count
                    
                    #convert to int
                    allDemographics[demographic][key] = int(allDemographics[demographic][key])
                
                #Get number of people added to the pop next year
                allDemographics[demographic]["Population Growth"] = int(allDemographics[demographic]["Population Growth Percentage"] * allDemographics[demographic]["Population"])
            
            totalPop = sum(demo["Population"] for demo in allDemographics.values() if demo)
            totalPopGrowth = int(sum(demo["Population Growth"] for demo in allDemographics.values() if demo))
                    
            pages = makePages(
            list(allDemographics.values()),
            f"{gameInfo['Nation Name']} Total Demographics",
            f"Total Population is {totalPop} growing by {totalPopGrowth} people annually",
            ["Name"],
            [">>> ", "Population", '\n', "Population Growth", '\n', "Average Unrest", '\n', "Average Unrest Growth"])
            
            await ctx.send(embed = pages[0])
            
            pprint.pprint(allDemographics)
        
        #If this is a territory
        elif (optionalArg in gameInfo["Savegame"][gameInfo["Nation Name"]].territories.keys()):
        
            territory = NationController.getTerritory(gameInfo["Savegame"], gameInfo["Nation Name"], optionalArg)
            
            pages = makePages(
            list(territory.demographics.values()),
            f"{optionalArg} Demographics",
            "PopulationData and UnrestData are formatted like this: [Amount, Annual Growth %]",
            ["name"],
            [">>> ", "populationData", '\n', "unrestData"])
            
            await ctx.send(embed = pages[0])
            
            if ("Stack" not in playerStatuses[str(ctx.author.id)]):
                playerStatuses[str(ctx.author.id)]["Stack"] = Util.Stack()
            
            playerStatuses[str(ctx.author.id)]["Stack"].push({"State": f"n.demographics:{optionalArg}", "Pages": pages, "Page": 0, "Territory": territory})
        
        #If we're already on a territory, get the info for the specified demographic in this territory.
        elif ("Territory" in playerStatuses[str(ctx.author.id)]["Stack"].top.value):
            territory = playerStatuses[str(ctx.author.id)]["Stack"].top.value["Territory"]
            
            #If this demographic exists in this territory
            if (optionalArg in territory.demographics):
                demographic = territory.demographics[optionalArg]
                
                newEmbed = discord.Embed(
                    title = territory.name + " " + optionalArg + " Information",
                    #description = f"",
                    color = discord.Color.from_rgb(153, 0, 0)
                )
                
                newEmbed.add_field(name = "**Population:**\n", 
                    value = ">>> " + str(demographic.populationData[0]) + "\nGrowth: " + str(demographic.populationData[1] * 100) + f"% Annually ({int(demographic.populationData[0] * demographic.populationData[1])} next year)", 
                    inline = False)
                    
                newEmbed.add_field(name = "**Unrest:**\n", 
                    value = ">>> " + str(demographic.unrestData[0]) + "\nGrowth: " + str(demographic.unrestData[1] * 100) + f"% Annually ({demographic.unrestData[0] * demographic.unrestData[1]} next year)", 
                    inline = False)
                
                await ctx.send(embed = newEmbed)
            
        else: await ctx.send(f"\"{optionalArg}\" cannot be found, please choose a valid Territory or Demographic")
    
    #Gets information of all armies or a specific army
    @commands.command()
    async def armies(self, ctx, *optionalArgs): #optionalArg is either an army name or page number
        gameInfo = getGameInfo(ctx)
        
        armies = NationController.armiesInfo(gameInfo["Savegame"], gameInfo["Nation Name"])
        optionalArg = ' '.join(optionalArgs)
        
        #Army name is specified
        if (optionalArg in armies):
            army = NationController.getUnitGroup(gameInfo["Savegame"], gameInfo["Nation Name"], optionalArg)
            
            pages = makePages(
            list(army.composition.values()),
            optionalArg,
            f"Location: {army.territory}, Status: \"{army.status}\"",
            ["name", "status"],
            ["OMIT_ALL_LABELS", "unitType", "|", "size", "|", "homeTerritory"])
            
            await ctx.send(embed = pages[0])
            
            if ("Stack" not in playerStatuses[str(ctx.author.id)]):
                playerStatuses[str(ctx.author.id)]["Stack"] = Util.Stack()
            
            playerStatuses[str(ctx.author.id)]["Stack"].push({"State": f"n.armies:{optionalArg}", "Pages": pages, "Page": 0})

        #No army specified: open a menu of armies.
        else:
            if (optionalArg.isdigit()): optionalArg = int(optionalArg)
            else: optionalArg = 0
            
            pages = makePages(
            list(armies.values()),
            f"Nation <{gameInfo['Nation Name']}> Armies",
            "_Type 'n.armies <pageNo>' or 'n.page <pageNo>' to go to a specific page, or n.armies <army name> to get an army's information._",
            ["name"],
            ["size", "|", "territory", "|", "status"])
            
            await ctx.send(embed = pages[min(len(pages) - 1, max(0, int(optionalArg)))])
        
            if ("Stack" not in playerStatuses[str(ctx.author.id)]):
                playerStatuses[str(ctx.author.id)]["Stack"] = Util.Stack()
            
            playerStatuses[str(ctx.author.id)]["Stack"].push({"State": f"n.armies:{optionalArg}", "Pages": pages, "Page": optionalArg})
    
    #Gets information of all fleets or a specific fleet
    @commands.command()
    async def fleets(self, ctx, *optionalArgs): #optionalArg is either an fleet name or page number
        gameInfo = getGameInfo(ctx)
        
        fleets = NationController.fleetsInfo(gameInfo["Savegame"], gameInfo["Nation Name"])
        optionalArg = ' '.join(optionalArgs)
        
        #Fleet name is specified
        if (optionalArg in fleets):
        
            fleet = NationController.getUnitGroup(gameInfo["Savegame"], gameInfo["Nation Name"], optionalArg)
            
            pages = makePages(
            list(fleet.composition.values()),
            optionalArg,
            f"Location: {fleet.territory}, Status: \"{fleet.status}\"",
            ["name", "status"],
            ["OMIT_ALL_LABELS", "name", "|", "size", "|", "homeTerritory"])
            
            await ctx.send(embed = pages[0])
            
            if ("Stack" not in playerStatuses[str(ctx.author.id)]):
                playerStatuses[str(ctx.author.id)]["Stack"] = Util.Stack()
            
            playerStatuses[str(ctx.author.id)]["Stack"].push({"State": f"n.fleets:{optionalArg}", "Pages": pages, "Page": 0})

        #No fleet specified: open a menu of fleets.
        else:
            if (optionalArg.isdigit()): optionalArg = int(optionalArg)
            else: optionalArg = 0
            
            pages = makePages(
            list(fleets.values()),
            f"Nation <{gameInfo['Nation Name']}> Fleets",
            "_Type 'n.fleets <pageNo>' to go to a specific page, or n.fleets <fleet name> to get a fleet's information._",
            ["name"],
            ["OMIT_ALL_LABELS", "territory", "|", "status"])
            
            #["OMIT_ALL_LABELS", "rawSize", "|", "territory", "|", "status"])
            
            await ctx.send(embed = pages[0])
            
            if ("Stack" not in playerStatuses[str(ctx.author.id)]):
                playerStatuses[str(ctx.author.id)]["Stack"] = Util.Stack()
            
            playerStatuses[str(ctx.author.id)]["Stack"].push({"State": f"n.fleets:{optionalArg}", "Pages": pages, "Page": optionalArg})

    ''' MILITARY GAMEPLAY COMMANDS '''
    
    #Build a new Army
    @commands.command()
    async def trainArmy(self, ctx, *args):
    
        gameInfo = getGameInfo(ctx)
        saveGame = gameInfo["Savegame"]
        nationName = gameInfo["Nation Name"]
        
        vars = self.validateArgs(args,
            {
            "size": self.Flags.INT,
            "unit": gameInfo["Savegame"].getGameDict()["Game Objects"]["Divisions"],
            "territory": NationController.allTerritories(gameInfo["Savegame"], gameInfo["Nation Name"])
            }
        )
        
        newArmy = NationController.trainUnitGroup(gameInfo["Savegame"], gameInfo["Nation Name"], "Army", vars["unit"], vars["size"], vars["territory"])
        
        if (newArmy):
            newEmbed = discord.Embed(
                title = f"Building {vars['size']} {vars['unit']} in {vars['territory']}!",
                description = f"Date of completion: {newArmy.status.split(':')[1]}",
                color = discord.Color.red()
            )
            await ctx.send(embed = newEmbed)
            
        else: await ctx.send(f"Unable to build {vars['size']} {vars['unit']} in {vars['territory']}")

    #Build a new Fleet
    @commands.command()
    async def trainFleet(self, ctx, *args):
    
        gameInfo = getGameInfo(ctx)
        saveGame = gameInfo["Savegame"]
        nationName = gameInfo["Nation Name"]
        
        vars = self.validateArgs(args,
            {
            "size": self.Flags.INT,
            "unit": gameInfo["Savegame"].getGameDict()["Game Objects"]["Ships"],
            "territory": NationController.allTerritories(gameInfo["Savegame"], gameInfo["Nation Name"])
            }
        )
        
        newArmy = NationController.trainUnitGroup(gameInfo["Savegame"], gameInfo["Nation Name"], "Fleet", vars["unit"], vars["size"], vars["territory"])
        
        if (newArmy):
            newEmbed = discord.Embed(
                title = f"Building {vars['size']} {vars['unit']} in {vars['territory']}!",
                description = f"Date of completion: {newArmy.status.split(':')[1]}",
                color = discord.Color.red()
            )
            await ctx.send(embed = newEmbed)
            
        else: await ctx.send(f"Unable to build {vars['size']} {vars['unit']} in {vars['territory']}")

    #Move a unit group from its current location to another territory.
    @commands.command()
    async def move(self, ctx, *args):
        #saveGame, nation, unitGroup, destination
        gameInfo = getGameInfo(ctx)
        saveGame = gameInfo["Savegame"]
        nationName = gameInfo["Nation Name"]
        
        vars = self.validateArgs(args,
            {
            "unitGroup": gameInfo["Savegame"][gameInfo["Nation Name"]].unitGroups.keys(),
            "destination": NationController.traversableTerritories(gameInfo["Savegame"], gameInfo["Nation Name"])
            }
        )
        
        moved = NationController.moveUnitGroup(saveGame, nationName, vars['unitGroup'], vars['destination'])
        
        if (moved != False):
            
            #movement status looks like: "Moving:Territory;Date>>Territory;Date>>..Territory;Date>>
            terrList = moved.status.split(':')[1]
            pathStr = ">>> "
            for pathNode in terrList.split('>>')[0:-1]:
                nodeData = pathNode.split(';')
                pathStr += nodeData[0] + ": Arrive on " + nodeData[1] + '\n'
            
            newEmbed = discord.Embed(
                title = f"Moving {vars['unitGroup']} to {vars['destination']}!",
                color = discord.Color.red()
            )
            
            newEmbed.add_field(name = "Starting from:", value = moved.territory, inline = False)
            newEmbed.add_field(name = "Path:", value = pathStr, inline = False)
            
            await ctx.send(embed = newEmbed)
        
        else: await ctx.send(f"Unable to move {vars['unitGroup']} to {vars['destination']}")
            
    #Merge multiple unit groups of the same class (e.g. "Army", "Fleet", etc)
    @commands.command()
    async def merge(self, ctx, *args):
        gameInfo = getGameInfo(ctx)
        saveGame = gameInfo["Savegame"]
        nationName = gameInfo["Nation Name"]
        
        vars = self.validateArgs(args,
            {
            "coreUnitGroup": gameInfo["Savegame"][gameInfo["Nation Name"]].unitGroups.keys(),
            int(self.Flags.LIST): {
                "groupsToMerge": gameInfo["Savegame"][gameInfo["Nation Name"]].unitGroups.keys()
                }
            }
        )
        
        merged = NationController.mergeUnitGroups(saveGame, nationName, vars['coreUnitGroup'], *vars['groupsToMerge'])
        
        if (merged):
            
            #Show the new army information
            pages = makePages(
            list(merged.composition.values()),
            f"Merged {vars['groupsToMerge']} into {vars['coreUnitGroup']}",
            f"Location: {merged.territory}, Status: \"{merged.status}\"",
            ["name", "status"],
            ["OMIT_ALL_LABELS", "unitType", "|", "size", "|", "homeTerritory"])
            
            await ctx.send(embed = pages[0])
            
            if ("Stack" not in playerStatuses[str(ctx.author.id)]):
                playerStatuses[str(ctx.author.id)]["Stack"] = Util.Stack()
            
            playerStatuses[str(ctx.author.id)]["Stack"].push({"State": f"n.merge:{vars['coreUnitGroup']}", "Pages": pages, "Page": 0})
            
        else: await ctx.send(f"Unable to merge {vars['coreUnitGroup']} with {vars['groupsToMerge']}")

    #Merge multiple unit groups of the same class (e.g. "Army", "Fleet", etc)
    @commands.command()
    async def toggleMobilization(self, ctx, *args):
        
        gameInfo = getGameInfo(ctx)
        
        vars = self.validateArgs(args,
            {
            "unitGroup": gameInfo["Savegame"][gameInfo["Nation Name"]].unitGroups.keys(),
            }
        )
        
        NationController.toggleMobilization(gameInfo["Savegame"], gameInfo["Nation Name"], vars['unitGroup'])
        
        newStatus = gameInfo['Savegame'][gameInfo['Nation Name']].unitGroups[vars['unitGroup']].status
        
        #If the unitGroup's status is a countdown, reformat it for readability
        if ("Turns" in newStatus): 
            splitStatus = newStatus.split(':')
            newStatus = splitStatus[0] + " in " + splitStatus[1]
        
        await ctx.send(f"{vars['unitGroup']}'s status is now {newStatus}")
        
    #Split an army by units
    @commands.command()
    async def split(self, ctx, *args):
    
        gameInfo = getGameInfo(ctx)
        saveGame = gameInfo["Savegame"]
        nationName = gameInfo["Nation Name"]
        
        vars = self.validateArg(args,
            {"unitGroup": gameInfo["Savegame"][gameInfo["Nation Name"]].unitGroups}
        )
            
        unitGroup = vars["unitGroup"]
        args = vars[int(self.Flags.ARGS)]
        
        vars = self.validateArgs(args,
            {
            int(self.Flags.LIST):
                {
                "unitsToSplit": unitGroup.composition
                }
            }
        )
        
        splitArmies = NationController.splitUnitGroup(saveGame, nationName, unitGroup.name, *vars['unitsToSplit'])
        
        pages = makePages(
        splitArmies,
        f"Newly Split Forces",
        "_Type the appropriate commands (i.e. n.<command> <force name> to get an force's information._",
        ["name"],
        ["size", "|", "territory", "|", "status"])
        
        await ctx.send(embed = pages[0])
    
        #Not adding this to stack because its simply result confirmation
        ''' 
        if ("Stack" not in playerStatuses[str(ctx.author.id)]):
            playerStatuses[str(ctx.author.id)]["Stack"] = Util.Stack()
        
        playerStatuses[str(ctx.author.id)]["Stack"].push({"State": f"n.armies:{optionalArg}", "Pages": pages, "Page": optionalArg})
        '''
    
    #Split a unit into different units
    @commands.command()
    async def splitUnits(self, ctx, *args):
    
        '''gameInfo = getGameInfo(ctx)
        saveGame = gameInfo["Savegame"]
        nationName = gameInfo["Nation Name"]
        
        vars = self.validateArg(args,
            {"unitGroup": gameInfo["Savegame"][gameInfo["Nation Name"]].unitGroups}
        )
            
        unitGroup = vars["unitGroup"]
        args = vars[int(self.Flags.ARGS)]
        
        vars = self.validateArgs(args,
            {
            "unitToSplit": unitGroup.composition,
            "numToSplitOff": self.Flags.INT,
            "newUnitName": self.Flags.ALL
            }
        )'''

def setup(client):
    client.add_cog(GameMasterCog(client))
    client.add_cog(NationsCog(client))

#Bottom



























































#Bottom 2 Electric Boogaloo