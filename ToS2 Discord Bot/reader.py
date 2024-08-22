import sqlite3
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Path to your service account key file
SERVICE_ACCOUNT_FILE = './western-rider-428117-r8-d303a3d16f0b.json'

# Scopes required for the Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# Google Sheets ID and range
SPREADSHEET_ID = '1IwhWyb4Ms0tuIBsWVI2ry2NiMj5CklJBR7d4NjUXAu4'
RANGE_NAME = 'ToS2 Leaderboard Update Form!A2:H'

if __name__ == '__main__':
    # Authenticate and construct the service
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=RANGE_NAME).execute()
    values = result.get('values', [])


    # Connect (create if not exists) to database
    db_file = 'leaderboard.db'
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS leaderboard
                    (name TEXT PRIMARY KEY,
                    ingame TEXT,
                    elo INTEGER,
                    peak INTEGER,
                    wins INTEGER,
                    losses INTEGER,
                    draws INTEGER,
                    date TEXT
                    )''')

    # Add/update entries to database
    if not values:
        print('No data found.')
    else:
        for row in values:
            print("Attempting " + str(row))
            if len(row) == 8: # If the "approved" column has been marked for an entry, we add this entry to the leaderboard
                print("Added " + str(row))
                name = row[1].lower()
                ingame = row[2]
                elo = int(row[3])
                wld = [int(num) for num in row[4].split('/')]
                date = row[0]

                cursor.execute('''
                                INSERT INTO leaderboard (name, ingame, elo, peak, wins, losses, draws, date) 
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                ON CONFLICT(name)
                                DO UPDATE SET
                                    ingame = excluded.ingame,
                                    elo = excluded.elo,
                                    wins = excluded.wins,
                                    losses = excluded.losses,
                                    draws = excluded.draws,
                                    date = excluded.date,
                                    peak = CASE
                                        WHEN excluded.peak > leaderboard.peak THEN excluded.peak
                                        ELSE leaderboard.peak
                                    END
                                ''', (name, ingame, elo, elo, wld[0], wld[1], wld[2], date))

    # Commit changes and close the database
    conn.commit()
    conn.close()



