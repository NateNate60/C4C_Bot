import praw
import config
from userdb import Database, User
import time
import re

def logon() -> praw.Reddit:
    r = praw.Reddit(username=config.username, password=config.password, 
                    client_id=config.client_id, client_secret=config.client_secret,
                    user_agent="Cash4Cashbot")
    return r

def getUSL (r: praw.Reddit) -> None :
    bannedlist = []
    for user in r.subreddit(config.main).banned() :
        bannedlist.append(user.name)
    return bannedlist

def banc4crep (r : praw.Reddit, list: list) -> None :
    for user in list :
        if user not in r.subreddit(config.alt).banned() :
            r.subreddit('c4crep').banned.add(user)
            print ("Banned", user)

def handleflair (r: praw.Reddit, user: praw.models.Redditor, db: Database) -> None :
    """
    Give the user a new flair if they do not have one.
    """
    if next(r.subreddit("cash4cash").flair(redditor=user))['flair_text'] is None :
        u = User(user.name.lower(), 0)
        db.add(u)
        praw.models.reddit.subreddit.SubredditFlair(r.subreddit("cash4cash")).set(user.name, "0 trust pts | New Trader")

def log (r, usera: praw.models.Redditor, userb: praw.models.Redditor, amt: int, db: Database, recurse: bool = True) -> None :
    """
    Log a new transaction between two users
    """
    a = db.lookup(usera.name.lower())
    b = db.lookup(userb.name.lower())
    if (a == None) :
        a = User(usera.name, 0)
    if (b == None) :
        b = User(userb.name, 0)
    basescore = 0
    #complicated base score calculation
    if (b.status == 1) :
        if (b.score <= 200) :
            basescore = 2
        elif (b.score <= 1000) :
            basescore = 5
        elif (b.score <= 2500) :
            basescore = 10
        elif (b.score <= 5000) :
            basescore = 15
        else :
            basescore = 20
    else :
        if (b.score <= 200) :
            basescore = 5
        elif (b.score <= 1000) :
            basescore = 10
        elif (b.score <= 2500) :
            basescore = 20
        else :
            basescore = 40
    if (amt < 100) :
        basescore //= 2
    if (userb.comment_karma + userb.link_karma < 1000 or time.time() - userb.created_utc < 31556952) :
        basescore //= 2
    posts = 0
    for submission in userb.comments.new(limit=6) :
        if (int(time.time()) - submission.created_utc > 864000) :
            break
        if (submission.subreddit.display_name.lower() not in config.tradingsubs) :
            posts += 1
    if (posts < 5) :
        basescore //= 4
    a.score += basescore
    db.add(a)
    flairuser(r, a)
    if (recurse) :
        log(r, userb, usera, amt, db, False)
        
    
def decay (r: praw.Reddit, user: str, db: Database) -> None :
    """
    Trigger point decay on a user
    """
    for submission in r.redditor(user).new(limit=1) :
        if (time.time() - submission.created_utc < 259200) :
            return
        usero = db.lookup(user)
        usero.score *= .96
        db.add(usero)

def detectval (body: str) -> int :
    """
    Detect the value of a transaction given the body as a str
    """
    body = body.lower().split()
    regex = re.compile("[^a-zA-Z][$€£]?\d+[.]?\d*€?[^a-zA-Z]") #regex matches decimal numbers
    for i in range(0, len(body)) :
        word = body[i]
        if bool(regex.search(word)) :
            word = word.replace("$", "")
            word = word.replace("€", "")
            word = word.replace("£", "")
            try :
                if ("btc" in body[i+1]) :
                    return int(40000 * float(word))
                elif ("ltc" in body[i+1]) :
                    return int(150 * float(word))
                elif ("bch" in body[i+1]) :
                    return int(600 * float(word))
                elif ("eth" in body[i+1]) :
                    return int(2400 * float(word))
            except IndexError :
                return int(float(word))
    return 0

def parseparter (body: str) -> str :
    """
    Detect the trade partner given the body of the trade confirmation comment
    """
    return body.split('u/')[2].split()[0]

def monitor (monitorlist: list, r: praw.Reddit, db: Database) -> list :
    """
    Monitor a list of comments for "confirmed" replies.
    """
    for c in monitorlist :
        comment = praw.Reddit.comment(id = c)
        try :
            for message in comment.replies :
                if (message.author.name == parseparter(comment.body.lower())) :
                    message.reply("Transaction confirmed!" + config.signature)
                    value = detectval(b)
                    log(r, comment.author.name, message.author.name, value, db)
                else :
                    raise ValueError
        except ValueError :
            message.reply("Confirmation failed. Please ensurse you are the person mentioned in the parent comment.")
        continue

def flairuser (r, user: User) -> None :
    """
    Update the flair for a given user
    """
    if (user == None) :
        return
    fl = praw.models.reddit.subreddit.SubredditFlair(praw.models.Subreddit(r, display_name="cash4cash"))
    tm = ""
    tx = ""
    if (user.score < 200) :
        tx = "New Trader"
        tm = "4d6cfc5a-b4d1-11e9-942c-0e2188f2c5a2"
    elif (user.score < 1000) :
        tx = "Active Trader"
        tm = "4d6cfc5a-b4d1-11e9-942c-0e2188f2c5a2"
    elif (user.score < 2500) :
        tx = "Experienced Trader"
        tm = "07c72f9a-9a6a-11e8-b6d8-0ee58c2a0216"
    elif (user.score < 5000) :
        tx = "Veteran Trader"
        tm = "2791817c-9a6a-11e8-9aea-0ed4f48adeec"
    else :
        tx = "Top Trader"
        tm = "71d39e14-9a6a-11e8-8494-0ec3502664d4"
    if (user.status == 2 or user.status == 3) :
        tx = "Confirmed " + tx
    fl.set(user.username, tx, flair_template_id = tm)