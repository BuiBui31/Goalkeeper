def multiply_if_half_is_two(df):
    condition = df['half'] == "Two"
    df.loc[condition, ['x', 'y']] *= -1
    condition = df['half'] == "Four"
    df.loc[condition, ['x', 'y']] *= -1
    return df

def adjust_timestamps(df):
    min_timestamps = df.groupby('half')['timestamp'].min().to_dict()
    print(min_timestamps)
    df['timestamp'] = df.apply(lambda row: row['timestamp'] - min_timestamps[row['half']], axis=1)
    return df

def addTeam(df,lineup):

    player_team_dict = {}
    for i,row in lineup.iterrows():
        
        player_id = row['player_id']
        team_name = row['team_name']
        player_team_dict[player_id] = team_name


    def map_team(object_id):
        return player_team_dict.get(object_id, "referee/ball")

    df['team'] = df['object_id'].apply(map_team)
    
    return df 