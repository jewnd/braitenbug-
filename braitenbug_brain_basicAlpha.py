
from brian2 import *
start_scope()
import matplotlib.pyplot as plt
map_size = 100
global foodx, foody, food_count, bug_plot, food_plot, sr_plot, sl_plot,outbugx,outbugy,outbugang,outfoodx,outfoody,outsrx,outsry,outslx,outsly

food_count = 0
foodx=50
foody=50
duration=1000
outbugx=np.zeros(int(duration/2))
outbugy=np.zeros(int(duration/2))
outbugang=np.zeros(int(duration/2))
outfoodx=np.zeros(int(duration/2))
outfoody=np.zeros(int(duration/2))
outsrx=np.zeros(int(duration/2))
outsry=np.zeros(int(duration/2))
outslx=np.zeros(int(duration/2))
outsly=np.zeros(int(duration/2))
x
# Sensor neurons
a = 0.02
b = 0.2
c = -65
d = 0.5

I0 = 1250
g_synpk=0.4
tau_syn = 2*ms
g_synmaxval = g_synpk/(tau_syn*exp(-1)/ms)

sensor_eqs = '''
# equations for neurons
x : 1
y : 1
x_disp : 1
y_disp : 1
foodxx : 1
foodyy : 1
mag :1
I = I0 / sqrt(((x-foodxx)**2+(y-foodyy)**2)): 1
dv/dt = (0.04*v**2 + 5*v + 140 - u + I - g_alpha*v) /ms: 1
du/dt = a*(b*v - u)/ms : 1
dg_alpha/dt = (-g_alpha/(tau_syn/ms) + z)/ms : 1
dz/dt = (-z/(tau_syn/ms))/ms : 1
'''

sensor_reset = '''
v = c
u = u + d
'''

# right sensor
sr = NeuronGroup(1, sensor_eqs, clock=Clock(0.2*ms), threshold = "v>=30", reset = sensor_reset,method='euler')
sr.v = c
sr.u = c*b
sr.x_disp = 5
sr.y_disp = 5
sr.x = sr.x_disp
sr.y = sr.y_disp
sr.foodxx = foodx
sr.foodyy = foody
sr.mag=1

# left sensor
sl = NeuronGroup(1, sensor_eqs, clock=Clock(0.2*ms), threshold = "v>=30", reset = sensor_reset,method='euler')
sl.v = c
sl.u = c*b
sl.x_disp = -5
sl.y_disp = 5
sl.x = sl.x_disp
sl.y = sl.y_disp
sl.foodxx = foodx
sl.foodyy = foody
sl.mag=1

# right bug motor neuron
sbr = NeuronGroup(1, sensor_eqs, clock=Clock(0.2*ms), threshold = "v>=30", reset = sensor_reset,method='euler')
sbr.v = c
sbr.u = c*b
sbr.foodxx = foodx
sbr.foodyy = foody
sbr.mag=0

# left bug motor neuron
sbl = NeuronGroup(1, sensor_eqs, clock=Clock(0.2*ms), threshold = "v>=30", reset = sensor_reset,method='euler')
sbl.v = c
sbl.u = c*b
sbl.foodxx = foodx
sbl.foodyy = foody
sbl.mag=0

# The virtual bug
taum = 4*ms
base_speed = 800
turn_rate = 10*Hz

bug_eqs = '''
dx/dt = speed*cos(angle)*Hz :1
dy/dt = speed*sin(angle)*Hz :1
dangle/dt = (motorr-motorl)*turn_rate :1
speed = (motorl+motorr)/2+base_speed :1
dmotorl/dt = -motorl/taum :1
dmotorr/dt = -motorr/taum :1
'''

#These are the equation  for the motor and speed
bug = NeuronGroup(1, bug_eqs, clock=Clock(0.2*ms),method='euler')
bug.motorl = 0
bug.motorr = 0
bug.angle = pi/2
bug.x = 0
bug.y = 0

# Synapses (sensors communicate with bug motor)
w = 10

syn_rl=Synapses(sr, sbl, clock=Clock(0.2*ms), model='''
                  g_synmax:1
                ''',
		on_pre='''
		z+= g_synmax
		''')


syn_rl.connect(i=[0],j=[0])
syn_rl.g_synmax=g_synmaxval

syn_lr=Synapses(sl, sbr, clock=Clock(0.2*ms), model='''
                 g_synmax:1
                ''',
		on_pre='''
		z+= g_synmax
		''')
		
