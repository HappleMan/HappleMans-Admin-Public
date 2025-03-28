import discord
from storage import *
import json
import datetime
import time
from discord.ext import commands
from discord import app_commands
import topgg
import random
import pytz
import messageFilter
import os
from dotenv import load_dotenv

load_dotenv()

synced = []

#Bot's Settings, Initializing stuff

intents = discord.Intents.all()
intents.presences = False
intents.members = False

client = discord.Client(intents=intents)

botUID = os.getenv("BOT_UID")

ownerUID = os.getenv("OWNER_UID")

topgg.authorize(os.getenv("TOP_GG_TOKEN"), botUID)

dPrefix = "h!" #Default

colorTheme = 0x13ff00
botIcon = "https://happlecraft.com/images/adminlogo.png"
discordLink = "https://discord.gg/8GgyDPFdug"
websiteLink = "https://happle.xyz/"
patreonLink = "https://www.patreon.com/HappleCraft"

botVersion = "public 2.2"
botUpdate = " -Fixed an issue with infinite dice rolls.\n -Added some music safeguards.\n -Fixed issue preventing the bot from warning people."

voteUrl = f"https://top.gg/bot/{botUID}/vote"

bot = commands.Bot(command_prefix=dPrefix,intents=intents)
tree = app_commands.CommandTree(client=client)

#Crutial Methods

listOfCommands = json.loads(open("commands.json", "r").read())

def formEmbed(title, subtitle, body, files):
    toReturn = discord.Embed(color=colorTheme, title=subtitle, description=body)
    toReturn.set_author(name=title, icon_url=botIcon)
    if not files == False and not files is None:
        toReturn.set_thumbnail(url=files)
    return toReturn


welcomeMessage = formEmbed("HappleMan's Admin", "HappleMan's Admin is Here!", f"Thank you for choosing HappleMan's Admin!\nFor a list of commands, use `h!?`.\nWant to support HappleMan's Admin? vote for and rate it on [topgg](https://top.gg/bot/{botUID}).\n Need more help? Join the [support server]({discordLink}).", False)
rejectionMessage = formEmbed("HappleMan's Admin", "Invite me with permissions!", "Thank you for choosing HappleMan's Admin!\nIt looks like the bot was denied permissions. Most of HA's features rely on having permissions to create and modify channels, manage members, and more. Please re-invite the bot and check the `Administrator` box.", False)


def updateLogs(guildId, admin, victim, action, reason): 
    logs = getSetting(guildId, "modLogs")
    toAdd = {
        "admin": admin,
        "victim": victim,
        "action": action,
        "reason": reason,
        "time": round(time.time()) #<t:[int time representation]> for an embeded date and time
    }
    if logs:
        logs.append(toAdd)
    else:
        logs = [toAdd]
    setSetting(guildId, "modLogs", logs)
    
    
def getLogs(guild, search, stype, limit):
    #stype 1:all logs, 2:by victim, 3:by admin
    logs = getSetting(guild.id, "modLogs")
    tab = []
    
    for l in reversed(logs):
        if (stype == 1) or (stype == 2 and search == l['victim']) or (stype == 3 and search == l['admin']):
            tab.append(l)
        if len(tab) >= limit:
            break
    return tab
    
    
def hasPermission(member, permission, permsOptional = False): 
    userPerms = getattr(member.guild_permissions, permission) or member.guild_permissions.administrator or member.id == ownerUID
    botUser = member.guild.get_member(client.user.id)
    botPerms = getattr(botUser.guild_permissions, "administrator") or botUser.guild_permissions.administrator
    return userPerms and (botPerms or permsOptional)

def roleHasPermission(role, permission): 
    rolePerms = getattr(role.permissions, permission) or role.permissions.administrator
    return rolePerms

def hasPermissionChannel(member, permission,channel): 
    userPerms = getattr(channel.permissions_for(member), permission) or channel.permissions_for(member).administrator or member.id == ownerUID
    return userPerms

async def privateMessage(user, message, embeded: bool = False, files = None):
    if embeded:
        if not files is None:
            await user.send(embed= message, file = files)
        else:    
            await user.send(embed= message)
    elif not files is None:
        await user.send(message, file= files)
    else:
        await user.send(message)
    
    
def getMember(message):
    toBan = None
    if len(message.mentions) > 0:
        toBan = message.mentions[0]
    if len(message.content.split(" ")) > 1 and (toBan is None or not toBan) and message.content.split(" ")[1].isnumeric():
        toBan = message.guild.get_member(int(message.content.split(" ")[1]))
    return toBan
    
    
def getRole(message):
    toBan = None
    if len(message.role_mentions) > 0:
        toBan = message.role_mentions[0]
    if len(message.content.split(" ")) > 1 and (toBan is None or not toBan) and message.content.split(" ")[1].isnumeric():
        toBan = message.guild.get_role(int(message.content.split(" ")[1]))
    return toBan


def getReason(table, start):
    if len(table) >= start:
        start -= 1
        for x in range(0,start):
            table.remove(table[0])
        return " ".join(table)
    else:
        return "No reason provided."


def userFromMember(member):
    user = client.get_user(member.id)
    return user

def getTimer(str):
    times = ['']
    writing = 0
    onNum = True
    for i in str:
        if (i.isnumeric() and not onNum) or (not i.isnumeric() and onNum):
                writing += 1
                times.append("")
                onNum = not onNum
        times[writing] = times[writing] + i
    if len(times)%2 == 1:
        if times[0].isnumeric():
            times.pop(-1)
        else:
            times.pop(0)
    timer = round(time.time())
    lengths = {
        "s": 1,
        "m": 60,
        "h": 3600,
        "d": 86400,
        "mo": 2628288, #wont work
        "y": 31536000
    }
    changed = False
    for i in range(0,len(times)):
        if times[i].isnumeric() and times[i+1][0].lower() in lengths:
            changed = True
            timer += int(times[i]) * lengths[times[i+1][0].lower()]
    if not changed:
        timer += 10*60
    return timer
           
            
async def checkGiveaways():
    guilds = manageJson("HappleMansAdminData.json", "read", False)
    for i in guilds:
        v = guilds[i]
        if "giveawayStats" in v:
            for j in v['giveawayStats']:
                if j['endTime'] < time.time() and j['endTime'] != 0:
                    contestants = j['participants']
                    if contestants[0] == False:
                        contestants.pop(0)
                    prize = j['prize']
                    body = "An error occured"
                    winner = "0"
                    if len(contestants) > 0 and contestants[0] != False:
                        winner = random.choice(contestants)
                        j['active'] = False
                        body = f"<@{winner}> has won the **{prize}** giveaway!"
                    else:
                        body = "There were no participants!"
                    gchan = client.get_channel(int(j['channelId']))
                    if not gchan is None:
                        await gchan.send(embed = formEmbed("HappleMan's Admin", "Giveaway ended!", body, False))
                    setSetting(i, "lastGiveaway", j)
                    v['giveawayStats'].remove(j)
                    setSetting(i, "giveawayStats", v['giveawayStats'])
        
        
async def syncCommands(guild):
    if not guild.id in synced:
        synced.append(guild.id)
        tree.copy_global_to(guild=discord.Object(id=guild.id))
        await tree.sync()
    

#Commands

