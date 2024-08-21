import pandas as pd
from pathlib import Path
from my_functions_tracking_Euro import skillcorner_funcs,classifier,tracking_resolve

matches = pd.read_csv("matches.csv")

for i, row in matches.iterrows():

    game = row["home"] + " - " + row["away"]
    match_id = row["match_id"]
    lineup_df = pd.read_csv(f'lineups/lineup_{match_id}.csv')
    df_events =  pd.read_csv(f'Wyscout_processing/generated_files/{game}.csv')
    export_cols = ['Spiel','Torhüter','Team','Periode',"matchTimestamp",'Minute','Sekunden','Zeitperiode','Standard','Seite_Standard','Spielsituation','Zuspiel_Zone',"Abschluss/Klärungs Art",'Outcome','direkt_indirekt', "Entscheid",'location.x', 'location.y','attacking_team','x_start','y_start','x_avg','y_avg']

    ball_id = -1

    df = pd.read_csv(f"euro2024/{match_id}/tracking.csv")
    df = tracking_resolve.addTeam(df, lineup_df)
    df = tracking_resolve.multiply_if_half_is_two(df)
    df = tracking_resolve.adjust_timestamps(df)

    df_ball = df[df.object_id==ball_id]

    first_25_rows = df[df.half=="One"].head(25)
    min_index = first_25_rows['x'].idxmin()
    left_to_right = first_25_rows.loc[min_index]["object_id"]
    name_left_to_right = lineup_df[lineup_df.player_id == left_to_right]["team_name"].iloc[0]

    max_index = first_25_rows['x'].idxmax()
    right_to_left = first_25_rows.loc[max_index]["object_id"]
    name_right_to_left = lineup_df[lineup_df.player_id == right_to_left]["team_name"].iloc[0]

    metadata_df = pd.DataFrame({
        '1H': [name_right_to_left],
        '2H': [name_left_to_right],
        '1E': [name_right_to_left],
        '2E': [name_left_to_right],
    })

    goalkeeper_df = pd.DataFrame({
        f'{name_right_to_left}': [right_to_left],
        f'{name_left_to_right}': [left_to_right],
    })

    df_events.assign(Entscheid="")

    df_events.assign(Entscheid="",x_start=0,y_start=0,x_avg=0,y_avg=0)


    df_events = classifier.classify(df_events,goalkeeper_df,metadata_df,df,df_ball)
    df_events.to_csv(f'generated_decision/{game}.csv', columns= export_cols,index=False) 
