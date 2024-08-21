def segment(playerID,start,length,df,df_ball,half):

    x_cors = []
    y_cors = []
    z_cors = []
    ball_x= []
    ball_y= []
    ball_z = []

    half_time = 0
    print(half)
    if(half == "1H"):
        df = df[df.half=="One"]
        df_ball = df_ball[df_ball.half=="One"]

    elif(half == "2H"):
        half_time = 2700000
        df = df[df.half=="Two"]
        df_ball = df_ball[df_ball.half=="Two"]
    elif(half == "1E"):
        half_time = 5400000
        df = df[df.half=="Three"]
        df_ball = df_ball[df_ball.half=="Three"]
    elif(half == "2E"):
        half_time = 6300000
        df = df[df.half=="Four"]
        df_ball = df_ball[df_ball.half=="Four"]

    start = start - half_time
    df_player = df[df.object_id==playerID]
    for u in range(0,length,1):
        timestamp = start + u*40
        
        if(len(df_ball.loc[df_ball.timestamp == timestamp, 'x']) != 0 and (len(df_player.loc[df_player.timestamp == timestamp, 'x']) != 0)):
            ball_x.append(df_ball.loc[df_ball.timestamp == timestamp, 'x'].iloc[0])
            ball_y.append(df_ball.loc[df_ball.timestamp == timestamp, 'y'].iloc[0])
            ball_z.append(df_ball.loc[df_ball.timestamp == timestamp, 'z'].iloc[0])

            x_cors.append(df_player.loc[df_player.timestamp == timestamp, 'x'].iloc[0])
            y_cors.append(df_player.loc[df_player.timestamp == timestamp, 'y'].iloc[0])
            z_cors.append(df_player.loc[df_player.timestamp == timestamp, 'z'].iloc[0])
    return x_cors,y_cors,z_cors,ball_x,ball_y,ball_z