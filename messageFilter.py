listOfWords = ["anal", "anus", "arse", "ass", "balls", "ballsack", "bastard", "biatch", "bitch", "bloody", "blowjob", "bollock", "boner", "boob", "bugger", "bum", "butt", "clit", "cock", "coon", "crap", "cunt", "damn", "dick", "dildo", "dyke", "fag", "felching", "fellate", "fellatio", "flange", "fuck", "fudgepacker", "goddamn", "hell", "jerk", "jizz", "knobend", "labia", "lmfao", "muff", "nigga", "nigger", "penis", "piss", "prick", "pube", "pussy", "queer", "scrotum", "sex", "shit", "slut", "smegma", "spunk", "tit", "tosser", "turd", "twat", "vagina", "wank", "whore", "1man1jar", "2girls1cup", "acrotomophilia", "algophilia", "anal", "anilingus", "anus", "apeshit", "apotemnophilia", "arse", "arsehole", "ass", "babeland", "ballcuzi", "bangbros", "bangbus", "bareback", "bastard", "bastinado", "bdsm", "beaner", "beastiality", "bellend", "bellesa", "bicon", "birdlock", "bitch", "bloody", "blowjob", "blumpkin", "bollocks", "boner", "boob", "breasts", "buddhahead", "bufter", "bugger", "bukkake", "bulldyke", "bullshit", "chinaman", "chink", "cholerophilia", "christ", "cialis", "circlejerk", "cishet", "cissy", "claustrophilia", "clit", "clitoris", "clunge", "clusterfuck", "cock", "coimetrophilia", "collaring", "coon", "coprophilia", "cornhole", "crap", "creampie", "cum", "cumming", "cumshot", "cunnilingus", "cunt", "cuntboy", "damn", "darkie", "ddlg", "dendrophilia", "dick", "dickgirl", "dildo", "dingleberry", "dipsea", "dishabiliophilia", "dogshit", "dolcett", "domination", "dominatrix", "dyke", "dystychiphilia", "edgeplay", "ejaculate", "emetophilia", "enby", "eyetie", "fag", "faggot", "felch", "fellatio", "figging", "fingerbang", "fingering", "finocchio", "fisting", "footjob", "frogeater", "frolicme", "frotting", "fuck", "fuckhead", "fucktard", "fuckwad", "fuckwit", "futanari", "gangbang", "gaysian", "genitals", "genitorture", "gerontophilia", "goatse", "gokkun", "golliwog", "gook", "goregasm", "greaseball", "grope", "hajji", "hell", "hermie", "hippophilia", "homoerotic", "honkey", "horny", "horseshit", "humping", "hymie", "incest", "intercourse", "jap", "jerkmate", "jesus", "jigaboo", "jizz", "juggs", "kike", "kinbaku", "knobbing", "kraut", "kynophilia", "lesbo", "leso", "lezzie", "literotica", "lovemaking", "masturbate", "mdlb", "meatspin", "menophilia", "muffdiving", "mvtube", "nambla", "necrophilia", "negro", "neonazi", "nigga", "nigger", "nipples", "nude", "nutten", "nymphomania", "octopussy", "oklahomo", "omorashi", "onlyfans", "orgasm", "paedophilia|pedophilia", "painslut", "paki", "pansy", "panties", "parthenophilia", "pedobear", "pegging", "penis", "peterpuffer", "phagophilia", "pikey", "pissing", "playboy", "pnigerophilia|pnigophilia", "poinephilia", "ponyboy", "ponygirl", "ponyplay", "poof", "poon", "pornhub", "pornography", "proctophilia", "pubes", "punani", "pussy", "queef", "quim", "raghead", "rape", "raping", "rectum", "retard", "rhabdophilia", "rhypophilia", "rimjob", "santorum", "scatophilia", "schlong", "scissoring", "semen", "seplophilia", "sex", "sheepshagger", "shemale", "shibari", "shit", "shithead", "shitty", "shota", "shrimping", "sissy", "skeet", "slanteye", "snatch", "snowballing", "sodding", "sodomize", "spastic", "spearchucker", "spic", "splooge", "spunk", "strappado", "swastika", "taphephilia", "thanatophilia", "threesome", "throating", "thumbzilla", "tits", "titty", "topless", "tosser", "towelhead", "tranny", "transbian", "traumatophilia", "tribbing", "tubgirl", "twat", "twink", "urophilia", "vagina", "viagra", "vibrator", "vorarephilia", "voyeurweb", "wank", "wanker", "wetback", "whore", "wigger", "wiitwd", "wog", "wolfbagging", "worldsex", "xhamster", "xnxx", "xtube", "xvideos", "xxx", "xyrophilia", "zipperhead", "zippocat", "zoophilia"]
listOfLink = ["www.", ".com", ".net", ".gg", "http:", "https:", ".me", ".org", ".cc", ".xyz", ".co.uk", "//", ".ru"]

def swearFilter(message: str, additionalWords: list = []):
    for w in listOfWords:
        if w in message.lower().replace(" ",""):
            return True
    if len(additionalWords) > 0:
        for w in additionalWords:
            if w.lower().replace(" ","") in message.lower().replace(" ",""):
                return True
    return False

def blockCaps(message: str, ratio: float = 0.4, minMessageLength: int = 6):
    if len(message) > minMessageLength:
        capsNum = 0
        for i in range(0, len(message)):
            v = message[i]
            if v != v.lower():
                capsNum += 1
        capsNum = capsNum / len(message) 
        if capsNum > ratio:
            return True
    return False

def blockLinks(message: str):
    for w in listOfLink:
        if w in message.lower().replace(" ",""):
            return True
    return False