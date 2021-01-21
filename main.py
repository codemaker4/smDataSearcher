import json
import re

def openFile(path):
    f = open(path, "r")
    content = f.read()
    f.close()
    return content

def openJsonFile(path):
    return json.loads(re.sub("//.*","",openFile(path),flags=re.MULTILINE))

def processPathAlias(path):
    return path.replace("$GAME_DATA", config["paths"]["gameData"]).replace("$SURVIVAL_DATA", config["paths"]["survivalData"])

def openRelativeFile(path):
    return openFile(config["paths"]["main"] + processPathAlias(path))

def openRelativeJsonFile(path):
    return json.loads(re.sub("//.*","",openRelativeFile(path),flags=re.MULTILINE))

def getItemNameAndDescFromUuid(uuid):
    translationData = getFullTranslationData()
    if uuid in translationData:
        if "description" in translationData[uuid]:
            return translationData[uuid]
        else:
            return {
                "title" : translationData[uuid]["title"],
                "description" : ""
            }
    else:
        return {
                "title" : "error: could not find translation entry",
                "description" : ""
            }

def getFullShapeSet():
    fileNameList = openRelativeJsonFile(config["paths"]["shapeSets"])["shapeSetList"] # get list of formatted file names from json file
    translationData = getFullTranslationData()
    fullShapeSet = [] # will be something like [blockA, blockB, partA, partB]. the blocks and parts are put in a single array, and get an added property "shapeSetName" that stores what shape set it came from (currently only blockList and partList, but an SM update may add stuff, and this code will still work)
    for fileName in fileNameList:
        shapeSet = openRelativeJsonFile(fileName)
        for shapeSetName in shapeSet: # loop through lists in shape set. Usually only one per file, either "blockList" or "partList", but this code can handle multiple lists and other listnames.
            for shape in shapeSet[shapeSetName]: # loop through individual shapes
                shape["shapeSetName"] = shapeSetName # add shape set property
                if (shape["uuid"] in translationData):
                    shape["inventoryNameAndDesc"] = translationData[shape["uuid"]]
                fullShapeSet.append(shape) # add shape to fullShapeSet
    return fullShapeSet

def getFullTranslationData():
    fullTranslationData = {}
    for translationPath in config["paths"]["translationData"]:
        translationData = openRelativeJsonFile(translationPath)
        for uuid in translationData:
            fullTranslationData[uuid] =  translationData[uuid]
    return fullTranslationData

def searchByName(searchText):
    foundUuids = []
    for uuid in translationData:
        if searchText == "*" or searchText.lower() in translationData[uuid]["title"].lower():
            for shape in fullShapeSet: # check if the found id is actually a block/part
                if shape["uuid"] == uuid: 
                    foundUuids.append(uuid)
    return foundUuids

def getCraftingRecipes():
    craftingRecipes = []
    for botType in config["paths"]["craftingTypes"]: # loop through bot types
        botRecipes = openRelativeJsonFile(config["paths"]["craftingFolder"] + botType + ".json") # get recipes from bot type
        for recipe in botRecipes:
            recipe["botType"] = botType # add botType property
            if recipe["itemId"] in translationData:
                recipe["itemNameAndTitle"] = translationData[recipe["itemId"]]
            for ingredient in recipe["ingredientList"]:
                if ingredient["itemId"] in translationData:
                    ingredient["itemNameAndTitle"] = translationData[ingredient["itemId"]]
            craftingRecipes.append(recipe)
    return craftingRecipes

def searchMakeRecipes(uuid):
    foundRecipes = []
    for craftingRecipe in craftingRecipes:
        if uuid == "*" or craftingRecipe["itemId"] == uuid:
            foundRecipes.append(craftingRecipe)
    return foundRecipes

def searchUseRecipes(uuid):
    foundRecipes = []
    for craftingRecipe in craftingRecipes:
        for ingredient in craftingRecipe["ingredientList"]:
            if ingredient["itemId"] == uuid:
                foundRecipes.append(craftingRecipe)
    return foundRecipes

