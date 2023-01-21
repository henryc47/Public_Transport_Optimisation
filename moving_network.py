#moving_network.py
#this stores the newer updated network class "moving_network"
#as well as related functionality

from network import extract_coordinates

#Point class, represents a point on the transport network
class Point:
    def __init__(self,id,name,location,type,speed):
        self.name = name #name of the point
        self.latitude,self.longitude = extract_coordinates(location) #latitude and longitude for visual display
        self.type = type #type of point, valid types are . . .
        #"speed", the point only exists to represent a speed change, changing tracks is not possible
        #"junction", it is possible to change tracks at full line speed, as would be the case at a junction
        #"normal", a normal point where there is an additional speed limit for changing tracks
        self.speed = speed #speed at the point to change tracks, only relevant for normal points

#Line class, representing a section of track
class Line:
    def __init__(self,id,name,start,end,num_tracks,length,electrified,speed_limit_norm,speed_limit_tilt_double,speed_limit_tilt):
        self.id = id #position of the line in the array of all lines
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
    def __init__(self,id,name,line,platforms):
        self.id = id #position of the station in the array of all stations
        self.name = name #name of the station
        self.line = line #reference to the line
        self.platforms = platforms 
        


#network class, represents the overall structure of the transport network
class Network:
    #initalise the physical network
    def __init__(self,lines_csv,points_csv,stations_csv):
        self.import_points(points_csv)
        self.import_lines(lines_csv)
        self.import_stations(stations_csv)


    #import and generate points from a csv file
    def import_points(self,points_csv):
        self.point_names = points_csv["Name"].to_list() #extract and store names
        point_locations = points_csv["Location"].to_list() #extract locations (coordinate pairs)
        point_types = points_csv["Type"].to_list() #extract type of point
        point_speeds = points_csv["Speed"].to_list() #speed allowed through the points
        #now let's create the points
        self.points = [] #list of all points in the network
        num_points = len(self.point_names) #number of points in the network
        for i in range(num_points):
            self.points.append(Point(i,self.point_names[i],point_locations[i],point_types[i],point_speeds[i])) #create a point and add it to the array

    
    #import and generate lines from a csv file
    def import_lines(self,lines_csv):
        self.line_names = lines_csv["Name"].to_list() #extract and store line names
        line_starts = lines_csv["Start"].to_list() #name of point at the start of this line
        line_ends = lines_csv["End"].to_list() #name of point at the end of this line
        line_num_tracks = lines_csv["Number of Tracks"].to_list() #number of train tracks on this line
        line_length = lines_csv["Length"].to_list() #length of this section of line
        line_electrified = lines_csv["Electrified"].to_list() #is the line electrified
        line_min_curve = lines_csv["Min Curvature"].to_list() #minimum curvature on this segment of track
        line_speed_limit_norm = lines_csv["Speed Limit"].to_list() #speed limit of non-tilting trains
        line_speed_limit_double_tilt = lines_csv["Speed Limit Double Tilt"].to_list() #speed limit of single tilting trains
        line_speed_limit_tilt = lines_csv["Speed Limit Tilt"].to_list() #speed limit of double tilting trains
        num_lines = len(self.line_names) #how many lines in the network
        self.lines = [] #list of all lines in the network
        failed_lines = 0 #number of lines not created due to an error
        for i in range(num_lines): #create all lines
            line_start = line_starts[i] #extract name of starting point
            line_end = line_ends[i] #extract name of ending point
            start_point,start_index = self.find_point(line_start) #extract info about the starting point
            end_point,end_index = self.find_point(line_end) #extract info about the ending point
            if start_index==-1: #if we cannot find the start point
                print("DATA ERROR: starting point for ",self.line_names[i]," not found, line skipped")
                failed_lines = failed_lines + 1
                continue
            elif end_index==-1: #if we cannot find the start point
                print("DATA ERROR: ending point for ",self.line_names[i]," not found, line skipped")
                failed_lines = failed_lines + 1
                continue
            else:
                id = i-failed_lines #position in the index of lines is number of lines created so far
                #create new line and add it to the list
                self.lines.append(Line(id,self.line_names[i],start_point,end_point,line_num_tracks[i],line_length[i],line_electrified[i],line_speed_limit_norm[i],line_speed_limit_double_tilt[i],line_speed_limit_tilt[i]))
    
    #import and generate stations from a csv file
    def import_stations(self,stations_csv):
        self.station_names = stations_csv["Name"].to_list() #extract and store station names
        line_names = stations_csv["Line"].to_list() #extract the name of the corresponding lines
        platforms = stations_csv["Platform"].to_list() #extract the list of lines which have platforms
        num_stations = len(self.station_names) #number of stations
        failed_stations = 0 #number of stations we were unable to create
        self.stations = []
        for i in num_stations: #create all stations
            line_name = line_names[i] #extract the name of the line
            line,line_index = self.find_line(line_name) #get the line reference and index
            if line_index==-1: #if line not found
                print("DATA ERROR: line for ",self.station_names[i]," not found, station skipped")
                failed_stations = failed_stations + 1
            else:
                id = i-failed_stations
                self.stations.append(Station(id,self.station_names[i],line,platforms))

    #return a reference to a point object as well as it's index (id) in the list of all points from a name
    def find_point(self,point_name):
        try:
            #if we can successfully find the named point
            point_index = self.point_names.index(point_name) #determine it's position in the array
            point_reference = self.points[point_index] #and generate a reference to it
            return point_reference,point_index
        except ValueError:
            #if we cannot find the named point
            print("DATA ERROR: point ",point_name," not found in list of all points") #print an error message
            return 0,-1 #index of -1 indicates cannot be found

    #return a reference to a line object as well as it's index (id) in the list of all lines from a name
    def find_line(self,line_name):
        try:
            #if we can successfully find the named line
            line_index = self.line_names.index(line_name) #determine it's position in the array
            line_reference = self.lines[line_index] #and generate a reference to it
            return line_reference,line_index
        except ValueError:
            #if we cannot find the named point
            print("DATA ERROR: line ",line_name," not found in list of all lines") #print an error message
            return 0,-1 #index of -1 indicates cannot be found





