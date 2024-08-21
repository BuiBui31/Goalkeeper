import pandas as pd
import json
from datetime import datetime

def wyscout_json_to_df(file_name,base_path):
    with open(base_path+ '/' +file_name, encoding='utf8') as f:
        js = json.load(f)
        df = pd.json_normalize(js['events'])
    return df

def correct_time(sub, to_sub):
  
    time_format = '%H:%M:%S.%f'
    
    time1 = datetime.strptime(sub, time_format)
    time2 = datetime.strptime(to_sub, time_format)
    
    time_diff = time1 - time2
    
    result = (datetime.min + time_diff).strftime('%H:%M:%S.%f')[:-3]
    
    return result

def resolve(events,kick_off_first,kick_off_second,kick_off_first_e,kick_off_second_e):
    for i,row in events.iterrows():
        if(row["matchPeriod"] == "1H"):
            from_sub = row["matchTimestamp"]
            events.at[i,"matchTimestamp"] = correct_time(from_sub, kick_off_first)
        elif(row["matchPeriod"] == "2H"):
            from_sub = row["matchTimestamp"]
            events.at[i,"matchTimestamp"] = correct_time(from_sub, correct_time(kick_off_second,"00:45:00.000"))
        elif(row["matchPeriod"] == "1E"):
            from_sub = row["matchTimestamp"]
            events.at[i,"matchTimestamp"] = correct_time(from_sub, correct_time(kick_off_first_e,"01:30:00.000"))
        elif(row["matchPeriod"] == "2E"):
            from_sub = row["matchTimestamp"]
            events.at[i,"matchTimestamp"] = correct_time(from_sub, correct_time(kick_off_second_e,"01:45:00.000"))
    return events