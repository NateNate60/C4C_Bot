import actions
import config
import userdb
import time

def main() :
    db = userdb.Database()
    r = actions.logon()
    while (True) :
        for message in r.inbox.unread() :
            b = message.body.lower()
            if ('u/c4c_bot' in b) :
                partner = actions.parseparter(b)
                message.reply("PENDING CONFIRMATION\n\nWaiting for u/" +  partner + " to confirm the trade.\n\n**Note:** The flairing system has changed. You must reply to **this comment** to confirm! **If you reply to the parent comment your confirmation will not be detected." + config.signature)
                message.mark_read()
            if ("confirm" in b and "not" not in b) :
                try :
                    parent = message.parent().parent()
                    if (message.author.name.lower() == actions.parseparter(parent.body.lower())) :
                        message.reply("Transaction confirmed!" + config.signature)
                        value = actions.detectval(parent.body)
                        actions.log(r, parent.author, message.author, value, db)
                    else :
                        raise ValueError
                except ValueError :
                    message.reply("Confirmation failed. Please ensurse you are the person mentioned in the parent comment.")
                message.mark_read()


if __name__ == '__main__' :
    main()