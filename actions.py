import praw
import authentication
import config

def logon() :
    r = praw.Reddit(username=authentication.username, password=authentication.password, 
                    client_id=authentication.client_id, client_secret=authentication.client_secret,
                    user_agent="Cash4Cashbot")
    return r

def getUSL(r: praw.Reddit) :
    bannedlist = []
    for user in r.subreddit(config.main).banned() :
        bannedlist.append(user.name)
    return bannedlist

def banc4crep(r : praw.Reddit, list: list) :
    for user in list :
        if user not in r.subreddit(config.alt).banned() :
            r.subreddit('c4crep').banned.add(user)
            print ("Banned", user)