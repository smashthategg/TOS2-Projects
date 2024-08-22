import os
import sqlite3
import re

# ========= if you're an outside user, just change these paths to whatever works for you ==========
# ========= note: only useful if you have at least minimal knowledge of sqlite ====================
directory_path = r"C:\Program Files (x86)\Steam\steamapps\common\Town of Salem 2\SalemModLoader\ModFolders\Scorekeeper"
archive_path = r"C:\Users\jzlin\OneDrive\Documents\ToS2 Projects\Scorekeeper\archived_results"

def saveresults(directory_path, archive_path):

    # Connect (create if not exists) to database
    db_file = 'tos2.db'
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS players
                    (accountName TEXT PRIMARY KEY,
                    discordName TEXT
                   )''')
    
    # For clarity, 'won' and 'alive' are meant to be booleans designated by 0 or 1.
    cursor.execute('''CREATE TABLE IF NOT EXISTS entries
                    (gameName TEXT,
                    accountName TEXT,
                    originalRole TEXT,
                    won INTEGER,
                    alive INTEGER,
                    FOREIGN KEY(accountName) REFERENCES players(accountName)
                    )''')
    
    # Get a list of all files in the directory
    files = os.listdir(directory_path)
    
    for filename in files:
        # Check if the file is a text file
        print(filename)
        if filename.endswith(".txt"):
            filepath = os.path.join(directory_path, filename)
            destpath = os.path.join(archive_path, filename)
            # Open and read the file
            with open(filepath, 'r') as file:
                # Generate an array containing each line of text in the file
                content = file.read()
                lines = content.split('\n')
                for line in lines: # formatted by "gameName (accountName) originalRole won alive"
                    match = re.match(r"(.+?) \((.+?)\) (.+?) ([WL]) ([AD])", line)
                    if match:
                        game_name, account_name, original_role, won, alive = match.groups()
                        while not game_name[0].isalpha():
                            game_name = game_name[1:]
                        won = 1 if won == 'W' else 0
                        alive = 1 if alive == 'A' else 0

                        # Add the player to the 'players' table
                        cursor.execute('''INSERT OR IGNORE INTO players (accountName)
                                        VALUES (?)''', (account_name,))

                        # Add the entry to the 'entries' table
                        cursor.execute('''INSERT INTO entries (gameName, accountName, originalRole, won, alive)
                                        VALUES (?, ?, ?, ?, ?)''', (game_name, account_name, original_role, won, alive))

                        # Commit the changes to the database
                        conn.commit()

            # Remove and archive the txt file        
            os.remove(filepath)
            with open(destpath, 'w') as afile:
                afile.write(content)

    conn.close()
            

                
                    



if __name__ == '__main__':
    saveresults(directory_path, archive_path)