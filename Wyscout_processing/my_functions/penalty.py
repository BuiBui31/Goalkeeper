def penalty(df_events):
    df_penalty = df_events[(df_events['type.primary']=='penalty')]
    df_penalty= df_penalty.assign(Standard = "Penalty")
    return df_penalty
