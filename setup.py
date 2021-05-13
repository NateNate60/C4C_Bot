
def main() :
    print ("--NateNate60's Ban Propagator setup--")
    try:
        import sys
        import subprocess
        import os
        import shutil
    except ModuleNotFoundError:
        print ("You are missing required system packages. Setup cannot install automatically.")
        print ("This may be due to a corrupt or inadequate Python installation")
        print ("You can still install manually.")
        return 1
    try:
        import praw
    except ModuleNotFoundError:
        print ("It appears that the Python Reddit API Wrapper is not installed on your system.")
        print ("Setup can automatically install PRAW for you.")
        ok = input("Would you like to automatically install PRAW? (y/n): ")
        if "y" in ok :
            if "win" in sys.platform :
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'praw'])
            else :
                subprocess.check_call([sys.executable, '-m', 'pip3', 'install', 'praw'])
        else :
            print ("Installation aborted")
            return 1
    path = ''
    while True :
        path = input("Enter the path to the directory you'd like to install the files in (press enter to install in current directory): ")
        if path == "" :
            path = "."
        if path[0] == "~" :
            path = path [1:]
            path = os.path.expanduser('~') + path
        path = os.path.realpath(path)
        print("WillardPointsBot will be installed in", path)
        ok = input("Is this correct? (y/n): ")
        if 'y' in ok or ok == '':
            break
    try:
        os.mkdir(path)
    except FileExistsError:
        print ("WARNING: folder already exists and might not be empty!")
        input ("Press enter to continue, or press Control + C to quit")
    with open (path + '/config.py', 'w') as f:
        mainsub = input ("Enter the main subreddit name (where bans will be copied from): ")
        altsub = input ("Enter the secondary subreddit name )where bans will be copied to): ")
        w = "#Main subreddit name\nmain=" + mainsub + "\n\n#Secondary subreddit name\nsecond=" + altsub
        f.write(w)
    with open (path + "/authentication.py", 'w') as f:
        print("You'll now be asked for the credentials of the Reddit account that you want the bot to use.")
        print("You must obtain Reddit API keys first. You can obtain API keys at https://www.reddit.com/prefs/apps/")
        while True :
            username = input("Enter your Reddit username: ")
            password = input("Enter your Reddit password: ")
            client_id = input("Enter your API client ID: ")
            client_secret = input("Enter your API client secret: ")
            print("Verifying credentials...")
            f.write("username=" + username + '\npassword=' + password + '\nclient_id=' + client_id + '\nclient_secret=' + client_secret)
            try :
                r = praw.Reddit(username=username,
                        password=password,
                        client_id=client_id,
                        client_secret=client_secret,
                        user_agent="C4Csetup")
                print ("Authentication successful")
                break
            except Exception :
                print ("An error occured during login. Your credentials may be incorrect.")
                if "y" in input("Would you like to try again? If no, then you will have to set this up manually later. (y/n) ") :
                    continue
                print ("You can input the authentication information in " + path + "/authentication.py")
                break
    print ("Copying files...")
    shutil.copyfile("./actions.py", path + '/actions.py')
    shutil.copyfile("./main.py", path + '/main.py')
    print ("Installation complete!")
    print ("Simply run " + path + "/main.py to propagate bans. The bot checks every minute for new banned users.")
    return 0
if __name__ == '__main__' :
    main()