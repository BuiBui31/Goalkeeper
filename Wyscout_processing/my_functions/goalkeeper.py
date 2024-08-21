import pandas as pd
from my_functions.positionFuncs import zoning

def names(df_events):
    GK = df_events[(df_events['player.position']=='GK')] 
    GK_id = GK[["team.name","player.name"]].drop_duplicates().set_index('team.name')['player.name'].to_dict()
    if(len(GK_id) > 2):
        print("Goalkeeper substitution")
    return GK_id

def goalkeeperNan(events,GK_id):
     for i,row in events.iterrows():
          name = row["opponentTeam.name"]
          events.at[i,"shot.goalkeeper.name"] = GK_id[name]
          events.at[i,"attacking_team"]=  row["team.name"]
          events.at[i,"team.name"] = row["opponentTeam.name"]
          
     return events

def goalkeeperName(events,GK_id):
     for i,row in events.iterrows():
          name = row["team.name"]
          events.at[i,"Goalkeeper"] = GK_id[name]
     return events

def resolve(all,df_events):
      for i,row in all.iterrows():
         if (i!=0):
            row1 = df_events.iloc[i-1]
            if((row["Ball_erhalten_min"]=="") and (row["Spielsituation"] != "Ruhender Ball")):
                  all.at[i,"Ball_erhalten_min"] = row1["minute"] 
                  all.at[i,"Ball_erhalten_s"] = row1["second"]
                  all.at[i,"Zuspielzone"] = zoning(row1) + " (Von Gegner)"
      return all

def merge_save(actions):
    save_flag = False
    save_time = 0
    carry_flag = False
    save_id = 0
    to_del = []
    for i, row in actions.iterrows():
        situation = row["Spielsituation"]
        if(carry_flag):
            carry_flag = False
            actions.at[i,"Spielsituation"] = "Spielaufbau Hand"
        if(save_flag):
            save_flag = False
            if((((row["minute"]*60 + row["second"])-save_time) < 10)&(situation != "Ball erhalten")):
               actions.at[i,"Spielsituation"] = "Spielaufbau Hand"
            to_del.append(save_id)
        if(situation=="Carry"):
            save_flag = False
            carry_flag = True
        if(situation=="Save"):
            save_time = row["minute"]*60 + row["second"]
            save_flag = True
            carry_flag = False
            save_id = row["id"]
    return actions,to_del

def merge_recieve(actions):
    counter = 1
    to_merge = []
    recieve_flag = False
    recieve_time_min=0
    recieve_time_s=0
    zone = ""
    for i, row in actions.iterrows():
        if(counter < len(actions)):
            time = row["minute"]*60 + row["second"]
            row1 = actions.iloc[counter]
            time1 = row1["minute"]*60 + row1["second"]
            situation = row["Spielsituation"]
            if(recieve_flag & (situation != "Ball erhalten")):
                recieve_flag = False
                actions.at[i,"Ball_erhalten_min"] = recieve_time_min
                actions.at[i,"Ball_erhalten_s"] = recieve_time_s
                actions.at[i,"Zuspielzone"] = zone
            elif(situation in ["Carry","Ball erhalten"]):
                if(time1-time < 15):
                    recieve_flag = True
                    recieve_time_min = row["minute"]
                    recieve_time_s = row["second"]
                    zone = zoning(row)
                    if(not row["pass.accurate"]):
                        zone += " (Von Gegner)"
                to_merge.append(row["id"])
            elif(situation == "Save"):
                    if(time1-time < 15):
                        recieve_flag = True
                        recieve_time_min = row["minute"]
                        recieve_time_s = row["second"]
                    to_merge.append(row["id"])
            else:
                recieve_flag = False
        elif(recieve_flag):
            actions.at[i,"Ball_erhalten_min"] = recieve_time_min
            actions.at[i,"Ball_erhalten_s"] = recieve_time_s
            actions.at[i,"Zuspielzone"] = zone
        counter+=1
    return actions, to_merge

def actions(df_goalkeeper):
    df_goalkeeper_standard_mask = df_goalkeeper["type.primary"].apply(lambda x: (x=="free_kick") | (x=="goal_kick"))
    df_goalkeeper_standard = df_goalkeeper[df_goalkeeper_standard_mask].assign(Spielsituation="Ruhender Ball")

    goalkeeper_pass_mask = df_goalkeeper["type.primary"]=="pass"
    hand_pass_mask = df_goalkeeper["type.secondary"].apply(lambda x: "hand_pass" in x)
    df_goalkeeper_hand_pass = df_goalkeeper[hand_pass_mask].assign(Spielsituation="Spielaufbau Hand")
    df_goalkeeper_other_pass = df_goalkeeper[~hand_pass_mask & goalkeeper_pass_mask].assign(Spielsituation="Spielaufbau Fuss")

    df_intercept = df_goalkeeper[(df_goalkeeper["type.primary"]=="interception")]
    intercept_pass_mask = df_intercept["type.secondary"].apply(lambda x: ("pass" in x)&(not "hand_pass" in x))
    df_intercept_final = df_intercept[intercept_pass_mask].assign(Spielsituation="Pass other")

    carry_mask = df_goalkeeper["type.primary"].apply(lambda x: "carry" in x)
    df_goalkeeper_carry = df_goalkeeper[carry_mask].assign(Spielsituation="Carry")

    save_mask = df_goalkeeper["type.secondary"].apply(lambda x: "save" in x)
    df_goalkeeper_save = df_goalkeeper[save_mask].assign(Spielsituation="Save")

    all_actions = pd.concat([df_goalkeeper_standard,df_intercept_final,df_goalkeeper_hand_pass,df_goalkeeper_other_pass,df_goalkeeper_carry,df_goalkeeper_save]).sort_values(by=["team.name","matchPeriod","minute","second"]).assign(Zuspielzone="",Passzone="")
    return all_actions

def pass_zone(all):
    for i,row in all.iterrows():
        all.at[i,"Passzone"] = zoning(row) 
    return all