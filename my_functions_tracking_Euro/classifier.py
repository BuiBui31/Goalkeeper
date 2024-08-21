import math
import numpy as np
from .gemometry import transformCords,goalKeeperDistance
from .timing import segment
from matplotlib import animation
from mplsoccer import Pitch

def transformX(x):
    return (x + 52.5) / (2*52.5) * 100
def transformY(y):
    return (1 - (y+34.0)/ (2*34.0)) * 100

def animation_vid(ball_x,ball_y,x_cors,y_cors,title):
    pitch = Pitch(pitch_type='wyscout', goal_type='line', pitch_width=68, pitch_length=105, pitch_color='#aabb97', stripe=True, stripe_color='#c2d59d', line_color='black')
    fig, ax = pitch.draw(figsize=(15, 10))
    marker = {'marker': 'o', 'markeredgecolor': 'black', 'linestyle': 'None'}
    ball, = ax.plot([], [], ms=6, markerfacecolor='red', zorder=3, **marker)
    home, = ax.plot([], [], ms=10, markerfacecolor='blue', **marker)

    def animate(i):
        ball.set_data(transformX(ball_x[i]),transformY(ball_y[i]))
        home.set_data(transformX(x_cors[i]),transformY(y_cors[i]))
        return ball, home

    anim = animation.FuncAnimation(fig, animate, min(len(x_cors),40), interval=25, blit=True)
    anim.save(f'vids/{title}.mp4', fps = 25)

def round_to_nearest_40ms(seconds):
    
    milliseconds = seconds * 1000
    
    
    nearest_40ms = round(milliseconds / 40) * 40
    
    return nearest_40ms

def timestamp_to_seconds(timestamp):
 
    hours, minutes, seconds = timestamp.split(':')
    
    seconds, milliseconds = seconds.split('.')
    
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)
    milliseconds = int(milliseconds)
    
    total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000
    
    return round_to_nearest_40ms(total_seconds)

def check_goal(outcome):
    if((outcome == "nebens Tor") or (outcome == "Tor ") or (outcome == "Tor  (nächste Aktion)")):
        return True
    else:
        return False
    
def check_shot(spielsituation):
    if((spielsituation == "Nahdistanzzone Schuss") or (spielsituation == "Rote Zone Schuss") or (spielsituation == "Distanzschuss")):
        return True
    else:
        return False
    
def near(ball_x,ball_y,x_cors,y_cors):
    for i in range(0,len(x_cors),1):
        if((abs(ball_x[i]-x_cors[i])<3) and (abs(ball_y[i]-y_cors[i])<3)):
            return True
    return False

def classify(df_events,goalkeeper_df,metadata_df,df,df_ball):
    for j,row in df_events.iterrows():
        outcome = row["Outcome"]
        timestamp = timestamp_to_seconds(row["matchTimestamp"])
        period = row["Periode"]
        length = int(min(round((row["stop"] - row["videoTimestamp"])*25),40))
        team = row["Team"]


        if(len(goalkeeper_df[team])==0):
            continue
        goaklKeeperID = goalkeeper_df[team].iloc[0]

        goal_flag = True
        if(check_goal(outcome)):
            goal_flag = False
            length = length - 10

        shot_flag = True
        situation = row["Spielsituation"]
        if(check_shot(situation)):
            shot_flag = False
            timestamp = timestamp-400
            length = length - 10
            
        
        x_cors,y_cors,z_cors,ball_x,ball_y,ball_z = segment(goaklKeeperID,timestamp,length,df,df_ball,period)
        
        #animation_vid(ball_x,ball_y,x_cors,y_cors,(row["Torhüter"]+ " "+ str(row["Minute"]) + ":"+str(row["Sekunden"])))

        if(metadata_df[period].iloc[0] == team):
            for i in range(0,len(x_cors)):
                    x_cors[i] = 0-x_cors[i]
                    ball_x[i] = 0-ball_x[i]
                    y_cors[i] = 0-y_cors[i]
                    ball_y[i] = 0-ball_y[i]

        x_cors,ball_x,y_cors,ball_y = transformCords(x_cors,ball_x,y_cors,ball_y)
        print("x_cors:", x_cors)
        print("y_cors:", y_cors)
        print("ball_x:", ball_x)
        print("ball_y:", ball_y)
        
        
        dist = goalKeeperDistance(ball_x,ball_y,x_cors,y_cors)
       
        
        if(len(dist) == 0):
            df_events.at[j,"Entscheid"] = "nicht möglich"
            continue

        df_events.at[j,"x_start"] = x_cors[0]
        df_events.at[j,"y_start"] = y_cors[0]
        df_events.at[j,"x_avg"] = np.mean(x_cors)
        df_events.at[j,"y_avg"] = np.mean(y_cors)

        print("X_cors: ", x_cors[0])

        start = dist[0]
        theta = 0.9
        back = False
        go = False
    
      
        for k in range(1,len(dist)):
            if(dist[k]-start<=-(theta)):
                back = True
                break
            if(dist[k]-start>=(theta)):
                go = True
                break
        
        if(back):
            df_events.at[j,"Entscheid"] = "Back"
        elif(go):
            df_events.at[j,"Entscheid"] = "Go" 
        else:
            df_events.at[j,"Entscheid"] = "Stay"
        
        x_cors,y_cors,z_cors,ball_x,ball_y,ball_z = segment(goaklKeeperID,timestamp,length+12,df,df_ball,period)
        x_cors,ball_x,y_cors,ball_y = transformCords(x_cors,ball_x,y_cors,ball_y)
        max_dist = max(dist)

        min_abs_value = np.min(np.abs(np.array(x_cors)-np.array(ball_x)))

        if((go) and (goal_flag) and (ball_z[-1]>=1) and (shot_flag) and (max_dist>1.5) and (min_abs_value<3)):
            if(outcome == "Verteidiger geklärt"):
                df_events.at[j,"Entscheid"] = "Catch"
                df_events.at[j,"Outcome"] = "Torhüter Catch"

    
    
    return df_events
                


                    