import sqlite3
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ============ note: only works for the author (my auth tokens). You have to know a bit about Google Sheets API and my Scorekeeper code to make it work for you =====

def loadtosheets():
    # Path to your SQLite database
    db_path = 'tos2.db'

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)

    # Query the SQLite table and load it into a DataFrame
    df = pd.read_sql_query("SELECT * FROM entries", conn)

    # Close the connection
    conn.close()

    # Google Sheets authentication
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('./western-rider-428117-r8-d303a3d16f0b.json', scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet (by name or key)
    sheet = client.open("ToS2 Scorekeeper").sheet1

    # Clear the existing sheet (if needed)
    sheet.clear()

    # Upload DataFrame to Google Sheets
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

if __name__ == '__main__':
    loadtosheets()