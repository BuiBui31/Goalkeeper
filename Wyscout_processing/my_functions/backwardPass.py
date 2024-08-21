#backwardpass inside penalty box
import pandas as pd

def backwardPass(df_events):

    df_pass = df_events[(df_events['type.primary']=='pass')]
    backward_location_mask = df_pass['location.x'].apply(lambda x: x > 94) #checking for x cordinates 
    not_back_mask = df_pass['type.secondary'].apply(lambda x: 'back_pass' not in x) #not backward
    penaltyBox_mask = df_pass['location.y'].apply(lambda x: (x > 19) & (x < 81)) # still inside penalty box check
    df_backwardpass = df_pass[backward_location_mask & not_back_mask & penaltyBox_mask].assign(Spielsituation="Rückpass Grundlinie",Standard="Nein")

    head_mask = df_backwardpass['type.secondary'].apply(lambda x: 'head_pass' not in x)
    df_backwardpass = df_backwardpass[head_mask]
    
    if(len(df_backwardpass)!=0):
        mask_back_none = df_backwardpass["pass.recipient.name"].apply(lambda x: x==None) #noOne => keine Aktion
        mask_back_inAcc = df_backwardpass["pass.accurate"].apply(lambda x: x) #just inaccurate defender recovcery

        df_backwardpass_inAcc = df_backwardpass[mask_back_none & ~mask_back_inAcc].assign(Outcome="keine Aktion")
        df_backwardpass_def = df_backwardpass[~mask_back_none & ~mask_back_inAcc].assign(Outcome="Verteidiger geklärt")

        ids = df_backwardpass["id"].values.tolist() #get event ids of all backwardpasses

        df_backwardpass_final = pd.concat([df_backwardpass_def,df_backwardpass_inAcc,df_backwardpass[mask_back_inAcc]]) #merge to final df
        
        return df_backwardpass_final,ids
    else:
        empty_df = pd.DataFrame()
        return empty_df,[]