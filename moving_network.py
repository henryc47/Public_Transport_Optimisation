#moving_network.py
#this stores the newer updated network class "moving_network"
#as well as related functionality

from network import extract_coordinates

#Point class, represents a point on the transport network
class Point:
    def __init__(self,name,location,type,speed):
        self.name = name #name of the point
        self.latitude,self.longitude = extract_coordinates(location) #latitude and longitude for visual display
        self.type = type #type of point, valid types are . . .
        #"speed", the point only exists to represent a speed change, changing tracks is not possible
        #"junction", it is possible to change tracks at full line speed, as would be the case at a junction
        #"normal", a normal point where there is an additional speed limit for changing tracks
        self.speed = speed #speed at the point to change tracks, only relevant for normal points

#Line class, representing a section of track
class Line:
    def __init(self,name,start,end,num_tracks,length,electrified,speed_limit_norm,speed_limit_tilt_double,speed_limit_tilt):
        self.name = name #name of the line
        self.start_point = start #reference to the point at the start of the line
        self.end_point = end #reference to the point at the end of the line
        self.num_tracks = num_tracks #number of tracks on the line
        self.length = length #length of the line, metres
        self.electrified = electrified #is this line electrified, y or n
        self.speed_limit_norm = speed_limit_norm #speed limit for normal trains, m/s
        self.speed_limit_tilt_double = speed_limit_tilt_double #speed limit for double decker tilting trains, m/s
        self.speed_limit_tilt = speed_limit_tilt #speed limit for single decker tilting trains, m/s



#Station class, represents a stop on the transport network
class Station:
    def __init__(self,name,line):
        self.name = name #name of the station
        self.line = line #reference to the line 
        


#network class, represents the overall structure of the transport network
class Network:
    #initalise the physical network
    def __init__(self,track_csv,points_csv,stations_csv):