def help(cmd: str = None):
    if not cmd is None and not cmd.lower() == "secret" and not cmd.lower() == "all":
        for x in listOfCommands['commands']:
            if cmd.lower() == x['name'].lower() or cmd.lower() == x['short'].lower():
                name = x['name']
                nick = x['short']
                desc = x['description']
                tags = ", ".join(x['tags'])
                params = ", ".join(x['parameters'])
                usage = ", ".join(x['usage'])
                examples = ", ".join(x['examples'])
                return formEmbed("HappleMan's Admin", f"Help: h!{name}",f"**Nickname:**\nh!{nick}\n\n **Description:**\n{desc}\n\n**Tags:**\n{tags}\n\n**Parameters:**\n{params}\n\n**Usage:**\n{usage}\n\n**Examples:**\n{examples}\n", False)
        for x in listOfCommands['tags']:
            if cmd.lower() == x.lower():
                msg = ""
                for i in listOfCommands['commands']:
                    if x in i['tags']:
                        msg += f"**h!{i['name']}** (h!{i['short']}): {i['description']}\n\n"
                return formEmbed("HappleMan's Admin", f"{x} Commands",msg, False)
    return formEmbed("HappleMan's Admin", "Help",f"**Commands:**\n The full list of commands can be found at {websiteLink}admin#commands.\n\n**Support:**\nYou can join the HappleMan's Admin server at {websiteLink}support", False)

def setPrefix(member, newPrefix): #WIP
    if hasPermission(member, "manage_guild"):
        setSetting(member.guild.id, "prefix", newPrefix)
        return formEmbed("HappleMan's Admin", "Prefix", "Successfully changed prefix to " + newPrefix + ".", False)
    return formEmbed("HappleMan's Admin", "Prefix", "You do not have permission to use this command.", False)

def support():
    return formEmbed("HappleMan's Admin", "Support", f"Thanks! Here's a list of ways you can support HappleMan's Admin: \n \n - Donate to my patreon. Donations will help HappleMan's admin stay online for as long as possible. You can donate at {patreonLink} \n \n - Spread the word. It would be amazing to get as many users as possible, so it is always helpful to spread the word about HappleMan's Admin. -\n \n - Vote for and rate HappleMan's Admin on top.gg. Voting on top.gg helps promote HappleMan's Admin to the many users of top.gg. You can use the `h!vote` command for more information.", False)

def version():
    return formEmbed("HappleMan's Admin", "Version " + botVersion, botUpdate, False)

def invite():
    return formEmbed("HappleMan's Admin", "Invite", f"You can invite me at https://top.gg/bot/{botUID}.\nIf you need any help or would like to provide suggestions, feedback, or comments, you can join my discord server at {discordLink}.", False)

def vote():
    return formEmbed("HappleMan's Admin", "Vote", "You can vote for and rate HappleMan's Admin on top.gg at " + voteUrl + " . Thanks!", False)

def stats():
    list = "**Servers:** - `" + str(len(client.guilds)) + "` \n**Shards:** - `" + str(client.shard_count) + "`"
    return formEmbed("HappleMan's Admin", "Stats", list, False)

def logs(member, toBan):
    if hasPermission(member, "manage_messages") and not toBan is None:
        log = getLogs(member.guild, toBan.id, 2, 15)
        msg = "**__Logs:__**"
        warns = 0
        
        for i in range(0, len(log)):
            v = log[i]
            temp1 = v['victim']
            temp2 = v['action'].lower()
            temp3 = str(v['time'])
            temp4 = v['reason']
            temp5 = v['admin']
            msg = f"{msg}\n\n -<@{temp1}> was {temp2} by <@{temp5}> on <t:{temp3}> for: {temp4}"
            if v['action'].lower() == "warned":
                warns +=1
        msg = f"*Warns*: {str(warns)}\n\n{msg}"
        if len(log) > 0:
            return formEmbed("HappleMan's Admin", f"{toBan.display_name}'s logs", msg, False)
        else:
            return formEmbed("HappleMan's Admin", f"{toBan.display_name}'s logs", "Could not find any logs", False)
    else: #all logs search
        log = getLogs(member.guild, 0, 1, 15)
        msg = "**__All logs:__**"
        
        for i in range(0, len(log)):
            v = log[i]
            temp1 = v['victim']
            temp2 = v['action'].lower()
            temp3 = str(v['time'])
            temp4 = v['reason']
            temp5 = v['admin']
            msg = f"{msg}\n\n -<@{temp1}> was {temp2} by <@{temp5}> on <t:{temp3}> for: {temp4}"
        if len(log) > 0:
            return formEmbed("HappleMan's Admin", "Server logs", msg, False)
    return formEmbed("HappleMan's Admin", "Server logs", "You do not have permission to use this command.", False)
            
def modLogs(member, toBan): #settings for each type of log lookup
    if hasPermission(member, "manage_messages") and not toBan is None:
        log = getLogs(member.guild, toBan.id, 3, 15)
        msg = "**__Moderation logs:__**"
        for v in log:
            temp1 = v['victim']
            temp2 = v['action'].lower()
            temp3 = str(v['time'])
            temp4 = v['reason']
            temp5 = v['admin']
            msg = f"{msg}\n\n -<@{temp1}> was {temp2} by <@{temp5}> on <t:{temp3}> for: {temp4}"
        if len(log) > 0:
            return formEmbed("HappleMan's Admin", f"{toBan.display_name}'s moderation logs", msg, False)
        else:
            return formEmbed("HappleMan's Admin", f"{toBan.display_name}'s moderation logs", "Could not find any logs", False)
    return formEmbed("HappleMan's Admin", "Moderation logs", "You do not have permission to use this command.", False)
    

async def warn(member, toBan, reason): 
    if hasPermission(member, "kick_members", True) and (member.top_role > toBan.top_role or member.id == ownerUID):
        await privateMessage(toBan, formEmbed("HappleMan's Admin", "Warning", f"You have been warned in **{member.guild.name}** by <@{member.id}>: {reason}", False), True)
        updateLogs(member.guild.id, member.id, toBan.id, "Warned", reason)
        return formEmbed("HappleMan's Admin", "Warning", f"<@{member.id}> successfully warned <@{toBan.id}>: {reason}", False)
    return formEmbed("HappleMan's Admin", "Warning", "You don't have permission to warn this user.", False)

async def mute(member, toBan, reason, timer): 
    leng = round((timer-time.time())/60)
    if hasPermission(member, "manage_messages") and (member.top_role > toBan.top_role or member.id == ownerUID):
        await privateMessage(toBan, formEmbed("HappleMan's Admin", "Mute", f"You have been muted in **{member.guild.name}** for {leng} minutes by <@{member.id}>: {reason}", False), True)
        updateLogs(member.guild.id, member.id, toBan.id, f"Muted for {leng} minutes", reason)
        await toBan.timeout(datetime.datetime.fromtimestamp(timer, tz=pytz.UTC), reason=reason)
        return formEmbed("HappleMan's Admin", "Muted", f"<@{member.id}> successfully muted <@{toBan.id}> for {leng} minutes: {reason}", False)
    return formEmbed("HappleMan's Admin", "Mute", "You don't have permission to mute this user.", False)

async def unmute(member, toBan): 
    if hasPermission(member, "manage_messages") and (member.top_role > toBan.top_role or member.id == ownerUID):
        await toBan.edit(timed_out_until=None)
        return formEmbed("HappleMan's Admin", "Unmute", f"<@{member.id}> successfully unmuted <@{toBan.id}>.", False)
    return formEmbed("HappleMan's Admin", "Unmute", "You don't have permission to unmute this user.", False)

async def kick(member, toBan, reason): 
    if hasPermission(member, "kick_members") and (member.top_role > toBan.top_role or member.id == ownerUID):
        await privateMessage(toBan, formEmbed("HappleMan's Admin", "Warning", f"You have been kicked from **{member.guild.name}** by <@{member.id}>: {reason}", False), True)
        await toBan.kick(reason= reason)
        updateLogs(member.guild.id, member.id, toBan.id, "Kicked", reason)
        return formEmbed("HappleMan's Admin", "Kick", f"<@{member.id}> successfully kicked <@{toBan.id}>: {reason}", False)
    return formEmbed("HappleMan's Admin", "Kick", "You don't have permission to kick this user.", False)