def cmd_search():
    searchText = input("Give the text or uuid to search: ")
    print("Searching...")
    uuidSearch = getItemNameAndDescFromUuid(searchText)
    if uuidSearch["title"] != "error: could not find translation entry": # if uuid exists (according to translation data)
        print("found uuid:")
        print(uuidSearch["title"])
        print(uuidSearch["description"])
    else:
        print("could not find a maching uuid")
        foundUuids = searchByName(searchText)
        print("Found " + str(len(foundUuids)) + " results.")
        for uuid in foundUuids:
            print(uuid)
            titleAndDesc = getItemNameAndDescFromUuid(uuid)
            print(titleAndDesc["title"])
            print("")

def cmd_info():
    searchText = input("Give the uuid or title to search: ")
    print("searching...")
    results = []
    for shape in fullShapeSet:
        if searchText == "*" or shape["uuid"] == searchText:
            results.append(shape)
        elif shape["uuid"] in translationData:
            if searchText.lower() in translationData[shape["uuid"]]["title"].lower():
                results.append(shape)
    print("found " + str(len(results)) + " results. Here is a json formatted list:")
    print(json.dumps(results, indent=4, sort_keys=False))
    print("note: the shapeSetName property was added by the program. This property stores the name of the original shapeSet list.")
    print("note: the inventoryNameAndDesc propery was added by the program. This property stores the corresponging translation data for the inventory name and description, but is only present if this data could be found.")
    if len(results) > 10:
        f = open("result.json", "w")
        f.write(json.dumps(results, indent=4, sort_keys=False))
        f.close()
        print("The results have also been put in 'result.json' because there were a lot of results")

def cmd_getMake():
    uuid = input("give a uuid: ")
    foundRecipes = searchMakeRecipes(uuid)
    print("found " + str(len(foundRecipes)) + " crafting recipes that make " + uuid + ". Here is a json formatted list:")
    print(json.dumps(foundRecipes, indent=4, sort_keys=False))
    print("note: the botType property was added by the program. This property stores the name of the bot/thing that the crafting recipe belongs to (the filename but without the .json part)")
    print("note: the itemNameAndTitle properties were added by the program. This property stores the title and description of the uuids of crafted items and ingredients (only if found in translation data.)")
    if len(foundRecipes) > 10:
        f = open("result.json", "w")
        f.write(json.dumps(foundRecipes, indent=4, sort_keys=False))
        f.close()
        print("The results have also been put in 'result.json' because there were a lot of results")

def cmd_getUse():
    uuid = input("give a uuid: ")
    foundRecipes = searchUseRecipes(uuid)
    print("found " + str(len(foundRecipes)) + " crafting recipes that use " + uuid + ". Here is a json formatted list:")
    print(json.dumps(foundRecipes, indent=4, sort_keys=False))
    print("note: the botType property was added by the program. This property stores the name of the bot/thing that the crafting recipe belongs to (the filename but without the .json part)")

config = openJsonFile("config.json")
translationData = getFullTranslationData()
fullShapeSet = getFullShapeSet()
craftingRecipes = getCraftingRecipes()

def reload():
    config = openJsonFile("config.json")
    translationData = getFullTranslationData()
    fullShapeSet = getFullShapeSet()
    craftingRecipes = getCraftingRecipes()

running = True

while running:
    cmd = input("SM data reader > ")
    if cmd == "help":
        print("Here are the commands:")
        print("stop : stop the program.")
        print("reload: reload all files.")
        print("search : search a block or part by name or uuid.")
        print("info : get JSON info about a block or part.")
        print("getMake : get all crafting recipes that make a uuid as a JSON list. You need to enter a UUID, and cant search by item name yet.")
        print("getUse : similar to getMake, but it gets all recipes that use a given uuid.")
    elif cmd == "stop":
        running = False
        print("stopping...")
    elif cmd == "search":
        cmd_search()
    elif cmd == "info":
        cmd_info()
    elif cmd == "getMake":
        cmd_getMake()
    elif cmd == "getUse":
        cmd_getUse()
    elif cmd == "reload":
        reload()
        print("reloaded")
    else:
        print("Unknown command. Type 'help' to get help")

