#merge indirect and hohe bälle

def merge(cross):
    to_merge = []
    counter = 0
    cross = cross.iloc[::-1]
    for i, row in cross.iterrows():
        if counter > 0:
            row1 = cross.iloc[counter-1]
            time = row["minute"]*60 + row["second"]
            action = row["Spielsituation"]
            standard = row["Standard"]
            if(row["shot.goalkeeper.name"]==row1["shot.goalkeeper.name"]): #avoid merge after teams switch
                time1 = row1["minute"]*60 + row1["second"]
                if ((action == "Rückpass Grundlinie")| (action == "Ball durch 16er") | (action == "Hoher Ball") | ((standard == "Ecke") & (row["direkt_indirekt"]=="direkt"))):
                    if((time1-time < 3)& (row["Outcome"] != "gehalten")): # for direct/cross only merge if within 3s
                        #to_merge.append(int(row1["id"]))
                        cross.at[i,"Outcome"] = str(row1["Outcome"]) + " (nächste Aktion)"
                        cross.at[i,"shot.bodyPart"] = row1["shot.bodyPart"]
                elif (row["Standard"] == "placeHolder"):
                    if(time1-time < 8): #for indirect
                        to_merge.append(row1["id"])
                        cross.at[i,"Spielsituation"] = row1["Spielsituation"]
                        cross.at[i,"Outcome"] = row1["Outcome"]
                        cross.at[i,"Standard"] = "Ecke"
                    else:
                        to_merge.append(int(row["id"]))
                        cross.at[i,"Standard"] = "Ecke"
        if(row["Standard"] == "placeHolder"):
            to_merge.append(int(row["id"]))
            cross.at[i,"Standard"] = "Ecke"
        counter+=1
    return cross,to_merge

def unkown(events,df_events):
    for i,row in events.iterrows():
        if(row["Outcome"]==""):
            events.at[i,"Outcome"] = "keine Aktion"
            time = row["minute"]*60 + row["second"]
            x_cor = int(row["possession.startLocation.x"]) 
            y_cor = int(row["possession.startLocation.y"])
            for j in range(i+1,i+6):
                if (j>len(df_events)): # checking for out of bounds 
                    break
                row1 = df_events.iloc[j]
                secondary = row1["type.secondary"]
                primary = row1["type.primary"]
                timeCheck = row1["minute"]*60 + row1["second"]
                x_corCheck = row1["possession.startLocation.x"] 
                y_corCheck = row1["possession.startLocation.y"]
                if((timeCheck-time > 7)):
                    break
                if(("recovery" in secondary) | (primary == "interception")):
                    events.at[i,"Outcome"] = "geklärt"
                    break
                if(x_cor,y_cor)!=(x_corCheck,y_corCheck):# if not same posession anymore without recovery break and no action
                    break
    return events

def stopTimestamp(events,df_events):
    for i,row in events.iterrows():
        events.at[i,"stop"] = df_events.iloc[i+1]["videoTimestamp"]

    return events