async def ban(member, toBan, reason): 
    if hasPermission(member, "ban_members") and (member.top_role > toBan.top_role or member.id == ownerUID):
        await privateMessage(toBan, formEmbed("HappleMan's Admin", "Ban", f"You have been banned from **{member.guild.name}** by <@{member.id}>: {reason}", False), True)
        await toBan.ban(reason= reason)
        updateLogs(member.guild.id, member.id, toBan.id, "Banned", reason)
        return formEmbed("HappleMan's Admin", "Ban", f"<@{member.id}> successfully banned <@{toBan.id}>: {reason}", False)
    return formEmbed("HappleMan's Admin", "Ban", "You don't have permission to ban this user.", False)

async def celebratoryBan(member, toBan, reason, channel): 
    cbanvid = discord.File("Banned.mp4")
    cbanvid2 = discord.File("Banned.mp4")
    if hasPermission(member, "ban_members") and (member.top_role > toBan.top_role or member.id == ownerUID):
        await privateMessage(toBan, formEmbed("HappleMan's Admin", "Celebratory Ban", f"You just got banned from **{member.guild.name}** by <@{member.id}>, and we couldn't be happier! Reason: {reason}", False), True, cbanvid)
        await toBan.ban(reason= reason)
        updateLogs(member.guild.id, member.id, toBan.id, "Banned in style", reason)
        await channel.send(embed = formEmbed("HappleMan's Admin", "Celebratory Ban", f"<@{member.id}> successfully banned <@{toBan.id}>! 🥳 Time to celebrate! Reason: {reason}", False), file = cbanvid2)
        return
    await channel.send(embed = formEmbed("HappleMan's Admin", "Celebratory Ban", "You don't have permission to ban this user. 😢 Maybe next time.", False))

async def unban(member, id): 
    if hasPermission(member, "ban_members"):
        return formEmbed

async def clear(member, channel, num): 
    if hasPermission(member, "manage_messages"):
        if num.isnumeric() and int(num) > 1  and int(num) <= 99:
            await channel.purge(limit= int(num))
            return formEmbed("HappleMan's Admin", "Clear", f"Cleared {num} messages.", False)
        else:
            return formEmbed("HappleMan's Admin", "Clear", "Failed to clear messages.", False)
    return formEmbed("HappleMan's Admin", "Clear", "You do not have permission to clear messages.", False)
        

def togglePolls(member, channel): 
    if hasPermission(member, "manage_channels"):
        status = "*(error)*"
        chanelList = getSetting(member.guild.id, "polls")
        if str(channel.id) in chanelList:
            chanelList.remove(str(channel.id))
            status = "**Disabled**"
        else:
            chanelList.append(str(channel.id))
            status = "**Enabled**"
        setSetting(member.guild.id, "polls", chanelList)
        return formEmbed("HappleMan's Admin", "Polls", f"Polls have been {status} in this channel.", False)
    return formEmbed("HappleMan's Admin", "Polls", "You do not have permission to use this command.", False)
    

def toggleStarboard(member, channel): 
    if hasPermission(member, "manage_channels"):
        status = "*(error)*"
        chanelList = getSetting(member.guild.id, "starboard")
        if str(channel.id) == chanelList:
            chanelList = False
            status = "**Disabled** in"
        elif chanelList == False:
            hanelList = str(channel.id)
            status = "**Enabled** in"
        else:
            chanelList = str(channel.id)
            status = "**Moved to**"
        setSetting(member.guild.id, "starboard", chanelList)
        return formEmbed("HappleMan's Admin", "Starboard", f"Starboard has been {status} this channel.", False)
    return formEmbed("HappleMan's Admin", "Starboard", "You do not have permission to use this command.", False)

def toggleBlockCaps(member): 
    if hasPermission(member, "manage_messages"):
        status = "*(error)*"
        current = getSetting(member.guild.id, "blockCaps")
        if current:
            status = "**Disabled**"
        else:
           status = "**Enabled**"
        setSetting(member.guild.id, "blockCaps", not current)
        return formEmbed("HappleMan's Admin", "Caps", f"Caps block has been {status} in this server.", False)
    return formEmbed("HappleMan's Admin", "Caps", "You do not have permission to use this command.", False)

def toggleJoinMessage(member, chan): 
    if hasPermission(member, "manage_messages"):
        status = "*(error)*"
        current = getSetting(member.guild.id, "joinMessages")
        if current['enabled']:
            status = "**Disabled**"
        else:
           status = "**Enabled**"
        current['enabled'] = not current['enabled']
        if not chan is None:
            current['channelId'] = chan.id
        setSetting(member.guild.id, "joinMessages", current)
        return formEmbed("HappleMan's Admin", "Join Messages", f"Join messsages have been {status} in this server.", False)
    return formEmbed("HappleMan's Admin", "Join Messages", "You do not have permission to use this command.", False)

def toggleLeaveMessage(member, chan): 
    if hasPermission(member, "manage_messages"):
        status = "*(error)*"
        current = getSetting(member.guild.id, "joinMessages")
        if current['leaveEnabled']:
            status = "**Disabled**"
        else:
           status = "**Enabled**"
        current['leaveEnabled'] = not current['leaveEnabled']
        if not chan is None:
            current['channelId'] = chan.id
        setSetting(member.guild.id, "joinMessages", current)
        return formEmbed("HappleMan's Admin", "Join Messages", f"Join messsages have been {status} in this server.", False)
    return formEmbed("HappleMan's Admin", "Join Messages", "You do not have permission to use this command.", False)

def toggleJoinDM(member): 
    if hasPermission(member, "manage_messages"):
        status = "*(error)*"
        current = getSetting(member.guild.id, "joinMessages")
        if current['joinDM']:
            status = "**Disabled**"
        else:
           status = "**Enabled**"
        current['joinDM'] = not current['joinDM']
        setSetting(member.guild.id, "joinMessages", current)
        return formEmbed("HappleMan's Admin", "Join DMs", f"Join DMs have been {status} in this server.", False)
    return formEmbed("HappleMan's Admin", "Join DMs", "You do not have permission to use this command.", False)

def setJoinMessage(member, mes): 
    if hasPermission(member, "manage_messages"):
        current = getSetting(member.guild.id, "joinMessages")
        current['joinMessage'] = mes
        setSetting(member.guild.id, "joinMessages", current)
        return formEmbed("HappleMan's Admin", "Join Messages", f"Set the current join message.", False)
    return formEmbed("HappleMan's Admin", "Join Messages", "You do not have permission to use this command.", False)

def setLeaveMessage(member, mes): 
    if hasPermission(member, "manage_messages"):
        current = getSetting(member.guild.id, "joinMessages")
        current['leaveMessage'] = mes
        setSetting(member.guild.id, "joinMessages", current)
        return formEmbed("HappleMan's Admin", "Join Messages", f"Set the current join message.", False)
    return formEmbed("HappleMan's Admin", "Join Messages", "You do not have permission to use this command.", False)

def setJoinDM(member, mes): 
    if hasPermission(member, "manage_messages"):
        current = getSetting(member.guild.id, "joinMessages")
        current['JoinDMContent'] = mes
        setSetting(member.guild.id, "joinMessages", current)
        return formEmbed("HappleMan's Admin", "Join DMs", f"Set the current join message.", False)
    return formEmbed("HappleMan's Admin", "Join DMs", "You do not have permission to use this command.", False)

