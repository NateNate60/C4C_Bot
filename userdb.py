"""
Contains the framework for interacting with the SQLite database
"""

from dataclasses import dataclass
import sqlite3
import time

def string (a) -> str :
    if (a == None) :
        return "NULL"
    else :
        return str(a)

@dataclass
class User :
    """
    Struct representing a user. This is distinct from reddit.Redditor.
    """
    username: str
    score: int
    realname: str
    address: str
    realid: str
    status: int
    last: int
    def __init__ (self, username: str, score: int, realname: str = None, address: str = None, realid: str = None, status: int = 1, last: int = 0) :
        self.username = username
        self.score = score
        self.realname = realname
        self.address = address
        self.realid = realid
        self.status = status
        self.last = last



class Database :
    """
    Class representing the SQLite3 database connection
    """
    def __init__ (self) :
        self.db = sqlite3.connect("database.sqlite3")
        with self.db :
            self.db.execute("CREATE TABLE IF NOT EXISTS users (" +
                            "username TEXT NOT NULL PRIMARY KEY," +
                            "score INTEGER NOT NULL," + #score is stored in decipoints
                            "realname TEXT," +
                            "address TEXT," +
                            "realid TEXT," +
                            "status INTEGER NOT NULL," +
                            "last INTEGER NOT NULL," +
                            "txcount INTEGER);") #last modified time, in UNIX
                            #Statuses:
                            # 1: unverified
                            # 2: id verified
                            # 3: trade verified
                            # -1: under investigation, unverified
                            # -2: under investigation, id verified
                            # -3: unver investigation, trade verified

            self.db.commit()
    
    def lookup (self, username: str) -> User :
        """
        Look up a user by their username
        """
        with self.db :
            cursor = self.db.execute("SELECT * FROM users WHERE username=?;", (username,))
            rows = cursor.fetchall()
            if (len(rows) == 0) :
                return None
            print(rows[0])
            user = User(rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4], rows[0][5])
            return user
    
    def edit (self, username: str, decipoints: int = 0) :
        """
        Add or subtract decipoints from a user's score.
        Returns their new score.
        """
        with self.db :
            self.db.execute("UPDATE users SET score = score + ? WHERE username = ?", (decipoints, username,))
            user = self.lookup(username)
            self.db.commit()
            return user.score

    
    def add (self, user: User) :
        """
        Add (or update) a user in the database
        """

        with self.db :
            if (user.last == 0) :
                user.last = int(time.time())
            if (self.lookup(user.username) == None) :
                self.db.execute("INSERT INTO users VALUES (\"" + user.username.lower() + "\"," + str(user.score) + ",\"" + string(user.realname) + '\",\"' + string(user.address) + '\",\"' + string(user.realid) + '\",' + str(user.status) + ', ' + string(user.last) + ', 0);')
            else :
                self.db.execute("UPDATE users SET score=" + str(user.score) + ",realname=\"" + string(user.realname) + '\",address=\"' + string(user.address) + '\",realid=\"' + string(user.realid) + '\",status=' + str(user.status) + ',last=' + string(user.last) + ', txcount=txcount+1 WHERE username=?;', (user.username.lower(),))
            self.db.commit()
    