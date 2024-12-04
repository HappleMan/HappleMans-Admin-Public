import json

defaultSettings = {
    "prefix": "h!",
    "polls": ['0'],
    "starboard": False,
    "autoRoles": ['0'],
    "blockLinks": False,
    "blockCaps": False,
    "swearFilter": False,
    "blockedWords": [False],
    "autoPublish": False,
    "lastMemberCount": 0,
    "joinMessages": {
        "enabled": False,
        "leaveEnabled": False,
        "joinMessage": "Welcome to **[guild]**, [user]!",
        "leaveMessage": "Sorry to see you go, [user].",
        "channelId": 0,
        "joinDM": False,
        "JoinDMContent": "Thanks for joining **[guild]**, [user]! Please read the rules."
    },
    "stats": {
        "enabled": False,
        "category": False,
        "members": False,
        "users": False,
        "bots": False
    },
    "giveawayStats": [{
        "active": False,
        "guildId": False,
        "channelId": False,
        "messageId": False,
        "prize": False,
        "endTime": 0,
        "participants": [False]
    }],
    "lastGiveaway": {
        "active": False,
        "guildId": False,
        "channelId": False,
        "messageId": False,
        "prize": False,
        "endTime": 0,
        "participants": [False]
    },
    "modLogs": [{
        "admin": "485514940313239562",
        "victim": "794759245408370729",
        "action": "Created",
        "reason": "you",
        "time": 0
    }],
    "reactionRoles": [{
            "emojisToApply": [False, False],
            "canHaveMultiple": False,
            "messageId": "0"
        }],
    "ticketPrompts": [{
        "messageId": False, #ID of the message that will be reacted to
        "roleId": False, #Role that can access the tickets
        "categoryId": False #ID of the category of the message, to put tickets into
    }],
    "activeTickets": [{
        "active": False, #If the ticket exists
        "sourceId": False, #The ID of the message from which the channel was created, to support multiple ticket groups in each server
        "channelId": False, #Ticket ID
        "creatorId": False, #UID of ticket creator
        "roleId": False,
        "additionalMembers": [False] #Other members able to view the channel 
    }],
    "pingMods": False, #ticket
    "lockdownVictims": {
        0: [False], #Channel id: list of roles to unlock
    }

}

def manageJson(file, action, data):
    if action == "write":
        with open(file, "w") as file:
            toWrite = json.dumps(data)
            if not toWrite is None and len(toWrite) > 1:
                file.write(toWrite) #dumps() encodes
    elif action == "read":
        with open(file, "r") as file:
            return json.loads(file.read()) #loads() decodes
        

def getSetting(guildId, setting):
    guildId = str(guildId)
    guilds = manageJson("HappleMansAdminData.json", "read", 0)
    if guildId in list(guilds.keys()):
        guild = guilds[guildId]
        if guild and setting in guild:
            return guild[setting]
        else:
            return fixSettings(guildId)[setting]
    else:
        fixSettings(guildId)
        guilds = manageJson("HappleMansAdminData.json", "read", 0)
        guild = guilds[guildId]
        if guild and setting in guild:
            return guild[setting]
        else:
            return fixSettings(guildId)[setting]

def setSetting(guildId, setting, value):
    guildId = str(guildId)
    guilds = manageJson("HappleMansAdminData.json", "read", 0)
    if not guildId in list(guilds.keys()):
        fixSettings(guildId)
    guild = guilds[guildId]
    guild[setting] = value
    manageJson("HappleMansAdminData.json", "write", guilds)

def fixSettings(guildId):
    modified = False
    data = manageJson("HappleMansAdminData.json", "read", 0)
    
    if not guildId in data:
        modified = True
        data[guildId] = defaultSettings
    else:
        guild = data[guildId]
        for setting in defaultSettings:
            if not setting in guild:
                modified = True
                guild[setting] = defaultSettings[setting]
    if modified:
        manageJson("HappleMansAdminData.json", "write", data)
        return data[guildId]