def toggleChatFilter(member): 
    if hasPermission(member, "manage_messages"):
        status = "*(error)*"
        current = getSetting(member.guild.id, "swearFilter")
        if current:
            status = "**Disabled**"
        else:
           status = "**Enabled**"
        setSetting(member.guild.id, "swearFilter", not current)
        return formEmbed("HappleMan's Admin", "Chat Filter", f"Chat Filter has been {status} in this server.", False)
    return formEmbed("HappleMan's Admin", "Chat Filter", "You do not have permission to use this command.", False)

def toggleAutoPublish(member): 
    if hasPermission(member, "manage_messages"):
        status = "*(error)*"
        current = getSetting(member.guild.id, "autoPublish")
        if current:
            status = "**Disabled**"
        else:
           status = "**Enabled**"
        setSetting(member.guild.id, "autoPublish", not current)
        return formEmbed("HappleMan's Admin", "Auto Publish", f"Auto publish has been {status} in this server.", False)
    return formEmbed("HappleMan's Admin", "Auto Publish", "You do not have permission to use this command.", False)

def toggleBlockLinks(member): 
    if hasPermission(member, "manage_messages"):
        status = "*(error)*"
        current = getSetting(member.guild.id, "blockLinks")
        if current:
            status = "**Disabled**"
        else:
           status = "**Enabled**"
        setSetting(member.guild.id, "blockLinks", not current)
        return formEmbed("HappleMan's Admin", "Links", f"Blocking links has been {status} in this server.", False)
    return formEmbed("HappleMan's Admin", "Links", "You do not have permission to use this command.", False)

def toggleAutoRole(member, role): 
    if hasPermission(member, "manage_roles"):
        status = "*(error)*"
        current = getSetting(member.guild.id, "autoRoles")
        if str(role.id) in current:
            current.remove(str(role.id))
            status = "no longer"
        else:
            current.append(str(role.id))
            status = "now"
        setSetting(member.guild.id, "autoRoles", current)
        return formEmbed("HappleMan's Admin", "Auto Role", f"The role <@&{role.id}> will {status} be given out automatically.", False)
    return formEmbed("HappleMan's Admin", "Auto Role", "You do not have permission to use this command.", False)

    
async def reactionRoles(member, guild, channel, message, content, single, slash): #save for last
    if hasPermission(member, "manage_roles"):
        content = content.replace("<@&", "")
        content = content.replace("<:", "")
        content = content.replace(">", "")
        content = content.split(" ")
        content.pop(0)
        toApply = []
        toAdd = [False, False]
        if not slash:
            if len(content[len(content)-1]) > 0 and content[len(content)-1][0].lower() == "t":
                single = True
        count = 0
        for v in content:
            if ":" in v:
                v = v.split(":")[1]
            if not (count%2 == 1):
                toAdd[0] = v
            else:
                toAdd[1] = v
            if toAdd[0].isnumeric() and toAdd[1]:
                toApply.append(toAdd)
                toAdd = [False, False]
            count += 1
        if not len(toApply) > 0:
            return formEmbed("HappleMan's Admin", "Reaction Roles", "Your command was formatted incorrectly.", False)
        if slash:
            newMessageContent = ""
            for v in toApply:
                if v[0] and v[1]:
                    emoji = v[1]
                    if emoji.isnumeric():
                        emoji = f"<:emoji:{emoji}>"
                    newMessageContent = newMessageContent + f"React with {emoji} for <@&{v[0]}>.\n"
            if single:
                newMessageContent = newMessageContent + "\nLimit one role."
            else:
                newMessageContent = newMessageContent + "\nYou may take multiple roles."
            newMessage = await channel.send(embed = formEmbed("HappleMan's Admin", "Reaction Roles", newMessageContent, False))
            message = newMessage
        saveFormat = {
            "emojisToApply": toApply,
            "canHaveMultiple": not single,
            "messageId": message.id
        }
        oldSave = getSetting(guild.id, "reactionRoles")
        if not oldSave or oldSave is None:
            oldSave = []
        oldSave.append(saveFormat)
        setSetting(guild.id, "reactionRoles", oldSave)
        for v in toApply:
            emoji = v[1]
            if emoji.isnumeric():
                emoji = f"<:emoji:{emoji}>"
            await message.add_reaction(emoji)
        return formEmbed("HappleMan's Admin", "Reaction Roles", "Reaction role message created.", False)
    return formEmbed("HappleMan's Admin", "Reaction Roles", "You do not have permission to create a reaction role message.", False)
            

async def startGiveaway(member, channel, timer, prize): 
    if hasPermission(member, "manage_messages"):
        message = await channel.send(embed = formEmbed("HappleMan's Admin", "Giveaway: " + prize, f"A Giveaway has been started by <@{member.id}>!\nThis Giveaway ends <t:{timer}:R>.\nReact with 💵 to enter.", False))
        current = getSetting(member.guild.id, "giveawayStats")
        current.append({
            "active": True,
            "guildId": member.guild.id,
            "channelId": channel.id,
            "messageId": message.id,
            "endTime": timer,
            "participants": [False],
            "prize": prize,
        })
        if not current[0]['guildId']:
            current.pop(0)
        setSetting(member.guild.id, "giveawayStats", current)
        await message.add_reaction("💵")
        return formEmbed("HappleMan's Admin", "Giveaway", "A giveaway has been started.", False)
    return formEmbed("HappleMan's Admin", "Giveaway", "You do not have permission to use this command.", False)

def endGiveaway(member): 
    if hasPermission(member, "manage_messages"):
        current = getSetting(member.guild.id, "giveawayStats")
        if current[0]['active']:
            current[0]['endTime'] = 10
        setSetting(member.guild.id, "giveawayStats", current)
        thing = current[0]['prize']
        return formEmbed("HappleMan's Admin", "Giveaway", f"Giveaway for {thing} has been ended early.", False)
    return formEmbed("HappleMan's Admin", "Giveaway", "You do not have permission to use this command.", False)

def cancelGiveaway(member): 
    if hasPermission(member, "manage_messages"):
        current = getSetting(member.guild.id, "giveawayStats")
        thing = "*unknown*"
        if current[0]['active']:
            thing = current[0]['prize']
            current.pop(0)
        return formEmbed("HappleMan's Admin", "Giveaway", f"Giveaway for {thing} has been cancelled.", False)
    return formEmbed("HappleMan's Admin", "Giveaway", "You do not have permission to use this command.", False)

def rerollGiveaway(member): 
    if hasPermission(member, "manage_messages"):
        last = getSetting(member.guild.id, "lastGiveaway")
        new = random.choice(last['participants'])
        prize = last['prize']
        return formEmbed("HappleMan's Admin", "Giveaway rerolled!", f"<@{new}> is the new winner of the **{prize}** giveaway!", False)
    return formEmbed("HappleMan's Admin", "Giveaway", "You do not have permission to use this command.", False)

async def ticketPrompt(member, channel, message, role, slash):
    if hasPermission(member, "manage_channels"):
        if slash or message is None:
            message = await channel.send(embed= formEmbed("HappleMan's Admin", "Ticket", "React with ✉️ to create a ticket.", False))
        await message.add_reaction("✉️")
        if role is None:
            role = False
        else:
            role = role.id
        catId = False
        if not channel.category is None:
            channel.category_id
        ticketPrompt = {
            "messageId": message.id,
            "roleId": role,
            "categoryId": channel.category_id 
        }
        currentList = getSetting(member.guild.id, "ticketPrompts")
        currentList.append(ticketPrompt)
        setSetting(member.guild.id, "ticketPrompts", currentList)
        return formEmbed("HappleMan's Admin", "Tickets", "Created a ticket prompt.", False)
    return formEmbed("HappleMan's Admin", "Tickets", "You do not have permission to create a ticket prompt.", False)

