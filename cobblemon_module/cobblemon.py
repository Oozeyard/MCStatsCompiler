import json
import os
import pandas as pd
import numpy as np
import configparser
import openpyxl
import datetime
import ftplib
import math


def loadData(csvtoggle, csvpath, useftp, ftpserver, ftppath):
    df = pd.DataFrame()
    names = pd.read_csv('../data/names.csv')
    path = 'cobblemonplayerdata'
    root_dirnames = []
    if useftp == "true":
        # Get directories (assuming they are player directories)
        root_dirnames = ftpserver.nlst(ftppath)
        ftpserver.cwd(ftppath)
        
        for dirname in root_dirnames:
            if dirname[-1] == ".":
                continue
            # Go to the subfolder
            ftpserver.cwd(dirname.split("/")[-1])
            filenames = ftpserver.nlst()
            
            for filename in filenames:
                if filename == "." or filename == "..":
                    continue
                print("Now processing", filename)
                
                # Download the file to process
                local_file = f"temp_{filename}"
                with open(local_file, "wb") as file:
                    ftpserver.retrbinary(f"RETR {filename}", file.write)
                
                with open(local_file, "r") as file:
                    data = json.load(file)['extraData']['cobbledex_discovery']['registers']
                
                os.remove(local_file)
                
                temp_df = pd.json_normalize(data, meta_prefix=True)
                temp_name = names.loc[names['uuid'] == filename[:-5]]['name']
                temp_df = temp_df.transpose().iloc[1:].rename({0: temp_name.iloc[0]}, axis=1)
                
                if not temp_df.empty:
                    temp_df.index = temp_df.index.str.split('.', expand=True)
                    if df.empty:
                        df = temp_df
                    else:
                        df = df.join(temp_df, how="outer")
                else:
                    df[temp_name] = np.nan
                
            ftpserver.cwd("../")  # Move back to the parent directory
    else:
        i = -1
        for dirpath, dirnames, filenames in os.walk(path):
            if len(dirnames) > 0:
                root_dirnames = dirnames
            for filename in filenames:
                if filename == ".gitignore":
                    continue
                print("Now processing", filename)
                file = open(path + '/' + root_dirnames[i] + '/' + filename)
                data = json.load(file)['extraData']['cobbledex_discovery']['registers']
                # Import the JSON to a Pandas DF
                temp_df = pd.json_normalize(data, meta_prefix=True)
                temp_name = names.loc[names['uuid'] == filename[:-5]]['name']
                temp_df = temp_df.transpose().iloc[1:].rename({0: temp_name.iloc[0]}, axis=1)
                # Split the index (stats.blabla.blabla) into 3 indexes (stats, blabla, blabla)
                if not temp_df.empty:
                    temp_df.index = temp_df.index.str.split('.', expand=True)
                    if df.empty:
                        df = temp_df
                    else:
                        df = df.join(temp_df, how="outer")
                else:
                    df[temp_name] = np.nan
            i += 1
        # Replace missing values by 0 (the stat has simply not been initialized because the associated action was not performed)
        df = df.fillna(0)
        if csvtoggle == "true":
            df.to_csv(csvpath)
    return df


def most_pokemons_leaderboard(df, config):
    # Load the Excel file
    file_path = "output.xlsx"

    # This first leaderboard might be removed in the future
    sheet_name = "leaderboard1"
    wb = openpyxl.load_workbook(file_path)
    ws = wb[sheet_name]
    i = 0
    for index, row in df[0:10].iterrows():
        ws.cell(row=i+3, column=3, value=index)
        ws.cell(row=i+3, column=4, value=row[0])
        i += 1
    now = datetime.datetime.now()
    ws.cell(row=13, column=2, value="Dernière update le "+now.strftime("%d.%m.%y à %H:%M"))
    
    sheet_name = "leaderboard2"
    ws = wb[sheet_name]
    i = 0
    ExcelRows = int(config['LEADERBOARD']['ExcelRows'])
    ExcelCols = int(config['LEADERBOARD']['ExcelColumns'])
    for index, row in df[0:ExcelRows*ExcelCols].iterrows():
        ws.cell(row=(i%ExcelRows)+3, column=3+math.floor(i/ExcelRows)*3, value=index)
        ws.cell(row=(i%ExcelRows)+3, column=4+math.floor(i/ExcelRows)*3, value=row[0])
        i += 1
    now = datetime.datetime.now()
    ws.cell(row=ExcelRows+3, column=2, value="Dernière update le "+now.strftime("%d.%m.%y à %H:%M"))
    ws.cell(row=ExcelRows+4, column=2, value=config['LEADERBOARD']['Subtitle'])
    wb.save(file_path)


# Read config
config = configparser.ConfigParser()
config.read('cobblemon_config.ini')

# Connect to FTP if activated
ftp_server = None
if config['FTP']['UseFTP'] == "true":
    ftp_server = ftplib.FTP(config['FTP']['Host'], open("../username.txt", "r").read(), open("../password.txt", "r").read())
    ftp_server.encoding = "utf-8"

# Load the data
# To get: table with columns for players and rows for pokemons
df = loadData(config['GLOBALMATRIX']['CreateCSV'], config['GLOBALMATRIX']['CSVPath'], config['FTP']['UseFTP'], ftp_server, config['FTP']['Path'])
count_df = df.drop(['caughtTimestamp', 'discoveredTimestamp', 'isShiny'], level=2)
print(count_df)
count_df['times_caught'] = count_df.apply(lambda row: (row == "CAUGHT").sum(), axis=1)
print(count_df['times_caught'].sort_values().to_string())
count_df.drop('times_caught', axis=1, inplace=True)
player_sum = pd.DataFrame((count_df == "CAUGHT").sum().sort_values())
player_sum['index'] = range(len(player_sum), 0, -1)
player_sum = player_sum.iloc[::-1]
player_sum.drop(config['LEADERBOARD']['IgnoreNames'].split(","), inplace=True)
print(player_sum)
most_pokemons_leaderboard(player_sum.iloc, config)


# Close the Connection
if config['FTP']['UseFTP'] == "true":
    ftp_server.quit()