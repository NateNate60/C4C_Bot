from prawcore import exceptions
from helpers import readchecked, writechecked
import actions
import config
import userdb
import time

def main() :
    try :
        db = userdb.Database()
        r = actions.logon()
        while (True) :
            checked = readchecked()
            for message in r.inbox.unread() :
                b = message.body.lower()
                if ('u/c4c_bot' in b) :
                    partner = actions.parseparter(b)
                    message.reply("PENDING CONFIRMATION\n\nWaiting for u/" +  partner + " to confirm the trade.\n\n**Note:** The flairing system has changed. You must reply to **this comment** to confirm! **If you reply to the parent comment your confirmation will not be detected." + config.signature)
                    message.mark_read()
                if ("confirm" in b and "not" not in b) :
                    try :
                        parent = message.parent().parent()
                        if ("This transaction has been confirmed" in message.parent().body) :
                            continue
                        if (message.author.name.lower() == actions.parseparter(parent.body.lower())) :
                            parent.edit("This transaction has been confirmed" + config.signature)
                            value = actions.detectval(parent.body)
                            points = actions.log(r, parent.author, message.author, value, db)
                            message.reply("Transaction confirmed!\n\nPoints awarded:\n\n- u/" + parent.author.name + ": " + str(points[0]) +  " points\n- u/" + message.author.name + ": " + str(points[1]) + " points" + config.signature)
                        else :
                            raise ValueError
                    except ValueError :
                        message.reply("Confirmation failed. Please ensurse you are the person mentioned in the parent comment.")
                    message.mark_read()
            for post in r.subreddit("cash4cash").new(limit=5) :
                if (post.id in checked) :
                    continue
                author = db.lookup(post.author.name.lower())
                message = "#OP's Cash4Cash Trust Score: " + str(author.score) + '\n\n'
                if (author.score < 200) :
                    message += "Note: This user's trust score is low. It's highly recommended to use the escrow when trading, since a large portion of scams target or are perpetrated by such users.\n\n"
                
                message += "➤ Automated escrow service: Don't like the uncertainty of going first? Want to make sure the other party doesn't take your money and disappear? Our escrow service can help with that. [Click here to start a new escrow transaction with this user.](https://www.reddit.com/message/compose?to=" + post.author.name + "&subject=Escrow&message=--NEW TRANSACTION--%0APartner%3A {{author}}%0AAmount%3A 0.12345 BTC%2FBCH%0A--CONTRACT--%0AWrite whatever you want here. What are the parties agreeing to%3F%0AAbout this service%3A https%3A%2F%2Fwww.reddit.com%2Fr%2FCash4Cash%2Fwiki%2Fedit%2Findex%2Fescrow)  ([about](https://reddit.com/r/Cash4Cash/wiki/index/escrow))\n\n"
                message += "➤ Trade safely! **Scammers will contact you via PM & reddit chat**: they may pretend to be experienced traders with fake rep pages, or pose as the person you're negotiating with. It falls on you to do your own due diligence.\n\n"
                message += "➤ Please **[read all of our rules](https://www.reddit.com/r/Cash4Cash/wiki/index)**. We require any user to comment on your post first before contacting you. It's one of the easiest ways to check for a scam. If someone won't comment on your post **DO NOT WORK WITH THEM** and report them to moderators.\n\n"
                message += "➤ For your convenience, upon conclusion of this trade please post a `!closed` comment"
                post.reply(message).mod.distinguish(sticky="yes")
                checked.append(post.id)
            writechecked(checked)
    except exceptions.ServerError :
        time.sleep(5)
        main()


if __name__ == '__main__' :
    main()
