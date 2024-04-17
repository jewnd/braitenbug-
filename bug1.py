#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 12:06:29 2020

-Just the bug1 

@author: jingwendeng
"""

from brian2 import *
start_scope()
import matplotlib.pyplot as plt
map_size = 100
global foodx, poisonx, foody, poisony, food_count,  bug1_plot, food_plot,  sr1_plot, sl1_plot, sr2_plot, sl2_plot

food_count = 0
foodx=-75
foody=0
poisonx= 75
poisony = 0
duration=1000

# Sensor neurons for food
#basic alpha sensors for the aggressor
a = 0.02
b = 0.2
c = -65
d = 0.5

I0 = 1250
g_synpk=0.4
tau_syn = 1*ms


g_synmaxval = g_synpk/(tau_syn*exp(-1)/ms)

# The virtual bugs
taum = 3*ms
base_speed1 = 1400
turn_rate = 15*Hz


# eqs for food - bug1
# I and g_alpha*v were doubeled to increase the stimulus from the food
sensor1_eqs = '''
x : 1
y : 1
x_disp : 1
y_disp : 1
foodxx : 1
foodyy : 1
mag :1
I = 2*I0 / sqrt(((x-foodxx)**2+(y-foodyy)**2)): 1
dv/dt = (0.04*v**2 + 5*v + 140 - u + I - 2*g_alpha*v) /ms: 1
du/dt = a*(b*v - u)/ms : 1
dg_alpha/dt = (-g_alpha/(tau_syn/ms) + z)/ms : 1
dz/dt = (-z/(tau_syn/ms))/ms : 1
'''

sensor_reset = '''
v = c
u = u + d
'''

# right sensor1
sr1 = NeuronGroup(1, sensor1_eqs, clock=Clock(0.2*ms), threshold = "v>=0", reset = sensor_reset,method='euler')
sr1.v = c
sr1.u = c*b
sr1.x_disp = 6
sr1.y_disp = 4
sr1.x = sr1.x_disp
sr1.y = sr1.y_disp
sr1.foodxx = foodx
sr1.foodyy = foody
sr1.mag=1

# left sensor1
sl1 = NeuronGroup(1, sensor1_eqs, clock=Clock(0.2*ms), threshold = "v>=0", reset = sensor_reset,method='euler')
sl1.v = c
sl1.u = c*b
sl1.x_disp = -6
sl1.y_disp = 4
sl1.x = sl1.x_disp
sl1.y = sl1.y_disp
sl1.foodxx = foodx
sl1.foodyy = foody
sl1.mag=1

#Sensor neurons for poison
#detect poison and guide motor neurons to aviod it
#inhibited by food sensors to ensure that the bug primarily tracks food
#inhibition from SR&SL1 was weakened by multiplying 0.3, to ensure this set of sensors works
sensor2_eqs = '''
# equations for neurons
x : 1
y : 1
x_disp : 1
y_disp : 1
poisonxx : 1
poisonyy : 1
mag :1
I = I0 / sqrt(((x-poisonxx)**2+(y-poisonyy)**2)): 1
dv/dt = (0.04*v**2 + 5*v + 140 - u + I - g_alpha*v - 0.3*g_gaba*(v+80)) /ms: 1
du/dt = a*(b*v - u)/ms : 1
dg_alpha/dt = (-g_alpha/(tau_syn/ms) + z)/ms : 1
dg_gaba/dt = (-g_gaba/(tau_syn/ms) + z1)/ms :1
dz/dt = (-z/(tau_syn/ms))/ms : 1
dz1/dt = (-z1/(tau_syn/ms))/ms : 1
'''


# right sensor2
sr2 = NeuronGroup(1, sensor2_eqs, clock=Clock(0.2*ms), threshold = "v>=20", reset = sensor_reset,method='euler')
sr2.v = c
sr2.u = c*b
sr2.x_disp = 4
sr2.y_disp = 6
sr2.x = sr2.x_disp
sr2.y = sr2.y_disp
sr2.poisonxx = poisonx
sr2.poisonyy = poisony
sr2.mag=1

# left sensor2
sl2 = NeuronGroup(1, sensor2_eqs, clock=Clock(0.2*ms), threshold = "v>=20", reset = sensor_reset,method='euler')
sl2.v = c
sl2.u = c*b
sl2.x_disp = -4
sl2.y_disp = 6
sl2.x = sl2.x_disp
sl2.y = sl2.y_disp
sl2.poisonxx = poisonx
sl2.poisonyy = poisony
sl2.mag=1

bug1_eqs = '''
dx/dt = speed*cos(angle)*Hz :1
dy/dt = speed*sin(angle)*Hz :1
dangle/dt = (motorr-motorl)*turn_rate :1
speed = (motorl+motorr)/2+base_speed1 :1
dmotorl/dt = -motorl/taum :1
dmotorr/dt = -motorr/taum :1
'''

#These are the equations  for the motor and speed
bug1 = NeuronGroup(1, bug1_eqs, clock=Clock(0.2*ms),method='euler')
bug1.motorl = 0
bug1.motorr = 0
bug1.angle = pi/2
bug1.x = 0
bug1.y = 25

#motor neuron of bug1 (x_disp&y_disp deleted)
#an aggressor for food, exploror for poison, crowd for bug2
#the connection to SL&SR1 and SL&SR2 is adjusted to make sure food searching is the primary task
motor1_eqs = '''
# equations for neurons
x : 1
y : 1
foodxx : 1
foodyy : 1
mag :1
I = 1.2*I0 / sqrt(((x-foodxx)**2+(y-foodyy)**2)) : 1
dv/dt = (0.04*v**2 + 5*v + 140 - u + mag*I - 1.2*g_alpha2*v - g_gaba*(v+80)) /ms: 1
du/dt = a*(b*v - u)/ms : 1
dg_alpha2/dt = (-g_alpha2/(tau_syn/ms) + z)/ms : 1
dg_gaba/dt = (-g_gaba/(tau_syn/ms) + z1)/ms :1
dz/dt = (-z/(tau_syn/ms))/ms : 1
dz1/dt = (-z1/(tau_syn/ms))/ms : 1
'''

# right bug1 motor neuron
sbr1 = NeuronGroup(1, motor1_eqs, clock=Clock(0.2*ms), threshold = "v>=20", reset = sensor_reset,method='euler')
sbr1.v = c
sbr1.u = c*b
sbr1.foodxx = foodx
sbr1.foodyy = foody
sbr1.mag=0

# left bug1 motor neuron
sbl1 = NeuronGroup(1, motor1_eqs, clock=Clock(0.2*ms), threshold = "v>=20", reset = sensor_reset,method='euler')
sbl1.v = c
sbl1.u = c*b
sbl1.foodxx = foodx
sbl1.foodyy = foody
sbl1.mag=0

# Synapses (sensors communicate with bug motor)
w = 10

#inhibitory synapses from sr1 to sr2, food detection > poison detection
syn_ll1 = Synapses(sl1,sl2, clock=Clock(0.2*ms), model='''
                  g_synmax:1
                ''',
		on_pre='''
		z1+= g_synmax
        ''')

syn_ll1.connect(i=[0],j=[0])
syn_ll1.g_synmax = g_synmaxval

syn_rr1 = Synapses(sr1,sr2, clock=Clock(0.2*ms), model='''
                  g_synmax:1
                ''',
		on_pre='''
		z1+= g_synmax
        ''')

syn_rr1.connect(i=[0],j=[0])
syn_rr1.g_synmax = g_synmaxval

#sr1 to motor neurons
syn_rl1=Synapses(sr1, sbl1, clock=Clock(0.2*ms), model='''
                  g_synmax:1
                ''',
		on_pre='''
		z+= g_synmax
		''')

syn_rl2=Synapses(sr2, sbl1, clock=Clock(0.2*ms), model='''
                  g_synmax:1
                ''',
		on_pre='''
		z1+= g_synmax
		''')

syn_rl1.connect(i=[0],j=[0])
syn_rl2.connect(i=[0],j=[0])
syn_rl1.g_synmax=g_synmaxval
syn_rl2.g_synmax=g_synmaxval


syn_lr1=Synapses(sl1, sbr1, clock=Clock(0.2*ms), model='''
                 g_synmax:1
                ''',
		on_pre='''
		z+= g_synmax
		''')

syn_lr2=Synapses(sl2, sbr1, clock=Clock(0.2*ms), model='''
                 g_synmax:1
                ''',
		on_pre='''
		z1+= g_synmax
		''')
		
syn_lr1.connect(i=[0],j=[0])
syn_lr2.connect(i=[0],j=[0])
syn_lr1.g_synmax=g_synmaxval
syn_lr2.g_synmax=g_synmaxval

#motor neuron to bug1
syn_r1 = Synapses(sbr1, bug1, clock=Clock(0.2*ms), on_pre='motorr += w')
syn_r1.connect(i=[0],j=[0])
syn_l1 = Synapses(sbl1, bug1, clock=Clock(0.2*ms), on_pre='motorl += w')
syn_l1.connect(i=[0],j=[0])

#plot
f = figure(1)
bug1_plot = plot(bug1.x, bug1.y, 'ko')
food_plot = plot(foodx, foody, 'b*')
poison_plot = plot(poisonx, poisony, 'r*')
sr1_plot = plot([0], [25], 'p')
sl1_plot = plot([0], [25], 'p')
sr2_plot = plot([0], [25], 'g')
sl2_plot = plot([0], [25], 'g')

# Update the location of food and poison
@network_operation()
def update_positions():
    global foodx, foody, poisonx, poisony, food_count
    sr1.x = bug1.x + sr1.x_disp*sin(bug1.angle)+ sr1.y_disp*cos(bug1.angle) #right sensor1 x position
    sr1.y = bug1.y + - sr1.x_disp*cos(bug1.angle) + sr1.y_disp*sin(bug1.angle) #right sensor y position

    sl1.x = bug1.x +  sl1.x_disp*sin(bug1.angle)+sl1.y_disp*cos(bug1.angle) #left sensor1 x position
    sl1.y = bug1.y  - sl1.x_disp*cos(bug1.angle)+sl1.y_disp*sin(bug1.angle) #left sensor y position
    
    sr2.x = bug1.x + sr2.x_disp*sin(bug1.angle)+ sr2.y_disp*cos(bug1.angle) #right sensor2 x position
    sr2.y = bug1.y + - sr2.x_disp*cos(bug1.angle) + sr2.y_disp*sin(bug1.angle) #right sensor y position

    sl2.x = bug1.x +  sl2.x_disp*sin(bug1.angle)+sl2.y_disp*cos(bug1.angle) #left sensor2 x position
    sl2.y = bug1.y  - sl2.x_disp*cos(bug1.angle)+sl2.y_disp*sin(bug1.angle) #left sensor y position 
    if ((bug1.x-foodx)**2+(bug1.y-foody)**2) < 16:
        food_count += 1
        foodx = randint(-map_size+15, map_size-15)
        foody = randint(-map_size+15, map_size-15)
        poisonx = randint(-map_size+15, map_size-15)
        poisony = randint(-map_size+15, map_size-15)
        
    if ((foodx - poisonx)**2+(foody - poisony)**2) < 400:
        food_count += 1
        foodx = randint(-map_size+15, map_size-15)
        foody = randint(-map_size+15, map_size-15)
        poisonx = randint(-map_size+15, map_size-15)
        poisony = randint(-map_size+15, map_size-15)        

    if (bug1.x < -map_size): #hits a wall and bounce off it
        bug1.x = -map_size
        bug1.angle = pi - bug1.angle
        
    if (bug1.x > map_size):
	    bug1.x = map_size
	    bug1.angle = pi - bug1.angle
        
    if (bug1.y < -map_size):
	    bug1.y = -map_size
	    bug1.angle = -bug1.angle
        
    if (bug1.y > map_size):
	    bug1.y = map_size
	    bug1.angle = -bug1.angle
  
    sr1.foodxx = foodx
    sr1.foodyy = foody
    sl1.foodxx = foodx
    sl1.foodyy = foody
    sr2.poisonxx = poisonx
    sr2.poisonyy = poisony
    sl2.poisonxx = poisonx
    sl2.poisonyy = poisony

@network_operation(dt=2*ms)
def update_plot(t):
    global foodx, foody, poisonx, poisony, poison_plot, bug1_plot, bug2_plot,food_plot, sr1_plot, sl1_plot, sr2_plot, sl2_plot,sr3_plot, sl3_plot,sr4_plot, sl4_plot,sr5_plot, sl5_plot
    indx=int(.5*t/ms+1)
    bug1_plot[0].remove()
    food_plot[0].remove()
    poison_plot[0].remove()
    sr1_plot[0].remove()
    sl1_plot[0].remove()
    sr2_plot[0].remove()
    sl2_plot[0].remove()
    bug1_x_coords = [bug1.x, bug1.x-4*cos(bug1.angle), bug1.x-8*cos(bug1.angle)]
    bug1_y_coords = [bug1.y, bug1.y-4*sin(bug1.angle), bug1.y-8*sin(bug1.angle)]
    bug1_plot = plot(bug1_x_coords, bug1_y_coords, 'bo') 
    sr1_plot = plot([bug1.x, sr1.x], [bug1.y, sr1.y], 'p')
    sl1_plot = plot([bug1.x, sl1.x], [bug1.y, sl1.y], 'p')
    sr2_plot = plot([bug1.x, sr2.x], [bug1.y, sr2.y], 'g')
    sl2_plot = plot([bug1.x, sl2.x], [bug1.y, sl2.y], 'g')

    food_plot = plot(foodx, foody, 'b*') 
    poison_plot = plot(poisonx,poisony,'r*')
    axis([-100,100,-100,100])
    draw()
    #print "."
    pause(0.05)


run(duration*ms,report='text')
