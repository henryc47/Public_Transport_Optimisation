#moving_vehicle.py
#stores the moving vehicle class and related functionality
#this implements the physics of vehicle travel

#run this lines for testing
#import moving_vehicle as m
#a = m.MovingVehicle(50,160,8,27,378000,1.25,0.002,1.1,1.5,1.1,4400000,6000000,10,10,800000,'saver',0.9,0.8,65)
#moving vehicle class
class MovingVehicle:
    #create the vehicle and set it's parameters
    def __init__(self,max_speed,length,num_carriages,drag_area,tare_mass,air_density,rolling_resistance,max_acceleration,max_deceleration,design_deceleration,max_engine_power,max_regen_brake,regen_speed,brake_speed,max_brake,brake_mode,motor_efficiency,regen_efficiency,hotel_power):
        self.max_speed = max_speed #max speed limit of train, even if physics and track allow faster, m/s
        self.length = length #how long is the vehicle
        self.num_carriages = num_carriages #how many carriages make up the vehicle 
        self.drag_area = drag_area #effective frontal area in m^2
        self.tare_mass = tare_mass#unloaded mass in kg
        self.mass = self.tare_mass #current mass in kg, starts same as tare mass
        self.air_density = air_density #density of air, kg/m^3
        self.rolling_resistance = rolling_resistance #coefficient of rolling resistance
        self.max_acceleration = max_acceleration #max acceleration allowed, m/s^2
        self.max_deceleration = max_deceleration #max deceleration allowed, m/s^2
        self.design_deceleration = design_deceleration #max deceleration allowed to be used in routine operation, m/s^2
        self.max_engine_power = max_engine_power #max power from the engine, W
        self.max_regen_brake = max_regen_brake #max regenerative braking power, W
        self.regen_speed = regen_speed #speed below which regen braking power drops off quadratically, m/s
        self.brake_speed = brake_speed #speed below which to start using regular braking as well as regen braking when in saver mode
        self.max_brake = max_brake #max conventional braking power, W
        self.brake_mode = brake_mode #which type of braking in regular service, max = "use regen and regular", saver = "use regular only when speed below brake speed "
        self.motor_efficiency = motor_efficiency #how efficient is the motor at providing power, fraction
        self.regen_efficiency = regen_efficiency #how efficient is the motor at returing energy from braking, fraction
        self.hotel_power = hotel_power #how much power is used for non-traction purposes, W
    
    #calculate the amount of force caused by wind drag on the vehicle
    def calculate_drag(self,speed): #speed is in m/s
        force = 0.5*self.drag_area*self.air_density*speed*speed #force in newtons (N)
        return force
    
    #calculate the amount of force caused by rolling resistance on the vehicle
    def calculate_rolling_resistance(self): 
        force = self.rolling_resistance*self.mass
        return force
    
    #calculate the power required to maintain a particular speed
    def calculate_static_power(self,speed):
        drag_force = self.calculate_drag(speed)
        rolling_force = self.calculate_rolling_resistance()
        static_force = drag_force+rolling_force
        static_power = self.force_to_power(static_force,speed)
        return static_power

    #calculate either the power needed to accelerate at the maximum rate or the maximum rate you can accelerate with the power you have
    #return engine power and acceleration
    def calculate_max_power_acceleration(self,speed):
        excess_power = self.excess_acceleration_power(speed) #determine amount of excess engine power available for acceleration
        excess_power_acceleration = self.power_to_acceleration(excess_power,speed) #how much acceleration in m/s^2 would occur if all this power was used to accelerate
        if excess_power_acceleration>self.max_acceleration: #if acceleration is limited by acceleration limit
            acceleration = self.max_acceleration
            acceleration_power = self.acceleration_to_power(acceleration,speed) #additional engine power needed to accelerate at the maximum rate
            power_used = acceleration_power + self.calculate_static_power(speed) #total power is additional power plus power needed to maintain a steady state

        else: #acceleration is limited by engine power
            acceleration = excess_power_acceleration 
            power_used = self.max_engine_power #engine power used is the maximum possible

        return power_used,acceleration
    
    #calculate the maximum rate of deceleration at the current speed
    #return the regen power,friction power, engine power, and decceleration
    def calculate_max_power_deceleration(self,speed,brake_mode,mode):
        static_power = self.calculate_static_power(speed) #determine power to maintain current speed, this can be used for braking by not using the engine
        #"max" brake_mode, both regen and regular braking can be used, "saver", regular braking only used below brake_speed
        #"design " mode use the design limits, "max"  use the maximum limits.
        # determine max regen brake power
        max_regen_brake = self.calculate_max_regen_braking(speed)
        if brake_mode=="max" or mode=='max' or speed<self.brake_speed: #if conditions for using regular braking are met they can be used
            max_brake_power = max_regen_brake + self.max_brake #brake power without friction
        else:   #otherwise use only regen brakes
            max_brake_power = max_regen_brake
         
        max_brake_power_friction = max_brake_power + static_power #max braking power with friction

        max_brake_decceleration = self.power_to_acceleration(max_brake_power,speed) #max decceleration excluding friction
        max_brake_decceleration_friction = self.power_to_acceleration(max_brake_power_friction,speed) #max decceleration including friction 
        if mode=='design': #we wish to decelerate at a speed that won't trip anybody over
            if max_brake_decceleration_friction<=self.design_deceleration: #if we are slowing down less than the design maximum
                #our braking ability is the limit to how fast we can decelerate
                deceleration = max_brake_decceleration_friction
                brake_power = max_brake_power #brake power, excluding frictional effects
                engine_power = 0
            elif max_brake_decceleration_friction>self.design_deceleration:#if we have enough brakes to slow down more than the design maximum
                deceleration = self.design_deceleration
                needed_brake_power = self.acceleration_to_power(deceleration,speed) #needed brake power to achieve desired decceleration
                brake_power = needed_brake_power-static_power #needed brake power to achieve desired decceleration (this could actually be negative on upward inclines, requiring engine power to limit deceleration)
                if brake_power<0:
                    engine_power = brake_power
                    brake_power = 0
                else:
                    engine_power = 0
        elif mode=='max': #we wish to decelerate as fast as we can to avoid a collision
            if max_brake_decceleration<=self.max_deceleration:
                deceleration = max_brake_decceleration_friction 
                brake_power = max_brake_power
                engine_power = 0
            elif max_brake_decceleration>self.max_deceleration:#if we are slowing down as much as wheel adhesion will allow
                #we can get some extra deceleration from friction between the vehicle and the enviroment
                friction_deceleration = self.power_to_acceleration(static_power,speed)
                deceleration = self.max_deceleration + friction_deceleration
                brake_power = self.acceleration_to_power(self.max_deceleration,speed) 
                engine_power = 0

        #now determine type of brake force useds
        if max_regen_brake>=brake_power:
            regen_brake_power = brake_power
            regular_brake_power = 0

        else:
            regen_brake_power = max_regen_brake
            regular_brake_power = brake_power-max_regen_brake
        
        return regen_brake_power,regular_brake_power,engine_power,deceleration
    
    #calculate the maximum amount of regen braking power at the current speed
    def calculate_max_regen_braking(self,speed):
        if speed>=self.regen_speed: #if speed is above that required to best use regenerative braking
            max_regen_brake = self.max_regen_brake
        else: #otherwise, regenrative braking capacity will be lower
            speed_fraction = speed/self.regen_speed
            max_regen_brake = self.max_regen_brake*speed_fraction*speed_fraction #regenerative braking reduces quadratically with reduced speeed
        
        return max_regen_brake

    #how much power can the engine generate in excess of the power to maintain a static velocity
    def excess_acceleration_power(self,speed):
        static_power = self.calculate_static_power(speed) #determine power to maintain current speed
        excess_power = self.max_engine_power-static_power #determine excess power produced by engine
        return excess_power


    #convert force to power (W)
    def force_to_power(self,force,speed):
        power = force*speed
        return power

    #convert power to force (N)
    def power_to_force(self,power,speed):
        force = power/speed #force in N
        return force
    
    #convert force to acceleration (m/s^2)
    def force_to_acceleration(self,force):
        acceleration = force/self.mass #acceleration in m/s^2
        return acceleration
    
    #convert acceleration to force (N)
    def acceleration_to_force(self,acceleration):
        force = acceleration*self.mass #force in N
        return force

    #convert power to acceleration m/s^2 at a specific speed
    def power_to_acceleration(self,power,speed):
        force = self.power_to_force(power,speed)
        acceleration = self.force_to_acceleration(force)
        return acceleration
    
    #convert acceleration to power at a specific speed
    def acceleration_to_power(self,acceleration,speed):
        force = self.acceleration_to_force(acceleration)
        power = self.force_to_power(force,speed)
        return power

    






