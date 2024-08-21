import pandas as pd
from my_functions import wyscout_to_df, goalkeeper,positionFuncs

matches = pd.read_csv("matches.csv")

for i, row in matches.iterrows():

    
    name = row["home"] + " - " + row["away"]
    key = row["match_id_wyscout"]
    print(name)

    base_path = "wyscout" #where json file lies
    file_name = f"{key}/events.json" #name of our json file
    export_cols = ["game","Goalkeeper","team.name","matchPeriod","Ball_erhalten_min","Ball_erhalten_s","minute","second","Zuspielzone","Passzone","Spielsituation","location.x","location.y","pass.endLocation.x","pass.endLocation.y","pass.accurate","pass.length","type.secondary"]
    rename = {"minute":"Minute","second":"Sekunden","matchPeriod":"Periode","Goalkeeper":"Torhüter","team.name":"Team"}

    df_events = wyscout_to_df.wyscout_json_to_df(file_name,base_path)
    df_events["location.x"] = 100 - df_events["location.x"] 
    df_events = df_events.assign(game = name)
    export_string = '../generated_files_offensive/' + name +"_Offensive"+ '.csv'

    df_goalkeeper = df_events[(df_events["player.position"]=="GK")]
    df_clearance = df_goalkeeper[(df_goalkeeper["type.primary"]=="clearance")].assign(Spielsituation="Ball geklärt")
    df_recipient = df_events[(df_events["pass.recipient.position"]=="GK")].assign(Spielsituation="Ball erhalten")

    
    all_actions = goalkeeper.actions(df_goalkeeper)
    GK_ids = goalkeeper.names(df_events)

    frame_merged_save,to_del = goalkeeper.merge_save(all_actions)
    frame_filtered = frame_merged_save[~frame_merged_save['id'].isin(to_del)]

    df_all = pd.concat([frame_filtered,df_recipient,df_clearance]).sort_values(by=["matchPeriod","matchTimestamp"]).assign(Ball_erhalten_min="",Ball_erhalten_s="")

    frame_merged_recieve,to_del_rec = goalkeeper.merge_recieve(df_all)
    frame_filtered_final = frame_merged_recieve[~frame_merged_recieve['id'].isin(to_del_rec)].assign(Goalkeeper="")

    df_filtered_names = positionFuncs.time(goalkeeper.goalkeeperName(frame_filtered_final,GK_ids))

    df_pass_resolved = goalkeeper.pass_zone(df_filtered_names)
    df_final= goalkeeper.resolve(df_pass_resolved[export_cols],df_events).rename(columns=rename)
    df_final = df_final.sort_values(by=['Team','Periode'])


    df_final["location.x"] = 100 - df_final["location.x"] 
    df_final.to_csv(export_string, mode = 'w', index=False)#export