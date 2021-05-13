import actions
import time

def main() :
    while (True) :
        r = actions.logon()
        l = actions.getUSL(r)
        actions.banc4crep(r, l)
        print ("Sleeping...")
        time.sleep(60)

if __name__ == '__main__' :
    main()