async def closeTicket(member, channel):
    tickets = getSetting(member.guild.id, "activeTickets")
    for t in tickets:
        if t['channelId'] == channel.id and ((t['roleId'] and not member.get_role(t['roleId'] is None)) or hasPermission(member, "manage_channels")):
            t['active'] = False
            setSetting(member.guild.id, "activeTickets", tickets)
            await channel.send(embed = formEmbed("HappleMan's Admin", "Tickets", "This ticket will close shortly.", False))
            time.sleep(5)
            await channel.delete()
    return formEmbed("HappleMan's Admin", "Tickets", "You do not have permission to use this command.", False)

async def addToTicket(member, channel, toBan):
    tickets = getSetting(member.guild.id, "activeTickets")
    for t in tickets:
        if t['channelId'] == channel.id and ((t['roleId'] and not member.get_role(t['roleId'] is None)) or hasPermission(member, "manage_channels")):
            t['additionalMembers'].append(toBan.id)
            await channel.set_permissions(toBan, view_channel= True, read_messages= True, send_messages= True, attach_files= True)
            setSetting(member.guild.id, "activeTickets", tickets)
            return formEmbed("HappleMan's Admin", "Tickets", f"Added <@{toBan.id}> to the ticket.", False)
    return formEmbed("HappleMan's Admin", "Tickets", "You do not have permission to use this command.", False)

def togglePingMods(member): 
    if hasPermission(member, "manage_channels"):
        status = "*(error)*"
        enabled = getSetting(member.guild.id, "pingMods")
        if enabled:
            enabled = False
            status = "**no longer**"
        else:
            enabled = True
            status = "**now**"
        setSetting(member.guild.id, "pingMods", enabled)
        return formEmbed("HappleMan's Admin", "Tickets", f"Moderators will {status} be pinged in tickets.", False)
    return formEmbed("HappleMan's Admin", "Tickets", "You do not have permission to use this command.", False)

def dice(dicen: int = 6, quantity: int = 1):
    if dicen > 0 and quantity > 0:
        amountsn = []
        amounts = "[error]"
        totaln = 0
        total = "[error]"
        for i in range(0, quantity + 1):
            current = random.randrange(1,dicen + 1)
            amountsn.append(current)
            totaln += current
        if quantity > 2:
            amounts = str(amountsn[0])
            for i in range(1, quantity):
                amounts = amounts + ", " + str(amountsn[i])
            total = f" Your total was {str(totaln)}."
        elif quantity == 2:
            amounts = f"{str(amountsn[0])} and {str(amountsn[1])}"
            total = f" Your total was {str(totaln)}."
        else: 
            amounts = "a " + str(amountsn[0])
            total = ""
        return f"You rolled {amounts}.{total}"
    return "There was an error rolling dice"

def coinFlip():
    return f"You flipped a coin that landed on {random.choice(['Heads', 'Tails'])}."

async def lockdown(member, channel):
    if hasPermission(member, "manage_channels") and hasPermission(member, "manage_roles"):
        ldData = getSetting(channel.guild.id, "lockdownVictims")
        memberRole = member.top_role.position
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = False
        affected = []
        if str(channel.id) in ldData:
            affected = ldData[str(channel.id)]
        for role in channel.guild.roles:
            if not role.id in affected and hasPermissionChannel(role, "send_messages", channel) and not hasPermissionChannel(role, "manage_channels", channel) and role.position < memberRole:
                await channel.set_permissions(role, overwrite= overwrite)
                affected.append(role.id)
        ldData[str(channel.id)] = affected
        setSetting(channel.guild.id, "lockdownVictims", ldData)
        return formEmbed("HappleMan's Admin", "Channel Lockdown", f"Locked down {channel.name}.", False)
    return formEmbed("HappleMan's Admin", "Channel Lockdown", "You do not have permission to use this command.", False)

async def unLockdown(member, channel):
    if hasPermission(member, "manage_channels") and hasPermission(member, "manage_roles"):
        ldData = getSetting(channel.guild.id, "lockdownVictims")
        overwrite = discord.PermissionOverwrite()
        overwrite.send_messages = True
        if str(channel.id) in ldData:
            for role in ldData[str(channel.id)]:
                await channel.set_permissions(channel.guild.get_role(role), overwrite= overwrite)
        ldData[str(channel.id)] = []
        setSetting(channel.guild.id, "lockdownVictims", ldData)
        return formEmbed("HappleMan's Admin", "Channel Lockdown", f"Unlocked {channel.name}.", False)
    return formEmbed("HappleMan's Admin", "Channel Lockdown", "You do not have permission to use this command.", False)

def shoot(one, two):
    return formEmbed("HappleMan's Warfare", "Shooting 💥🔫", f"<@{two.id}> was shot by <@{one.id}>.", False)

def serverStatsEmbed(guild):
    chanCount = len(guild.channels)
    vanity = guild.vanity_url
    ts = round(guild.created_at.timestamp())
    return formEmbed("HappleMan's Admin", guild.name, f"**Owner**: <@{guild.owner_id}>\n**Server ID**: `{guild.id}`\n**Members**: `{guild.member_count}`\n**Channels**: `{chanCount}`\n**h!Created**: <t:{ts}:R>\n**Boosts**: `{guild.premium_subscription_count}`\n**Vanity Invite URL**: {vanity}", guild.icon)

def userStats(member):
    img = member.guild_avatar
    ts = round(member.created_at.timestamp())
    bot = "No"
    if member.bot:
        bot = "Yes"
    nitro = "No"
    if not member.premium_since is None:
        nitro = f"Since <t:{round(member.premium_since.timestamp())}:D>"
    return formEmbed("HappleMan's Admin", member.display_name, f"**Mention String**: <@{member.id}>\n**User ID**: `{member.id}`\n**Username**: {member.name}\n**Created**: <t:{ts}:R>\n**Bot**: {bot}\n**Nitro**: {nitro}", member.display_avatar)

def roleStats(role):
    color = role.color
    return formEmbed("HappleMan's Admin", role.name, f"**Mention String**: <@&{role.id}>\n**Role ID**: `{role.id}`\n**Rank**: `{role.position}`\n**Color**: `{color}`", role.display_icon)

#Text Commands

