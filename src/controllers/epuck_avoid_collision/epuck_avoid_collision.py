"""epuck_avoid_collision controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from controller import Robot,DistanceSensor , Motor

TIME_STEP=64
MAX_SPEED=6.28
# create the Robot instance.
robot = Robot()

# get the time step of the current world.


# You should insert a getDevice-like function in order to get the
# instance of a device of the robot. Something like:
#  motor = robot.getDevice('motorname')
#  ds = robot.getDevice('dsname')
#  ds.enable(timestep)
ps=[]
psNames = [
    'ps0', 'ps1', 'ps2', 'ps3',
    'ps4','ps5','ps6','ps7'
]
    
for i in range(8):
     ps.append(robot.getDevice(psNames[i]))
     ps[i].enable(TIME_STEP)
     
left_motor=robot.getDevice('left wheel motor')
right_motor=robot.getDevice('right wheel motor')
left_motor.setPosition(float('inf'))
right_motor.setPosition(float('inf'))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)


# Main loop:
# - perform simulation steps until Webots is stopping the controller
while robot.step(TIME_STEP) != -1:
    # Read the sensors:
    psValues=[]
    for i in range(8):
        psValues.append(ps[i].getValue())
    # Enter here functions to read sensor data, like:
    #  val = ds.getValue()
    right_obstacle=psValues[0]>80.0 or psValues[1]>80.0 or psValues[2]>80.0
    left_obstacle=psValues[5]>80.0 or psValues[6]>80.0 or psValues[7]>80.0
    # Process sensor data here.

    
    leftSpeed=0.5*MAX_SPEED
    rightSpeed=0.5*MAX_SPEED
    
    
    if left_obstacle:
        leftSpeed=0.5*MAX_SPEED
        rightSpeed=-0.5*MAX_SPEED
        
    elif right_obstacle:
    # turn left
        leftSpeed  = -0.5 * MAX_SPEED
        rightSpeed = 0.5 * MAX_SPEED
        
    left_motor.setVelocity(leftSpeed)
    right_motor.setVelocity(rightSpeed)
    # Enter here functions to send actuator commands, like:
    #  motor.setPosition(10.0)

# Enter here exit cleanup code.
