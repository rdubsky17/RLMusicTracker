import pandas as pd
from datetime import datetime, timedelta
import glob
import os, sys

def get_runtime_path(filename_or_folder):
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), filename_or_folder)
    return os.path.abspath(filename_or_folder)

GAMESTATS_PATH = "GameStats"



pd.set_option('display.max_colwidth', None)
def getStats(_playerName):
    file_pattern = os.path.join(get_runtime_path(GAMESTATS_PATH), "*.csv")
    csv_files = glob.glob(file_pattern)
    print("CSV files found:", csv_files)
    dataframeList = []

    for file in csv_files:
        df = pd.read_csv(file)
        df['source_file'] = file

        team_scores = df.groupby(["Timestamp", "TeamName"])["Goals"].sum().reset_index()
        winning_teams = team_scores.loc[team_scores.groupby("Timestamp")["Goals"].idxmax()]
        winning_teams = winning_teams[["Timestamp", "TeamName"]].rename(columns={"TeamName": "WinningTeam"})
        df = df.merge(winning_teams, on="Timestamp", how="left")
        df.loc[(df["TeamName"] == df["WinningTeam"]), "Wins"] = 1

        dataframeList.append(df)

    gamestats_df = pd.concat(dataframeList)
    goku_stats = gamestats_df[gamestats_df['PlayerName'] == _playerName]
    gamestats_df = goku_stats
    #gamestats_df.to_csv("gamestats.csv")


    spotify_df = pd.read_csv(get_runtime_path("spotify_log.csv"))
    spotify_df['Timestamp'] = pd.to_datetime(spotify_df['Timestamp'])
    gamestats_df['Timestamp'] = gamestats_df['Timestamp'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d_%H-%M-%S'))
    
    unique_games = gamestats_df['Timestamp'].drop_duplicates().sort_values()


    game_duration = timedelta(minutes=7)
    game_windows = [(end - game_duration, end) for end in unique_games]

    def match_game(song_time, windows):
        for game_start, game_end in windows:
            if game_start <= song_time <= game_end + timedelta(minutes=1):
                return game_end
        return None

    spotify_df['GameEnd'] = spotify_df['Timestamp'].apply(lambda ts: match_game(ts, game_windows)) # adds song to game if song lands in game time-frame. Future additions to ensure no duplicates in consecutive games.
    spotify_df = spotify_df.dropna(subset=['GameEnd']) # Deletes all non-matching songs


    #spotify_df.to_csv("completelog.csv", index=False) # All songs that played during rl

    gamestats_df['Timestamp'] = pd.to_datetime(gamestats_df['Timestamp'], format='%Y-%m-%d %H:%M:%S')
    spotify_df['GameEnd'] = pd.to_datetime(spotify_df['GameEnd'], format='%Y-%m-%d %H:%M:%S')



    combined_df = pd.merge(
        gamestats_df,
        spotify_df,
        how='right',          
        left_on='Timestamp',
        right_on='GameEnd',
        suffixes=('_game', '_spotify')
    )


    #combined_df.to_csv('combined.csv', index=False)

    columns_to_keep = ['GameEnd', 'PlayerName', 'Score', 'Goals', 'Assists', 'Saves', 'Shots', 'Demolishes', 'BoostUsage', 'PossessionTime', 'Artist', 'Track', 'Wins']
    combinedandrefined_df = combined_df[columns_to_keep].copy()
    #combinedandrefined_df.to_csv('combinedandrefined.csv', index=False)


    combinedandrefined_df['Count'] = 1

    combinedandrefined_df['PossessionTime'] = pd.to_timedelta("0:" + combinedandrefined_df['PossessionTime'])
    numeric_cols = ['Score', 'Goals', 'Assists', 'Saves', 'Shots', 'Demolishes', 'BoostUsage', 'PossessionTime', 'Wins', 'Count']
    # superstats = combinedandrefined_df.groupby(['Artist', 'Track'], as_index=False)[numeric_cols].sum()
    
    # superstats['Score_Average'] = superstats['Score'] / superstats['Count']
    # superstats['Goals_Average'] = superstats['Goals'] / superstats['Count']
    # superstats['Wins_Average'] = superstats['Wins'] / superstats['Count']
    # superstats['Saves_Average'] = superstats['Saves'] / superstats['Count']
    # superstats['Shots_Average'] = superstats['Shots'] / superstats['Count']
    # superstats['Assists_Average'] = superstats['Assists'] / superstats['Count']
    # superstats['Demoloshes_Average'] = superstats['Demolishes'] / superstats['Count']
    # superstats['BoostUsage_Average'] = superstats['BoostUsage'] / superstats['Count']
    # superstats['PossessionTime_Average'] = superstats['PossessionTime'] / superstats['Count']
    # # sorted_df = superstats.sort_values(by='Goal_Average', ascending= False)
    # superstats.to_csv("AllSongsAndStats.csv", index=False)
    return combinedandrefined_df

if __name__ == '__main__':
    df = getStats("Goku SSJGSS")
    print(getStats("Goku SSJGSS"))
    #sorted_df = df.sort_values(by=['Goal_Average', 'Count'], ascending= [False, False])
    #sorted_df.to_csv('sortedstats.csv', index=False)
    