syn_lr.connect(i=[0],j=[0])
syn_lr.g_synmax=g_synmaxval

syn_r = Synapses(sbr, bug, clock=Clock(0.2*ms), on_pre='motorr += w')
syn_r.connect(i=[0],j=[0])
syn_l = Synapses(sbl, bug, clock=Clock(0.2*ms), on_pre='motorl += w')
syn_l.connect(i=[0],j=[0])

f = figure(1)
bug_plot = plot(bug.x, bug.y, 'ko')
food_plot = plot(foodx, foody, 'b*')
sr_plot = plot([0], [0], 'w')
sl_plot = plot([0], [0], 'w')
# Additional update rules (not covered/possible in above eqns)

# Update the location of food
@network_operation()
def update_positions():
    global foodx, foody, food_count
    sr.x = bug.x + sr.x_disp*sin(bug.angle)+ sr.y_disp*cos(bug.angle) #right sensor x position
    sr.y = bug.y + - sr.x_disp*cos(bug.angle) + sr.y_disp*sin(bug.angle) #right sensor y position

    sl.x = bug.x +  sl.x_disp*sin(bug.angle)+sl.y_disp*cos(bug.angle) #left sensor x position
    sl.y = bug.y  - sl.x_disp*cos(bug.angle)+sl.y_disp*sin(bug.angle) #left sensor y position
    

    if ((bug.x-foodx)**2+(bug.y-foody)**2) < 16:
        food_count += 1
        foodx = randint(-map_size+10, map_size-10)
        foody = randint(-map_size+10, map_size-10)

    if (bug.x < -map_size): #hits a wall and bounce off it
        bug.x = -map_size
        bug.angle = pi - bug.angle
        
    if (bug.x > map_size):
	    bug.x = map_size
	    bug.angle = pi - bug.angle
        
    if (bug.y < -map_size):
	    bug.y = -map_size
	    bug.angle = -bug.angle
        
    if (bug.y > map_size):
	    bug.y = map_size
	    bug.angle = -bug.angle

    sr.foodxx = foodx
    sr.foodyy = foody
    sl.foodxx = foodx
    sl.foodyy = foody


#update bug and sensor location
#rotation matrix
#solve equations other than neuron groups
#where was the bug/for show_bug
@network_operation(dt=2*ms)
def update_plot(t):
    global foodx, foody, bug_plot, food_plot, sr_plot, sl_plot,outbugx,outbugy,outbugang,outfoodx,outfoody,outsrx,outsry,outslx,outsly
    indx=int(.5*t/ms+1)
    bug_plot[0].remove()
    food_plot[0].remove()
    sr_plot[0].remove()
    sl_plot[0].remove()
    bug_x_coords = [bug.x, bug.x-4*cos(bug.angle), bug.x-8*cos(bug.angle)]
    bug_y_coords = [bug.y, bug.y-4*sin(bug.angle), bug.y-8*sin(bug.angle)]
    outbugx[indx-1]=bug.x[0]
    outbugy[indx-1]=bug.y[0]
    outbugang[indx-1]=bug.angle[0]
    outfoodx[indx-1]=foodx
    outfoody[indx-1]=foody
    outsrx[indx-1]=sr.x[0]
    outsry[indx-1]=sr.y[0]
    outslx[indx-1]=sl.x[0]
    outsly[indx-1]=sl.y[0]
    bug_plot = plot(bug_x_coords, bug_y_coords, 'bo')     #bug shape
    sr_plot = plot([bug.x, sr.x], [bug.y, sr.y], 'g')
    sl_plot = plot([bug.x, sl.x], [bug.y, sl.y], 'r')
    food_plot = plot(foodx, foody, 'b*') 
    axis([-100,100,-100,100])
    draw()
    #print "."
    pause(0.01)


#ML = StateMonitor(sl, ('v', 'I'), record=True)
#MR = StateMonitor(sr, ('v', 'I'), record=True)
#MB = StateMonitor(bug, ('motorl', 'motorr', 'speed', 'angle', 'x', 'y'), record = True)
run(duration*ms,report='text')
np.save('outbugx',outbugx)
np.save('outbugy',outbugy)
np.save('outbugang',outbugang)
np.save('outfoodx',outfoodx)
np.save('outfoody',outfoody)
np.save('outsrx',outsrx)
np.save('outsry',outsry)
np.save('outslx',outslx)
np.save('outsly',outsly)