@client.event
async def on_message(message):
    if not message.author.bot and len(message.content) > 1 and not "private" in message.channel.type:
        command = message.content.split(" ")
        member = message.author
        
        prefix = getSetting(message.guild.id, "prefix")
        botPerms = hasPermission(message.guild.get_member(client.user.id), "administrator")
        def matchCommand(name, abrev, length):
            return ((name and len(name) > 0 and command[0] == prefix + name) or (abrev and len(abrev) > 0 and command[0] == prefix + abrev)) and len(command) >= length
            
        
        if matchCommand("help","?", 1):
            cmddd = None
            if len(command) == 2:
                cmddd = command[1]
            await message.channel.send(embed = help(cmddd))
        
        
        if matchCommand("prefix","", 2):
            await message.channel.send(embed = setPrefix(member, command[1]))
        
        
        if matchCommand("support","sup", 1):
            await message.channel.send(embed = support())
        
        
        if matchCommand("version","ver", 1):
            await message.channel.send(embed = version())
        
        
        if matchCommand("invite","inv", 1):
            await message.channel.send(embed = invite())
        
        
        if matchCommand("vote","v", 1):
            await message.channel.send(embed = vote())
        
        
        if matchCommand("stats","", 1):
            await message.channel.send(embed = stats())
        
        
        if matchCommand("logs","", 1):
            toBan = getMember(message)
            await message.channel.send(embed = logs(member, toBan))
        
        
        if matchCommand("modlogs","mlogs", 2):
            toBan = getMember(message)
            await message.channel.send(embed = modLogs(member, toBan))
        
        
        if matchCommand("warn","w", 2):
            toBan = getMember(message)
            reason = getReason(command, 3)
            await message.channel.send(embed = await warn(member, toBan, reason))
        
        
        if matchCommand("timeout","mute", 2):
            reasonLen = 4
            timer = round(time.time() + 10*60)
            if len(command) < 3 or not any(char.isdigit() for char in command[2]):
                reasonLen -= 1
            else:
                timer = getTimer(command[2])
            toBan = getMember(message)
            reason = getReason(command, reasonLen)
            await message.channel.send(embed = await mute(member, toBan, reason, timer))
        
        
        if matchCommand("untimeout","unmute", 2):
            toBan = getMember(message)
            await message.channel.send(embed = await unmute(member, toBan))
        
        
        if matchCommand("kick","", 2):
            toBan = getMember(message)
            reason = getReason(command, 3)
            await message.channel.send(embed = await kick(member, toBan, reason))
        
        
        if matchCommand("ban","", 2):
            toBan = getMember(message)
            reason = getReason(command, 3)
            await message.channel.send(embed = await ban(member, toBan, reason))
        
        
        if matchCommand("celebratoryban","cban", 2):
            toBan = getMember(message)
            reason = getReason(command, 3)
            await celebratoryBan(member, toBan, reason, message.channel)
                
        
        
        if matchCommand("clear","", 2):
            msg = await message.channel.send(embed = await clear(member, message.channel, command[1]))
            time.sleep(5)
            await msg.delete()
        
        
        if matchCommand("togglepolls","polls", 1):
            await message.channel.send(embed = togglePolls(member, message.channel))
        
        
        if matchCommand("togglestarboard","sboard", 1):
            await message.channel.send(embed = toggleStarboard(member, message.channel))
        
        
        if matchCommand("toggleblocklinks","blocklinks", 1):
            await message.channel.send(embed = toggleBlockLinks(member))
        
        
        if matchCommand("toggleblockcaps","blockcaps", 1):
            await message.channel.send(embed = toggleBlockCaps(member))
        
        
        if matchCommand("reactionroles","rrole", 3):
            await reactionRoles(member, message.guild, message.channel, message, message.content, False, False)
        
        
        if matchCommand("startgiveaway","giveaway", 3):
            timer = getTimer(command[1])
            reason = getReason(command, 3)
            await startGiveaway(member, message.channel, timer, reason)
        
        if matchCommand("endgiveaway","end", 1):
            await message.channel.send(embed = endGiveaway(member))
        
        
        if matchCommand("cancelgiveaway","cancel", 1):
            await message.channel.send(embed = cancelGiveaway(member))
        
        
        if matchCommand("rerollgiveaway","reroll", 1):
            await message.channel.send(embed = rerollGiveaway(member))
        
        
        if matchCommand("ticketprompt","tickets", 1):
            role = getRole(message)
            await ticketPrompt(member, message.channel, message, role, False)
        
        
        if matchCommand("closeticket","close", 1):
            await closeTicket(member, message.channel)
        
        
        if matchCommand("addtoticket","add", 1):
            toBan = getMember(message)
            msg = await addToTicket(member, message.channel, toBan)
            if not msg is None:
                await message.channel.send(embed = msg)
        
        
        if matchCommand("toggleticketping","tping", 1):
            await message.channel.send(embed = togglePingMods(member))
        
        if matchCommand("diceroll","dice", 1):
            dicen = 6
            amount = 1
            if len(command) > 1 and command[1].isnumeric():
                dicen = int(command[1])
            if len(command) > 2 and command[2].isnumeric():
                amount = int(command[2])
            if dicen > 1000000:
                dicen = 1000000
            if amount > 20:
                amount = 20
            if dicen < 3:
                dicen = 3
            if amount < 1:
                amount = 1
            await message.channel.send(dice(dicen, amount))
        
        if matchCommand("coinflip","flip", 1):
            await message.channel.send(coinFlip())
        
        if matchCommand("togglechatfilter", "chatfilter", 1):
            await message.channel.send(embed = toggleChatFilter(member))
        
        if matchCommand("lockdown","lock", 1):
            await message.channel.send(embed = await lockdown(member, message.channel))
            
        
        if matchCommand("unlockdown","unlock", 1):
            await message.channel.send(embed = await unLockdown(member, message.channel))
        
        if matchCommand("serverstats","sstats", 1):
            await message.channel.send(embed = serverStatsEmbed(member.guild))
        
        
        if matchCommand("userstats","ustats", 1):
            mem = getMember(message)
            if not mem is None:
                await message.channel.send(embed = userStats(member))
        
        
        if matchCommand("rolestats","rstats", 1):
            rol = getRole(message)
            if not rol is None:
                await message.channel.send(embed = roleStats(rol))
        
        # if matchCommand("","", 1):
        #     await message.channel.send()
        
        
        
        
        
        await checkGiveaways()
        await syncCommands(message.guild)
        
        if getSetting(message.guild.id, "blockLinks") and messageFilter.blockLinks(message.content):
                await message.delete()
        
        if getSetting(message.guild.id, "blockCaps") and messageFilter.blockCaps(message.content):
                await message.delete()
        
        if getSetting(message.guild.id, "swearFilter"):
            additionalBlocked = []
            additionalBlockedSet = getSetting(message.guild.id, "blockedWords")
            if additionalBlockedSet[0] != False:
                additionalBlocked = additionalBlockedSet
            if messageFilter.swearFilter(message.content, additionalBlocked):
                await message.delete()
        
        if message.channel.type == discord.ChannelType.news and getSetting(message.guild.id, "autoPublish"):
            message.publish()
            
        if str(message.channel.id) in getSetting(message.guild.id, "polls"):
            await message.add_reaction("👍")
            await message.add_reaction("👎")
            
        #Owner-Only
        if message.author.id == ownerUID:
            if matchCommand("sync","", 1):
                await syncCommands(message.guild)
                
            if matchCommand("guildlookup","glook", 2) and command[1].isnumeric():
                id = int(command[1])
                guild = client.get_guild(id)
                if not guild is None:
                    body = f"**{guild.name}**\nOwned by **{guild.owner.name}**\nID: `{guild.id}`\n Owner Mention: <@{guild.owner.id}>"
                    await message.channel.send(embed = formEmbed("HappleMan's Admin", "Guild Lookup", body, False))
                else:
                    await message.channel.send(embed = formEmbed("HappleMan's Admin", "Guild Lookup", "Could not find the guild.", False))
            
            if matchCommand("topgg","tgg", 1):
                topgg.updateStats(client)
                
            if matchCommand("grabinvite","ginv", 2) and command[1].isnumeric():
                id = int(command[1])
                guild = client.get_guild(id)
                if not guild is None:
                    inv = await guild.invites()
                    body = "Invites:\n"
                    for i in inv:
                        body = f"{body}\n{i.inviter}'s invite: {i.url}"
                    await message.channel.send(embed = formEmbed("HappleMan's Admin", "Grab Invite", body, False))
                

#Slash Commands

@tree.command(name="help", description="Sends a link to a list of commands.")
async def _help(ctx, command: str = None):
    await ctx.response.send_message(embed= help(command), ephemeral= True)

@tree.command(name="support", description="Shares a list of ways you can support HappleMan's Admin. Thanks!")
async def _support(ctx):
    await ctx.response.send_message(embed= support(), ephemeral= True)

@tree.command(name="version", description="Sends the version and most recent update of the bot.")
async def _version(ctx):
    await ctx.response.send_message(embed= version(), ephemeral= True)

@tree.command(name="invite", description="Sends an invite link for the bot, as well as an invite to the support server.")
async def _invite(ctx):
    await ctx.response.send_message(embed= invite(), ephemeral= True)

@tree.command(name="vote", description="Sends a link to vote for the bot on top.gg. This does not grant any special privileges or boosts.")
async def _vote(ctx):
    await ctx.response.send_message(embed= vote(), ephemeral= True)

