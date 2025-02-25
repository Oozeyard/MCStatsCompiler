
# MCStatsCompiler

This project aims at taking a bunch of stats data file generated from Minecraft players and outputing nicely formatted statistics.

## Disclaimer

This was coded for my own use originally, but I've decided to share it in case it can be useful to someone else. It is still work in progress, and requires some knowledge of Python.

The script is intended to be executed on your own computer and not on a server. It could be executed on a server, but it probably requires a little adaptation.


## Modules
For now, there are 2 modules in this project:

### Main module
This module takes vanilla stats files (json format) that can be found in the folder "stats". It has currently 2 features: 
- A leaderboard (console printed-only for now) of the desired statistic. For example, `minecraft:play_time` for the play time of each player.
- A "best-and-worst" (console printed-only for now) for the desired player. This gives the position of the player in each of the leaderboards of individual stats.

### Cobblemon module
This module takes statistics files generated by the Cobblemon mod (json format) that can be found in the folder "cobblemonplayerdata". It has currently 3 (related) features:
- A leaderboard of the players who caught the most Cobblemons. The leaderboard is output on an Excel sheet.
- Same for the most Shiny Cobblemons. The leaderboard is output on the same Excel sheet.
- Same for the most Legendary Cobblemons. The leaderboard is output on the same Excel sheet.


## Running the scripts

### 1. Installation
In order to run the scripts, start by downloading this repo. You need a valid installation of Python, as well as the required libraries. Here are the libraries used by the modules that are not installed by default with Python:
- Main module: pandas, configparser
- Cobblemon module: pandas, numpy, configparser, openpyxl, paramiko

### 2. Edit the config
All modules have an associated config, named something like **[module]_config.ini**.
Read it, and if needed, edit it based on what you want.

### 3. Update usercache.json
All of your data files should be named [uuid].json, where [uuid] is the Minecraft UUID of the player. In order to work with the usernames of the players instead, you need to update the file **data/usercache.json**. Simply download it from your server (it should be at the root folder) and put it there. If you use the FTP setting (see below), the script will go and file the file for you (no need to update it manually then).

### 4. Input files 
You have the choice between 2 options to input your JSON data files: local files or FTP:
- Drop them in the appropriate folder (**stats** for main module, **cobblemonplayerdata** for cobblemon module. On your Minecraft server, both folders should be located in the "world" folder). Set UseFTP to false in the config to use those local files (it should be by default on false, so if you haven't changed it you're good to go).
- If you want to get your files directly from a FTP server, follow the related instructions in the config file. Basically, you need to create a file for the username, a file for the password, and change the relevant settings in the config and it should work. You also now have the option to use an SFTP instead of an FTP connection.

### (Cobblemon module only) 5a. Prepare output.xlsx
If you intend on using the leaderboard feature of the Cobblemon module, you need to prepare the **output.xlsx** file. Simply adapt the table to your desired number of players (for example, if you expect 20 players, you can for example have a 5x4 table or a 10x2 table). You can also change the title, the colors and other formatting elements. Just make sure to keep 3 Excel columns per leaderboard column, and start it in the cell B3 (see example in the image below).

Don't forget to adapt the config file to your changes, especially the number of rows and columns if you have changed them! The subtitles of the table can also be configured there.

![Cobblemon example](images/cobblemon_example.PNG)

### (Cobblemon module only) 5b. Prepare Pokemon.csv
If you intend on using the "Most Legendary Cobblemons" Leaderboard (which is disabled by default), you can edit **Pokemon.csv**. This is not needed, but if you want to change which pokémons are considered as legendary for the leaderboard, it is done there.

### 6. Run the script
You can now run the script of the module with your Python installation.
- For the main module: run **main_module/main.py**
- For the cobblemon module: run **cobblemon_module/cobblemon.py**

### Frequent problems
1. This script uses local paths, so make sure that you are executing the Python script from the folder! If you get errors related json files, it's probably that the script couldn't fint it.
2. The Cobblemon leaderboard feature only produces the XLSX table. To display an image in-game, you still need to convert the table to an image and then upload it somewhere. Feel free to contact me if you need help or tips with that.