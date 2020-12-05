import discord
from discord.ext import commands
import json, os, pprint, traceback, datetime
from NationController import *
from ConcertOfNations import *

print("GameCogs.py GAME MASTER AND NATION COGS FOR CONCERT OF NATIONS BOT\n*****\n")

#REMINDERS:
print("-----\nREMINDERS:\n")
print("Make pages able to evaluate functions (use eval()?)!\n")
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

#Makes an embed page
def makePages(listToPage, embedTitle, embedDesc, fieldNameList, fieldValueList):
    
    #fieldNameList and fieldValueList are lists of the string names of parameters that need to be included in field names and values, respectively
    #if fieldNameList is: ["name", "|", "status" "," "territory"]
    #then the field's name will be f"{thingDict[name]} | {thingDict[status]} , {thingDict[territory]}"
    def strFromList(list, obj):
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
                    
                    if (omitFirstLabel): omitFirstLabel = False
                
                else: rtnStr += thing + ": " + str(objDict[thing]) + " "
                
            else:
                rtnStr += thing + ' '
        
        return rtnStr
    
    pages, pageNo = [], 0
    pagedList = Util.pageify(listToPage, 10)
    
    for page in pagedList:
            
        newEmbed = discord.Embed(
                title = f"{embedTitle} || Page {pageNo}/{len(pagedList) - 1}",
                description = f"{embedDesc}\n_Type 'n.page <pageNo>' to go to a specific page._",
                color = discord.Color.blue()
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
    def __init__(self, client):
        self.client = client
    
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
    
    #Gets an entry from the game dictionary
    @commands.command()
    async def gameDict(self, ctx, key):
        return None
    
    #Main menu for national info
    @commands.command()
    async def nationInfo(self, ctx):
        gameInfo = getGameInfo(ctx)
        
        nationalInfo = NationController.nationalInfo(gameInfo["Savegame"], gameInfo["Nation Name"])
        
        newEmbed = discord.Embed(
            title = f"Nation <{gameInfo['Nation Name']}> Main Menu",
            description = "_Type 'n.exit' to log out of this game at any time._",
            color = discord.Color.blue()
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
                    color = discord.Color.blue()
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
    async def projects(self, ctx, *requiredArgs): #requiredArgs is a territory name or specific project
        gameInfo = getGameInfo(ctx)
        requiredArg = ' '.join(requiredArgs)
        
        terrs = NationController.allTerritories(gameInfo["Savegame"], gameInfo["Nation Name"])
        #If this is a territory
        if (requiredArg in terrs):
            territory = NationController.getTerritory(gameInfo["Savegame"], gameInfo["Nation Name"], requiredArg)
            
            pages, pageNo = [], 0
            pagedProjects = Util.pageify(list(territory.projects.values()), 10)
            
            for page in pagedProjects:
            
                newEmbed = discord.Embed(
                        title = f"{requiredArg} || Page {pageNo}/{len(pagedProjects) - 1}",
                        description = f"Status: \"{territory.status}\"\n_Type 'n.page <pageNo>' to go to a specific page._",
                        color = discord.Color.blue()
                    )
                    
                for project in page:
                    newEmbed.add_field(name = f"{territory.name} ({project.name})", value = f"Status: {project.status}", inline = False)
                
                pages.append(newEmbed)
                pageNo += 1
            
            await ctx.send(embed = pages[0])
            
            if ("Stack" not in playerStatuses[str(ctx.author.id)]):
                playerStatuses[str(ctx.author.id)]["Stack"] = Util.Stack()
            
            playerStatuses[str(ctx.author.id)]["Stack"].push({"State": f"n.projects:{requiredArg}", "Pages": pages, "Page": 0})
        
        elif(True):
            pass
    
    #Gets a list of demographics in the nation or in a territory
    @commands.command()
    async def demographics(self, ctx, requiredArgs): #requiredArgs is a territory name or specific demographic
        pass
    
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
            ["size", "|", "location", "|", "status"])
            
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
            
            fleet = NationController.getUnitGroup(gameInfo["Savegame"], gameInfo["Nation Name"], optionalArg)
            
            pages = makePages(
            list(fleet.composition.values()),
            f"Nation <{gameInfo['Nation Name']}> Fleets",
            "_Type 'n.fleets <pageNo>' to go to a specific page, or n.fleets <fleet name> to get a fleet's information._",
            ["name"],
            ["OMIT_ALL_LABELS", "territory", "|", "status"])
            
            #["OMIT_ALL_LABELS", "rawSize", "|", "territory", "|", "status"])
            
            await ctx.send(embed = pages[0])
            
            if ("Stack" not in playerStatuses[str(ctx.author.id)]):
                playerStatuses[str(ctx.author.id)]["Stack"] = Util.Stack()
            
            playerStatuses[str(ctx.author.id)]["Stack"].push({"State": f"n.fleets:{optionalArg}", "Pages": pages, "Page": optionalArg})

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
    
def setup(client):
    client.add_cog(GameMasterCog(client))
    client.add_cog(NationsCog(client))

#Bottom
























#Bottom 2 Electric Boogaloo