@tree.command(name="stats", description="Shows the bot's current stats.")
async def _stats(ctx):
    await ctx.response.send_message(embed= stats(), ephemeral= False)

@tree.command(name="logs", description="Shows moderation logs from the server or for a specified user.")
async def _logs(ctx, member: discord.Member=None):
    await ctx.response.send_message(embed= logs(ctx.user, member), ephemeral= False)

@tree.command(name="modlogs", description="Shows moderation logs made by a specified user.")
async def _modlogs(ctx, member: discord.Member):
    await ctx.response.send_message(embed= modLogs(ctx.user, member), ephemeral= False)

@tree.command(name="warn", description="Warns a user for a specified reason.")
async def _warn(ctx, member: discord.Member, reason: str=None):
    if reason is None:
        reason = "No reason provided."
    await ctx.response.send_message(embed= await warn(ctx.user, member, reason), ephemeral= False)

@tree.command(name="timeout", description="Puts a member of the server in timeout.")
async def _timeout(ctx, member: discord.Member, time: str, reason: str=None):
    if reason is None:
        reason = "No reason provided."
    await ctx.response.send_message(embed= await mute(ctx.user, member, reason, getTimer(time)), ephemeral= False)

@tree.command(name="untimeout", description="Takes a member out of timeout.")
async def _untimeout(ctx, member: discord.Member):
    await ctx.response.send_message(embed= await unmute(ctx.user, member), ephemeral= False)

@tree.command(name="kick", description="Kicks a member from the server.")
async def _kick(ctx, member: discord.Member, reason: str=None):
    if reason is None:
        reason = "No reason provided."
    await ctx.response.send_message(embed= await kick(ctx.user, member, reason), ephemeral= False)

@tree.command(name="ban", description="Bans a member from the server.")
async def _ban(ctx, member: discord.Member, reason: str=None):
    if reason is None:
        reason = "No reason provided."
    await ctx.response.send_message(embed= await ban(ctx.user, member, reason), ephemeral= False)

@tree.command(name="clear", description="Clears a certain amount of messages.")
async def _clear(ctx, amout: int):
    if amout > 100:
        amout = 100
    if amout < 1:
        amout = 1
    await ctx.response.defer(ephemeral= True)
    await ctx.followup.send(embed= await clear(ctx.user, ctx.channel, str(amout)))

@tree.command(name="togglepolls", description="Sets the current channel to the server's poll channel.")
async def _togglepolls(ctx):
    await ctx.response.send_message(embed= togglePolls(ctx.user, ctx.channel), ephemeral= False)

@tree.command(name="togglestarboard", description="Toggles current channel being a starboard channel.")
async def _togglestarboard(ctx):
    await ctx.response.send_message(embed= toggleStarboard(ctx.user, ctx.channel), ephemeral= False)

@tree.command(name="reactionroles", description="Creates a message that users can react to for roles.")
async def _reactionroles(ctx, input:str, limited:bool=False):
    if limited is None:
        limited = False
    await ctx.response.send_message(embed= await reactionRoles(ctx.user, ctx.guild, ctx.channel, False, "h!reactionroles " + input, limited, True), ephemeral= True)

@tree.command(name="toggleblocklinks", description="Deletes messages with links.")
async def _toggleblocklinks(ctx):
    await ctx.response.send_message(embed= toggleBlockLinks(ctx.user), ephemeral= False)

@tree.command(name="toggleblockcaps", description="Deletes messages with excessive caps.")
async def _toggleblockcaps(ctx):
    await ctx.response.send_message(embed= toggleBlockCaps(ctx.user), ephemeral= False)

@tree.command(name="togglechatfilter", description="Deletes messages with inappropriate language.")
async def _toggleblockcaps(ctx):
    await ctx.response.send_message(embed= toggleChatFilter(ctx.user), ephemeral= False)

@tree.command(name="toggleautopublish", description="Toggles automatically publishing messages in announcement channels.")
async def _toggleautopublish(ctx):
    await ctx.response.send_message(embed= toggleAutoPublish(ctx.user), ephemeral= False)

@tree.command(name="startgiveaway", description="Starts a giveaway for a certain amount of time.")
async def _startgiveaway(ctx, time: str, prize: str):
    await ctx.response.send_message(embed= await startGiveaway(ctx.user, ctx.channel, getTimer(time), prize), ephemeral= True)

@tree.command(name="endgiveaway", description="Ends a giveaway early.")
async def _endgiveaway(ctx):
    await ctx.response.send_message(embed= endGiveaway(ctx.user), ephemeral= True)

@tree.command(name="cancelgiveaway", description="Cancels a giveaway.")
async def _cancelgiveaway(ctx):
    await ctx.response.send_message(embed= cancelGiveaway(ctx.user), ephemeral= False)

@tree.command(name="rerollgiveaway", description="Rerolls a new winner for the most recent ended giveaway.")
async def _rerollgiveaway(ctx):
    await ctx.response.send_message(embed= rerollGiveaway(ctx.user), ephemeral= False)

@tree.command(name="ticketprompt", description="Creates a prompt for users to create tickets")
async def _ticketprompt(ctx, role: discord.Role = None):
    await ctx.response.send_message(embed= await ticketPrompt(ctx.user, ctx.channel, None, role, True), ephemeral= True)

@tree.command(name="closeticket", description="Closes and deletes a ticket channel.")
async def _closeticket(ctx):
    await closeTicket(ctx.user, ctx.channel)
    await ctx.response.send_message(embed= formEmbed("HappleMan's Admin", "Tickets", "Working..."), ephemeral= True)

@tree.command(name="addtoticket", description="Adds a new member to an existing ticket.")
async def _addtoticket(ctx, member: discord.Member):
    await ctx.response.send_message(embed= await addToTicket(ctx.user, ctx.channel, member), ephemeral= False)

@tree.command(name="toggleticketping", description="Toggles whether moderators are pinged in new tickets.")
async def _toggleticketping(ctx):
    await ctx.response.send_message(embed= togglePingMods(ctx.user), ephemeral= False)
    
@tree.command(name="diceroll", description="Roll dice.")
async def _diceroll(ctx, sides: int = 6, amount: int = 1):
    await ctx.response.send_message(dice(sides, amount))
    
@tree.command(name="coinflip", description="Flip a coin.")
async def _diceroll(ctx, sides: int = 6, amount: int = 1):
    await ctx.response.send_message(coinFlip())
    
@tree.command(name="lockdown", description="Lock low-ranking members out of sending messages in a channel.")
async def _lockdown(ctx):
    await ctx.response.send_message(embed= await lockdown(ctx.user, ctx.channel))
    
@tree.command(name="unlockdown", description="Unlock a locked channel.")
async def _unlockdown(ctx):
    await ctx.response.send_message(embed= await unLockdown(ctx.user, ctx.channel))

@tree.command(name="serverstats", description="View details about a server.")
async def _serverstat(ctx):
    await ctx.response.send_message(embed= await serverStatsEmbed(ctx.channel.guild))

@tree.command(name="userstats", description="View details about a member of the server.")
async def _memberstat(ctx, member: discord.Member):
    await ctx.response.send_message(embed= await userStats(member))
    
@tree.command(name="rolestats", description="View details about a role in the server.")
async def _rolestat(ctx, role: discord.Role):
    await ctx.response.send_message(embed= await roleStats(role))

#Events

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="h!help | HappleMan's Admin V." + botVersion + " |"))
    print(f'Started {client.user}')

