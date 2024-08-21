import pandas as pd

def corner(df_events):
    df_corner = df_events[(df_events["type.primary"]=="corner")]#filtering corner
    shot1 = df_corner["type.secondary"].apply(lambda x: "shot" in x)
    corner = df_corner[~shot1]
    corner_shot = df_corner[shot1].assign(direkt_indirekt="direkt",Standard="Ecke",Spielsituation="Hoher Ball")

    corner_pass = corner['pass.length'].apply(lambda x: x < 19) #checking for indirect corner
    corner_pass2 = corner['pass.endLocation.y'].apply(lambda x: x < 19)
    df_direct = corner[~corner_pass | ~corner_pass2].assign(direkt_indirekt="direkt",Standard="Ecke",Spielsituation="Hoher Ball",Outcome="gehalten")
    high = df_direct["pass.height"]== "high" #check if pass is high

    acc_mask_corner = df_direct["pass.accurate"].apply(lambda x: x)#just inaccurate defender recovcery
    none_mask_corner = df_direct["pass.recipient.name"].apply(lambda x: x==None)#noOne => keine Aktion


    df_direct_high_no = df_direct[high & ~acc_mask_corner & none_mask_corner].assign(Spielsituation="Hoher Ball",Outcome="Keine Aktion") #high no action
    df_direct_high_defender = df_direct[high & ~acc_mask_corner & ~none_mask_corner].assign(Spielsituation="Hoher Ball",Outcome="Verteidiger geklärt")#high defender
    df_direct_high_acc= df_direct[high & acc_mask_corner].assign(Spielsituation="Hoher Ball")#high and accurate

    df_direct_high = pd.concat([df_direct_high_no,df_direct_high_defender,df_direct_high_acc,corner_shot])#merge all direct high


    df_direct_low = df_direct[~high].assign(Spielsituation="Ball durch 16er") # low corner
    df_indirect = corner[corner_pass | corner_pass2].assign(direkt_indirekt="indirekt",Standard="placeHolder") #indirect with placeholder for merge fucntion

    df_corner_final = pd.concat([df_direct_low,df_direct_high,df_indirect])#merge together 
    return df_corner_final 