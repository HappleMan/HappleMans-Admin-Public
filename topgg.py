import requests
import json

auth = None
botId = None
headers = None

def authorize(token, bId):
    if not token is None and token != "":
        global auth
        auth = token
        global botId
        botId = bId
        global headers
        headers = {
            "Authorization": auth,
            "Content-Type": "application/json"
        }

def searchBots(search, limit):
    if not headers is None:
        hed = headers
        payload = {
            "limit": limit,
            "search": search
        }
        search.replace(" ","%%20")
        search.replace("'","%%27")
        req = requests.get("https://top.gg/api/search?q=" + search, json=payload, headers=hed)
        return json.loads(req.text)

def findBot(bId):
    if not headers is None:
        hed = headers
        req =  requests.get("https://top.gg/api/users/" + str(bId), headers=hed)
        return json.loads(req.text)

def botVotes(bId):
    if not headers is None:
        hed = headers
        req =  requests.get("https://top.gg/api/bots/" + str(bId) + "/votes", headers=hed)
        return json.loads(req.text)

def botStats(bId):
    if not headers is None:
        hed = headers
        req =  requests.get("https://top.gg/api/bots/" + str(bId) + "/stats", headers=hed)
        return json.loads(req.text)

def voteCheck(userId, bId):
    if not headers is None:
        hed = headers
        payload = {
            "userId": userId,
        }
        req =  requests.get("https://top.gg/api/bots/" + str(bId) + "/check", headers=hed, json=payload)
        return json.loads(req.text)

def updateStats(client):
    if not headers is None:
        hed = headers
        payload = {
            "server_count": len(client.guilds)
            #shards?
        }
        req =  requests.post("https://top.gg/api/bots/" + str(client.user.id) + "/stats", headers=hed, json= payload)
        return json.loads(req.text)