async def onReaction(reaction, user):
    if not user.bot:
        # Starboard
        v = getSetting(reaction.message.guild.id, "starboard")
        if v and not user.bot:
            channel = reaction.message.guild.get_channel(int(v))
            if "⭐" in str(reaction.emoji) and reaction.count >= 10 and reaction.message.channel != channel:
                await channel.send(embed= formEmbed("HappleMan's Admin", f"⭐ Starred message by **{reaction.message.author.display_name}**: ⭐", reaction.message.content  + f"\n\n [Original Message]({reaction.message.jump_url})" , False))
        # Giveaways
        giveaways = getSetting(reaction.message.guild.id, "giveawayStats")
        changed = False
        if "💵" in str(reaction.emoji):
            for v in giveaways:
                if "messageId" in v and v['messageId'] == reaction.message.id:
                    if not v['participants']:
                        v['participants'] = []
                    if v['participants'][0] == False:
                        v['participants'].pop(0)
                    v['participants'].append(str(user.id))
                    changed = True
            if changed:
                setSetting(reaction.message.guild.id, "giveawayStats", giveaways)
        # Reaction Roles
        reactRoles = getSetting(reaction.message.guild.id, "reactionRoles")
        for v in reactRoles:
            if v['messageId'] == reaction.message.id:
                for ww in v['emojisToApply']:
                    if not v['canHaveMultiple']:
                        for x in reaction.message.reactions:
                            if x!= reaction:
                                await x.remove(user)
                    if ww[1] in str(reaction.emoji):
                        role = reaction.message.guild.get_role(int(ww[0]))
                        await user.add_roles(role)
        if "✉️" in str(reaction.emoji):
            ticketPrompts = getSetting(reaction.message.guild.id, "ticketPrompts")
            for prompt in ticketPrompts:
                if reaction.message.id == prompt['messageId']:
                    activeTickets = getSetting(reaction.message.guild.id, "activeTickets")
                    if activeTickets[0]['creatorId'] == False:
                        activeTickets.pop(0)
                    canCreate = True
                    for ticket in activeTickets:
                        if ticket['creatorId'] == user.id and ticket['active'] and not reaction.message.guild.get_channel(ticket['channelId']) is None:
                            canCreate = False
                            break
                        
                    if canCreate:
                        newTicket = await reaction.message.guild.create_text_channel("ticket-" + str(len(activeTickets) + 1))
                        if prompt['categoryId']:
                            cat = reaction.message.guild.get_channel(prompt['categoryId'])
                            if not cat is None:
                                await newTicket.edit(category= cat)
                        ticketData = {
                            "active": True, #If the ticket exists
                            "sourceId": prompt['messageId'], #The ID of the message from which the channel was created, to support multiple ticket groups in each server
                            "channelId": newTicket.id, #Ticket ID
                            "creatorId": user.id, #UID of ticket creator
                            "roleId": prompt['roleId'],
                            "additionalMembers": [False] #Other members able to view the channel
                        }
                        activeTickets.append(ticketData)
                        await newTicket.set_permissions(reaction.message.guild.default_role, view_channel= False, read_messages= False, send_messages= False) #view history, send messages, etc.
                        await newTicket.set_permissions(user, view_channel= True, read_messages= True, send_messages= True, attach_files= True) #view history, send messages, etc.
                        extra = ""
                        if prompt['roleId']:
                            extra = f"Ticket managed by <@&{prompt['roleId']}>.\n"
                            nrole = reaction.message.guild.get_role(prompt['roleId'])
                            if not nrole is None:
                                await newTicket.set_permissions(nrole, view_channel= True, read_messages= True, send_messages= True, attach_files= True, manage_messages= True) #delete messages, etc.
                        setSetting(reaction.message.guild.id, "activeTickets", activeTickets)
                        await reaction.remove(user)
                        content = f"<@{user.id}>"
                        if getSetting(reaction.message.guild.id, "pingMods"):
                            content = content + " <@&" + str(prompt['roleId']) + ">"
                        await newTicket.send(content = content, embed = formEmbed("HappleMan's Admin", "Tickets", f"Ticket created by <@{user.id}>.\n{extra}\nTo close tickets, use `h!closeticket` or `h!close`.\nTo add another member to a ticket, use `h!addtoticket [@member/userId]` or `h!add [@member/userId]`", False))
                    break

    
async def onReactionRemove(message, emoji, user):
    if not user.bot:
        # Giveaways
        giveaways = getSetting(message.guild.id, "giveawayStats")
        changed = False
        if emoji in "💵":
            for v in giveaways:
                if "messageId" in v and v['messageId'] == message.id:
                    if not v['participants']:
                        v['participants'] = []
                    if str(user.id) in v['participants']:
                        v['participants'].remove(str(user.id))
                    if len(v['participants']) == 0:
                        v['participants'] = [False]
                    changed = True
            if changed:
                setSetting(message.guild.id, "giveawayStats", giveaways)
        # Reaction Roles    
        reactRoles = getSetting(message.guild.id, "reactionRoles")
        for ww in reactRoles:
            if ww['messageId'] == message.id:
                for v in ww['emojisToApply']:
                    if emoji in v[1]:
                        role = message.guild.get_role(int(v[0]))
                        await user.remove_roles(role)

@client.event
async def on_raw_reaction_add(data):
    channel = await client.fetch_channel(data.channel_id)
    user = await channel.guild.fetch_member(data.user_id)
    message = await channel.fetch_message(data.message_id)
    reactionList = message.reactions
    for r in reactionList:
        if str(r.emoji) in str(data.emoji):
            await onReaction(r, user)

@client.event
async def on_raw_reaction_remove(data):
    channel = await client.fetch_channel(data.channel_id)
    user = await channel.guild.fetch_member(data.user_id)
    message = await channel.fetch_message(data.message_id)
    await onReactionRemove(message, str(data.emoji), user)

def defaultChannel(guild):
    channel = guild.system_channel
    if not channel:
        channel = guild.text_channels[0]
    return channel

@client.event
async def on_guild_join(guild):
    fixSettings(guild.id)
    topgg.updateStats(client)
    channel = defaultChannel(guild)
    botPerms = hasPermission(guild.get_member(client.user.id), "administrator")
    if botPerms:
        await channel.send(embed = welcomeMessage)
    else:
        await channel.send(embed = rejectionMessage)
    await syncCommands(guild)
    
@client.event
async def on_guild_remove(guild):
    topgg.updateStats(client)

async def joinMessage(member):
    joinMes = getSetting(member.guild.id, "joinMessages")
    if joinMes['enabled']:
        chan = joinMes['channelId']
        if chan == 0:
            chan = defaultChannel(member.guild)
        else:
            chan = member.guild.get_channel(joinMes['channelId'])
        await chan.send(joinMes['joinMessage'].replace("[guild]", member.guild.name).replace("[user]", "<@" + str(member.id) + ">"))
    if joinMes['joinDM']:
        await privateMessage(member, joinMes['JoinDMContent'].replace("[guild]", member.guild.name).replace("[user]", "<@" + str(member.id) + ">"))

async def leaveMessage(member):
    joinMes = getSetting(member.guild.id, "joinMessages")
    if joinMes['enabled']:
        chan = joinMes['channelId']
        if chan == 0:
            chan = defaultChannel(member.guild)
        else:
            chan = member.guild.get_channel(joinMes['channelId'])
        await chan.send(joinMes['leaveMessage'].replace("[guild]", member.guild.name).replace("[user]", "<@" + str(member.id) + ">"))

@client.event
async def on_member_join(member):
    await joinMessage(member)
    autoRanks = getSetting(member.guild.id, "autoRoles")
    if len(autoRanks) >= 1:
        for i in autoRanks:
            if i != "0":
                role = member.guild.get_role(int(i))
                await member.add_roles(role)

@client.event
async def on_member_remove(member):
    await leaveMessage(member)

client.run(os.getenv("BOT_TOKEN"))