
def shots(df_events):
    return df_events[df_events['type.primary'].isin(['shot'])].assign(
    Spielsituation="",
    Standard="Nein"
)

def own(df_own):
    for i,row in df_own.iterrows():
        if row.loc['type.primary'] == "own_goal":
            team = row.loc["team.name"]
            df_own.at[i,"team.name"] = row.loc["opponentTeam.name"]
            df_own.at[i,"opponentTeam.name"] = team
    return df_own


def outcome(shots):
    for i,row in shots.iterrows():
        if(row.loc["shot.isGoal"]):
            shots.at[i,"Outcome"] = "Tor "
        elif(row.loc["shot.goalZone"] == "bc"):
            shots.at[i,"Outcome"] = "Verteidiger geblockt"
        elif(row.loc["shot.goalZone"] == "plt"):
            shots.at[i,"Outcome"] = "Aluminium"
        elif(row.loc["shot.onTarget"]):
            shots.at[i,"Outcome"] = "gehalten"
        else:
            shots.at[i,"Outcome"] = "nebens Tor"
    return shots

def bodypart(event):
    for i,row in event.iterrows():
        part = str(row.loc["shot.bodyPart"])
        match part:
                case "left_foot":
                    event.at[i,"shot.bodyPart"] = "Fuss links"
                case "right_foot":
                    event.at[i,"shot.bodyPart"] = "Fuss rechts"
                case "head_or_other":
                    event.at[i,"shot.bodyPart"] = "Kopf oder anderes"
    return event
