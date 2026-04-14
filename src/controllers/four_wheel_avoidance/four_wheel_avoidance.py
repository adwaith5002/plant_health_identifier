"""four_wheel_avoidance controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot,DistanceSensor,Motor


timestep=64
# create the Robot instance.
robot = Robot()

# get the time step of the current world.

ds=[]
dsNames=['ds_right','ds_left']

for i in range(2):
    ds.append(robot.getDevice(dsNames[i]))
    ds[i].enable(timestep)
    
wheels=[]
wheelNames=['wheel1','wheel2','wheel3','wheel4']
for i in range(4):
    wheels.append(robot.getDevice(wheelNames[i]))
    wheels[i].setPosition(float('inf'))
    wheels[i].setVelocity(0.0)
    
avoidObstaclecounter=0
# You should insert a getDevice-like function in order to get the
# instance of a device of the robot. Something like:
#  motor = robot.getDevice('motorname')
#  ds = robot.getDevice('dsname')
#  ds.enable(timestep)

# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(timestep) != -1:
    # Read the sensors:
    # Enter here functions to read sensor data, like:
    #  val = ds.getValue()
    leftSpeed=1.0
    rightSpeed=1.0
    
    if avoidObstaclecounter>0:
        avoidObstaclecounter-=1
        leftSpeed=1.0
        rightSpeed=-1.0
    else:
        for i in range(2):
            if ds[i].getValue()>950.0:
                avoidObstacleCounter=100
    wheels[0].setVelocity(leftSpeed)
    wheels[1].setVelocity(rightSpeed)
    wheels[2].setVelocity(leftSpeed)
    wheels[3].setVelocity(rightSpeed)
    # Process sensor data here.

    # Enter here functions to send actuator commands, like:
    #  motor.setPosition(10.0)

# Enter here exit cleanup code.
