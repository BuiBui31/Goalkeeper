#classification of shots areas 
import math

def zone_classification(shots):
    for i,row in shots.iterrows():
        x_cor = int(row.loc["location.x"]) 
        y_cor = int(row.loc["location.y"]) 
        if(row.loc["type.primary"]  == 'penalty'):
            shots.at[i,"Spielsituation"] = "Rote Zone"
        elif "touch_in_box" not in row.loc["type.secondary"]:
            shots.at[i,"Spielsituation"] = "Distanzschuss"
        elif x_cor >= 92 and (y_cor >= 19 or y_cor <= 81):
            shots.at[i,"Spielsituation"] =  "Nahdistanzzone Schuss"
        elif (x_cor < 92 and x_cor >= 84) and (y_cor >= 19 or y_cor <= 81):
            shots.at[i,"Spielsituation"] =  "Rote Zone Schuss"
    return shots

def zoning(row):
    if(math.isnan(row.loc["location.x"]) or math.isnan(row.loc["location.y"])):
        return "nicht möglich"
    x_cor = int(row.loc["location.x"]) 
    y_cor = int(row.loc["location.y"]) 
    to_add =''
    if(x_cor>=94):
        to_add +='A'
    elif(x_cor>=81):
        to_add +='B'
    elif(x_cor>=66):
        to_add +='C'
    elif(x_cor>=50):
        to_add +='D'
    else:
        to_add +='E'

    if((y_cor<19)|(y_cor > 81)): #4
        to_add +='4'
    elif((19 <= y_cor < 37) | (63 < y_cor <= 81)): #3
        to_add +='3'
    elif((37 <= y_cor < 45) | (55 < y_cor <= 63)): #2
        to_add +='2'
    else:   #1
        to_add +='1'
    return to_add

def standard_pos(standard):
    for i,row in standard.iterrows():
        y_cor = int(row.loc["location.y"])
        if(row.loc["Standard"] != "Nein"):
            if (y_cor<37):
                standard.at[i,"Seite_Standard"] =  "Links"
            elif (y_cor>63):
                standard.at[i,"Seite_Standard"] =  "Rechts"
            else:
                standard.at[i,"Seite_Standard"] =  "Zentral"
    return standard

def zoning_helper(events):
    for i,row in events.iterrows():
        to_add = zoning(row)
        events.at[i,"Zuspiel_Zone"] = to_add
    return events

def shot_zoning(shots,df_events):
    for i,row in shots.iterrows():
        for j in range (0,6):
            check = df_events.iloc[i-j] 
            if (check["type.primary"] == 'pass'):
                 shots.at[i,"Zuspiel_Zone"] =  zoning(check)
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

def time(events):
    for i,row in events.iterrows():
        if row.loc["minute"] < 15:
            events.at[i,"Zeitperiode"] = "0-15min"
        elif row.loc["minute"] < 30:
            events.at[i,"Zeitperiode"] = "15-30min"
        elif row.loc["minute"] < 45:
            events.at[i,"Zeitperiode"] = "30-45min"
        elif row.loc["matchPeriod"] == "1H":
            events.at[i,"Zeitperiode"] = "1. Nachspielzeit"
        elif row.loc["minute"] < 60:
            events.at[i,"Zeitperiode"] = "45-60min"
        elif row.loc["minute"] < 75:
            events.at[i,"Zeitperiode"] = "60-75min"
        elif row.loc["minute"] < 90:
            events.at[i,"Zeitperiode"] = "75-90min"
        elif row.loc["matchPeriod"] == "2H":
            events.at[i,"Zeitperiode"] = "2. Nachspielzeit"
        elif row.loc["matchPeriod"] == "1E":
            events.at[i,"Zeitperiode"] = "90-105min"
        elif row.loc["matchPeriod"] == "2E":
            events.at[i,"Zeitperiode"] = "105-120min"
    return events