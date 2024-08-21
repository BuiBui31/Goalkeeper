import pandas as pd

def goalkeeperInter(df_cross_final,df_corner_final,df_freekicks_indirect,df_backwardpass_final,GK_ids):
    all_cross = pd.concat([df_cross_final,df_corner_final,df_freekicks_indirect,df_backwardpass_final]).sort_values(by=["team.name","matchPeriod","minute","second"])
    intervention_mask = all_cross["pass.recipient.id"].apply(lambda x: x in GK_ids)
    all_cross = pd.concat([all_cross[intervention_mask].assign(Outcome="gehalten"),all_cross[~intervention_mask]])
    return all_cross
