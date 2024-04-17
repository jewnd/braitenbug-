#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 16:10:15 2020

@author: jingwendeng
"""

from brian2 import *
start_scope()
import matplotlib.pyplot as plt
map_size = 100
global foodx, foody, food_count,  bug2_plot, food_plot,  sr4_plot, sl4_plot

food_count = 0
foodx=-75
foody=0
duration=1000

# Sensor neurons for food
#basic alpha sensors for the aggressor
a = 0.02
b = 0.2
c = -65
d = 0.5

I0 = 1250.
g_synpk=0.4
tau_syn = 1*ms

g_synmaxval = g_synpk/(tau_syn*exp(-1)/ms)

# The virtual bugs
taum = 3*ms
base_speed2 = 900
turn_rate = 15*Hz

# eqs for food - bug2
sensor4_eqs = '''
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

# right sensor4
sr4 = NeuronGroup(1, sensor4_eqs, clock=Clock(0.2*ms), threshold = "v>=20", reset = sensor_reset,method='euler')
sr4.v = c
sr4.u = c*b
sr4.x_disp = 5
sr4.y_disp = 5
sr4.x = sr4.x_disp
sr4.y = sr4.y_disp
sr4.foodxx = foodx
sr4.foodyy = foody
sr4.mag=1

# left sensor3
sl4 = NeuronGroup(1, sensor4_eqs, clock=Clock(0.2*ms), threshold = "v>=20", reset = sensor_reset,method='euler')
sl4.v = c
sl4.u = c*b
sl4.x_disp = -5
sl4.y_disp = 5
sl4.x = sl4.x_disp
sl4.y = sl4.y_disp
sl4.foodxx = foodx
sl4.foodyy = foody
sl4.mag=1


bug2_eqs = '''
dx/dt = speed*cos(angle)*Hz :1
dy/dt = speed*sin(angle)*Hz :1
dangle/dt = (motorr-motorl)*turn_rate :1
speed = (motorl+motorr)/2+base_speed2 :1
dmotorl/dt = -motorl/taum :1
dmotorr/dt = -motorr/taum :1
'''


#These are the equations  for the motor and speed
bug2 = NeuronGroup(1, bug2_eqs, clock=Clock(0.2*ms),method='euler')
bug2.motorl = 0
bug2.motorr = 0
bug2.angle = pi/2
bug2.x = 0
bug2.y = -25

motor2_eqs = '''
# equations for neurons
x : 1
y : 1
foodxx : 1
foodyy : 1
mag :1
I = I0 / sqrt(((x-foodxx)**2+(y-foodyy)**2)) : 1
dv/dt = (0.04*v**2 + 5*v + 140 - u + mag*I  - g_gaba*(v+45)) /ms: 1
du/dt = a*(b*v - u)/ms : 1
dg_gaba/dt = (-g_gaba/(tau_syn/ms) + z3)/ms :1
dz3/dt = (-z3/(tau_syn/ms))/ms : 1
'''

# right bug2 motor neuron
sbr2 = NeuronGroup(1, motor2_eqs, clock=Clock(0.2*ms), threshold = "v>=20", reset = sensor_reset,method='euler')
sbr2.v = c
sbr2.u = c*b
sbr2.foodxx = foodx
sbr2.foodyy = foody
sbr2.mag=0

# left bug2 motor neuron
sbl2 = NeuronGroup(1, motor2_eqs, clock=Clock(0.2*ms), threshold = "v>=20", reset = sensor_reset,method='euler')
sbl2.v = c
sbl2.u = c*b
sbl2.foodxx = foodx
sbl2.foodyy = foody
sbl2.mag=0


# Synapses (sensors communicate with bug motor)
w = 10

#sr4 direct inhibition to motor neurons
syn_ll3 = Synapses(sl4,sbl2, clock=Clock(0.2*ms), model='''
                  g_synmax:1
                ''',
		on_pre='''
		z3+= g_synmax
        ''')

syn_ll3.connect(i=[0],j=[0])
syn_ll3.g_synmax = g_synmaxval

syn_rr3 = Synapses(sr4,sbr2, clock=Clock(0.2*ms), model='''
                  g_synmax:1
                ''',
		on_pre='''
		z3+= g_synmax
        ''')

syn_rr3.connect(i=[0],j=[0])
syn_rr3.g_synmax = g_synmaxval

#motor neuron to bug2
syn_r2 = Synapses(sbr2, bug2, clock=Clock(0.2*ms), on_pre='motorr += w')
syn_r2.connect(i=[0],j=[0])
syn_l2 = Synapses(sbl2, bug2, clock=Clock(0.2*ms), on_pre='motorl += w')
syn_l2.connect(i=[0],j=[0])


#plot
f = figure(1)
bug2_plot = plot(bug2.x, bug2.y, 'ko')
food_plot = plot(foodx, foody, 'b*')
sr4_plot = plot([0], [-25], 'b')
sl4_plot = plot([0], [-25], 'b')

@network_operation()
def update_positions():
    global foodx, foody, food_count
    sr4.x = bug2.x + sr4.x_disp*sin(bug2.angle)+ sr4.y_disp*cos(bug2.angle) #right sensor2 x position
    sr4.y = bug2.y + - sr4.x_disp*cos(bug2.angle) + sr4.y_disp*sin(bug2.angle) #right sensor y position

    sl4.x = bug2.x +  sl4.x_disp*sin(bug2.angle)+sl4.y_disp*cos(bug2.angle) #left sensor2 x position
    sl4.y = bug2.y  - sl4.x_disp*cos(bug2.angle)+sl4.y_disp*sin(bug2.angle) #left sensor y position 

    if (bug2.x < -map_size): #hits a wall and bounce off it
        bug2.x = -map_size
        bug2.angle = pi - bug2.angle
        
    if (bug2.x > map_size):
	    bug2.x = map_size
	    bug2.angle = pi - bug2.angle
        
    if (bug2.y < -map_size):
	    bug2.y = -map_size
	    bug2.angle = -bug2.angle
        
    if (bug2.y > map_size):
	    bug2.y = map_size
	    bug2.angle = -bug2.angle
        
    sl4.foodxx = foodx
    sl4.foodyy = foody
    sr4.foodxx = foodx
    sr4.foodyy = foody
    
@network_operation(dt=2*ms)
def update_plot(t):
    global foodx, foody,  bug2_plot,food_plot, sr4_plot, sl4_plot
    indx=int(.5*t/ms+1)
    bug2_plot[0].remove()
    food_plot[0].remove()
    sr4_plot[0].remove()
    sl4_plot[0].remove()
    bug2_x_coords = [bug2.x, bug2.x-4*cos(bug2.angle), bug2.x-8*cos(bug2.angle)]
    bug2_y_coords = [bug2.y, bug2.y-4*sin(bug2.angle), bug2.y-8*sin(bug2.angle)]
    bug2_plot = plot(bug2_x_coords, bug2_y_coords, 'ro')     #bug shape
    sr4_plot = plot([bug2.x, sr4.x], [bug2.y, sr4.y], 'b')
    sl4_plot = plot([bug2.x, sl4.x], [bug2.y, sl4.y], 'b')
    food_plot = plot(foodx, foody, 'b*') 

    axis([-100,100,-100,100])
    draw()
    #print "."
    pause(0.05)


run(duration*ms,report='text')
#duration0=0.1
