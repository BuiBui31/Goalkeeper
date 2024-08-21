import pandas as pd

def freekicks(df_events):

    mask = df_events['type.secondary'].apply(lambda x: 'free_kick_shot' in x) #freekicks/shots
    free_kick_cross = df_events['type.secondary'].apply(lambda x: 'free_kick_cross' in x)
    df_freekicks_direct = df_events[mask].assign(Standard = "Freistoss",direkt_indirekt="direkt") #direct freekicks
    df_freekicks_indirect = df_events[free_kick_cross].assign(Spielsituation="Hoher Ball",Standard = "Freistoss",direkt_indirekt="indirekt") #indirect freekicks
   
    return df_freekicks_direct,df_freekicks_indirect