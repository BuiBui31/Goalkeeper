import math


def transformCords(x_cors,ball_x,y_cors,ball_y):
    
    x_cors = list(map(lambda x: 105/2 + x, x_cors))
    ball_x = list(map(lambda x: 105/2 + x, ball_x)) 
    y_cors = list(map(lambda x: -x, y_cors))
    ball_y = list(map(lambda x: -x, ball_y)) 

    return x_cors,ball_x,y_cors,ball_y

def getDistance(point1,point2):
    x1,y1 = point1
    x2,y2 = point2

    return math.sqrt((x2-x1)**2 + (y2-y1)**2)

def find_intersectionX(point2,vec):
   #assumption always using goal line
    x2,y2 = point2
    dx2,dy2 = vec
    if(dy2==0):
        return (-1,-1)

    s = (-y2)/dy2
    

    return (x2 + s*dx2,0)

def find_intersectionY(point1,vec):
   #assumption always using goal line
    x1,y1 = point1
    dx1,dy1 = vec
    if(dx1==0):
        return (-1,-1)
    s = (-x1)/dx1
    
    return (0,y1 + s*dy1)

def rotate90(vec):
    x,y = vec
    if(y>=0):
        return (y,-x)
    else:
        return (-y,x)
    
def findMiddleCircle(ball_x,ball_y):
    all_intersect_circle = []
    right_post = (0,3.66) #right goal post 
    
    for x, y in zip(ball_x, ball_y):
        if(x>=0):
            direction_vector = (right_post[0]-x, right_post[1]-y)
            half_vec = ((x + right_post[0]) / 2, (y + right_post[1]) / 2)
            roated = rotate90(direction_vector) #get the 90 rotaed vec in correct 
            
            intersect_point = find_intersectionX(half_vec,roated) # Mittelpunkt des Umkreis
        
            all_intersect_circle.append(intersect_point)
        else:
            all_intersect_circle.append((-1,-1))
    return all_intersect_circle 

def interSectionGoalLine(ball_x,ball_y):
    middle = findMiddleCircle(ball_x,ball_y)
    intersection_points = []
    for i in range(0,len(middle),1):
        
        p = middle[i]
        if(p==(-1,-1)):
            intersection_points.append((-1,-1))
        else:
            
            radius = getDistance(p,(0,3.66)) #right goal post 
            south_pole = (p[0]-radius,p[1])
            south_pole_ball_vec = (ball_x[i]-south_pole[0],ball_y[i]-south_pole[1])
            interSect = find_intersectionY(south_pole,south_pole_ball_vec)
            
            intersection_points.append(interSect)
    return intersection_points

def goalKeeperDistance(ball_x,ball_y,cor_x,cor_y):
    goalKepper_distance_list = []
    intersection_points = interSectionGoalLine(ball_x,ball_y)
   
    if(len(cor_x) != len(intersection_points)):
        print("not same size")
    for i in range(0,len(intersection_points),1):
        if(intersection_points[i] != (-1,-1)):
            goalKepper_distance = getDistance(intersection_points[i],(cor_x[i],cor_y[i]))
            goalKepper_distance_list.append(goalKepper_distance)
        elif(ball_x[i]<=-0.5):
            return goalKepper_distance_list

    return goalKepper_distance_list