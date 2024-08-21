
def deepBall(df_events):
    df_pass = df_events[(df_events['type.primary']=='pass')]
    mask_through = df_pass['type.secondary'].apply(lambda x: ('through_pass' in x) & ("pass_to_penalty_area" in x))
    deep_pass = df_pass[mask_through].assign(Spielsituation="Ball in die Tiefe",Standard="Nein")

    return deep_pass