import pandas as pd

# cross 
def cross(df_events,ids):
    df_pass = df_events[(df_events['type.primary']=='pass')]
    cross_mask = df_events['type.secondary'].apply(lambda x: 'cross' in x) #pass into penalty area actual cross
    maskbackward = df_events['id'].apply(lambda x: x not in ids)
    mask_high = df_events['pass.height'] == "high"
    blocked_mask = df_events['type.secondary'].apply(lambda x: 'cross_blocked' not in x) #cross blocked 

    pass_box = df_pass['type.secondary'].apply(lambda x: ('touch_in_box' in x) & ("lateral_pass" in x))
    not_backward = df_pass["id"].apply(lambda x: x not in ids)
    high = df_pass["pass.height"].apply(lambda x: x !="high")
    not_cross = df_pass['type.secondary'].apply(lambda x: 'cross' not in x)

    df_cross_low = pd.concat([df_pass[pass_box & not_backward & high & not_cross],df_events[~mask_high & cross_mask & blocked_mask & maskbackward]])
    df_cross_low = df_cross_low.assign(Spielsituation="Ball durch 16er",direkt_indirekt="",Standard="Nein")

    acc_mask_low = df_cross_low["pass.accurate"].apply(lambda x: x)
    none_mask_low = df_cross_low["pass.recipient.name"].apply(lambda x: x==None)

    df_cross_low_defend = df_cross_low[~none_mask_low & ~acc_mask_low].assign(Outcome="Verteidiger geklärt") #labling low cross
    df_cross_low_noAction = df_cross_low[~acc_mask_low & none_mask_low].assign(Outcome="keine Aktion")

    df_cross_low_final = pd.concat([df_cross_low_defend,df_cross_low_noAction,df_cross_low[acc_mask_low]]) #merging all low cross
    
    one = df_pass["type.secondary"].apply(lambda x: ("pass_to_penalty_area" in x) & ("cross" not in x) & ("lateral_pass" in x))
    two = df_pass["pass.length"].apply(lambda x: x < 25)
   
    cross_pass = df_pass[one & two & not_backward & ~high]

    df_cross_high = pd.concat([cross_pass,df_events[mask_high & cross_mask & maskbackward]])

    df_cross_high = df_cross_high.assign(Spielsituation="Hoher Ball",direkt_indirekt="",Standard="Nein")  #labling high cross

    acc_mask_high = df_cross_high["pass.accurate"].apply(lambda x: x)
    none_mask_high = df_cross_high["pass.recipient.name"].apply(lambda x: x==None)
    df_cross_high_noAction = df_cross_high[~acc_mask_high & none_mask_high].assign(Outcome="keine Aktion") #applying mask adding outcome
    df_cross_high_defender = df_cross_high[~acc_mask_high & ~none_mask_high].assign(Outcome="Verteidiger geklärt")

    df_cross_high_final = pd.concat([df_cross_high_noAction,df_cross_high_defender,df_cross_high[acc_mask_high]]) #merging all cross
    
    return pd.concat([df_cross_high_final,df_cross_low_final])
