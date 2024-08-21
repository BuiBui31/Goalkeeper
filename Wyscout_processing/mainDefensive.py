import pandas as pd
from my_functions import backwardPass, corner, cross, deepBall, freekicks, positionFuncs, wyscout_to_df, shotsFunc, interception, penalty, merge, goalkeeper

matches = pd.read_csv("matches.csv")

for i, row in matches.iterrows():
 
    name = row["home"] + " - " + row["away"]
    key = row["match_id_wyscout"]
    print(name)
    

    base_path = "wyscout" #where json file lies
    file_name = f"{key}/events.json" #name of our json file
    rename = {"minute":"Minute","second":"Sekunden","matchPeriod":"Periode","shot.goalkeeper.name":"Torhüter","team.name":"Team","shot.bodyPart":"Abschluss/Klärungs Art"}
    export_cols = ['Spiel','Torhüter','Team','Periode',"matchTimestamp","videoTimestamp","stop",'Minute','Sekunden','Zeitperiode','Standard','Seite_Standard','Spielsituation','Zuspiel_Zone',"Abschluss/Klärungs Art",'Outcome','direkt_indirekt', 'location.x', 'location.y','attacking_team']

    df_events = wyscout_to_df.wyscout_json_to_df(file_name,base_path)

    df_events = df_events.assign(Outcome="",Zuspiel_Zone="",Seite_Standard="")


    GK_ids = goalkeeper.names(df_events)

    deep_pass = positionFuncs.zoning_helper(deepBall.deepBall(df_events))
    df_corner_final = corner.corner(df_events)
    df_backwardpass_final,ids = backwardPass.backwardPass(df_events)
    if(len(df_backwardpass_final) != 0):
        df_backwardpass_final= positionFuncs.zoning_helper(df_backwardpass_final)
        
    df_cross_final = positionFuncs.zoning_helper(cross.cross(df_events,ids))
    df_freekicks_direct,df_freekicks_indirect = freekicks.freekicks(df_events)
    df_shots_final = positionFuncs.shot_zoning(shotsFunc.shots(df_events),df_events)
    df_penalty = penalty.penalty(df_events)
    df_freekicks_indirect = positionFuncs.zoning_helper(df_freekicks_indirect)

    all_cross = interception.goalkeeperInter(df_cross_final,df_corner_final,df_freekicks_indirect,df_backwardpass_final,GK_ids)

    all_shots = shotsFunc.bodypart(positionFuncs.zone_classification(shotsFunc.outcome(pd.concat([df_shots_final,df_freekicks_direct,df_penalty]))))
    

    all_events = pd.concat([all_shots,all_cross,deep_pass]).assign(Spiel = name,Zeitperiode="",attacking_team="")
    own = df_events[df_events['type.primary'] == "own_goal"].assign(Outcome="Eigentor")
    if(len(own) !=0):
        own = shotsFunc.own(own)
        all_events = pd.concat([all_shots,all_cross,deep_pass,own]).assign(Spiel = name,Zeitperiode="",attacking_team="")

    frame = positionFuncs.time(goalkeeper.goalkeeperNan(all_events,GK_ids))
    frame_sorted = frame.sort_values(by=["team.name","minute","second"])
    frame_outcomes,todel  = merge.merge(merge.unkown(frame_sorted,df_events))

    frame_merged = frame_outcomes.iloc[::-1]

    frame_filtered = frame_merged[~frame_merged['id'].isin(todel)]

    frame_filtered = positionFuncs.standard_pos(frame_filtered.assign(stop=""))
    frame_filtered = merge.stopTimestamp(frame_filtered,df_events)

   

    kick_off_first = df_events[df_events.matchPeriod == "1H"].head(1)["matchTimestamp"].iloc[0]
    kick_off_second = df_events[df_events.matchPeriod == "2H"].head(1)["matchTimestamp"].iloc[0]

    kick_off_first_e = 0
    kick_off_second_e = 0
    if len(df_events[df_events.matchPeriod == "1E"] != 0):
        kick_off_first_e = df_events[df_events.matchPeriod == "1E"].head(1)["matchTimestamp"].iloc[0]
        kick_off_second_e = df_events[df_events.matchPeriod == "2E"].head(1)["matchTimestamp"].iloc[0]
    frame_resolved_times = wyscout_to_df.resolve(frame_filtered,kick_off_first,kick_off_second,kick_off_first_e,kick_off_second_e)

    
    
    frame_resolved_times = frame_resolved_times.sort_values(by=["team.name","minute","second"])
    frame_final = frame_resolved_times.rename(columns=rename)#renaming of cols

   

    frame_final.loc[frame_final['Team'] == "Turkey", 'Team'] = "Türkiye"
    frame_final.to_csv("generated_files/" + str(name) + ".csv", mode = 'w', columns= export_cols, index=False)#export
