#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar  1 12:15:49 2020

bug - "food and poison"

@author: jingwendeng
"""

from brian2 import *
start_scope()
import matplotlib.pyplot as plt
map_size = 100
global foodx, poisonx, foody, poisony, food_count,  bug1_plot, bug2_plot, food_plot, poison_plot, sr1_plot, sl1_plot, sr2_plot, sl2_plot,sr3_plot, sl3_plot,sr4_plot, sl4_plot,sr5_plot, sl5_plot

food_count = 0
foodx=-75
foody=0
poisonx= 75
poisony = 0
duration=700

#outbugx=np.zeros(int(duration/2))
#outbugy=np.zeros(int(duration/2))
#outbugang=np.zeros(int(duration/2))
#
#outfoodx=np.zeros(int(duration/2))
#outfoody=np.zeros(int(duration/2))
#outpoisonx=np.zeros(int(duration/2))
#outpoisony=np.zeros(int(duration/2))
#
#outsr1x=np.zeros(int(duration/2))
#outsr1y=np.zeros(int(duration/2))
#outsl1x=np.zeros(int(duration/2))
#outsl1y=np.zeros(int(duration/2))
#
#outsr2x=np.zeros(int(duration/2))
#outsr2y=np.zeros(int(duration/2))
#outsl2x=np.zeros(int(duration/2))
#outsl2y=np.zeros(int(duration/2))

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

#reduce the weight of internal inhibition
g_synmaxval0 = 0.8*g_synmaxval
#strengthen the effect of sr1&4 on motor neurons
g_synmaxval1 = 1.2*g_synmaxval

# The virtual bugs
taum = 3*ms
base_speed1 = 1400
base_speed2 = 900
turn_rate = 15*Hz


# eqs for food - bug1
sensor1_eqs = '''
x : 1
y : 1
x_disp : 1
y_disp : 1
foodxx : 1
foodyy : 1
mag :1
I = 2*I0 / sqrt(((x-foodxx)**2+(y-foodyy)**2)): 1
dv/dt = (0.04*v**2 + 5*v + 140 - u + I - 1.5*g_alpha*v) /ms: 1
du/dt = a*(b*v - u)/ms : 1
dg_alpha/dt = (-g_alpha/(tau_syn/ms) + z)/ms : 1
dz/dt = (-z/(tau_syn/ms))/ms : 1
'''

# eqs for food - bug2
sensor4_eqs = '''
x : 1
y : 1
x_disp : 1
y_disp : 1
foodxx : 1
foodyy : 1
mag :1
I = 2*I0 / sqrt(((x-foodxx)**2+(y-foodyy)**2)): 1
dv/dt = (0.04*v**2 + 5*v + 140 - u + I - 1.5*g_alpha*v) /ms: 1
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
dv/dt = (0.04*v**2 + 5*v + 140 - u + I - g_alpha*v - 0.1*g_gaba*(v+80)) /ms: 1
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

#corwd neurons to acoid bug2, inhibited by sr1, food search is primary
sensor3_eqs = '''
x : 1
y : 1
x_disp : 1
y_disp : 1
bug2xx : 1
bug2yy : 1
mag :1
I = I0 / sqrt(((x-bug2xx)**2+(y-bug2yy)**2)): 1
dv/dt = (0.04*v**2 + 5*v + 140 - u + I - g_alpha*v - 0.1*g_gaba*(v+80)) /ms: 1
du/dt = a*(b*v - u)/ms : 1
dg_alpha/dt = (-g_alpha/(tau_syn/ms) + z)/ms : 1
dg_gaba/dt = (-g_gaba/(tau_syn/ms) + z1)/ms :1
dz/dt = (-z/(tau_syn/ms))/ms : 1
dz1/dt = (-z1/(tau_syn/ms))/ms : 1
'''

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


# right sensor3
sr3 = NeuronGroup(1, sensor3_eqs, clock=Clock(0.2*ms), threshold = "v>=20", reset = sensor_reset,method='euler')
sr3.v = c
sr3.u = c*b
sr3.x_disp = 5
sr3.y_disp = 5
sr3.x = sr3.x_disp
sr3.y = sr3.y_disp
sr3.bug2xx = bug2.x
sr3.bug2yy = bug2.y
sr3.mag=1

# left sensor3
sl3 = NeuronGroup(1, sensor3_eqs, clock=Clock(0.2*ms), threshold = "v>=20", reset = sensor_reset,method='euler')
sl3.v = c
sl3.u = c*b
sl3.x_disp = -5
sl3.y_disp = 5
sl3.x = sl3.x_disp
sl3.y = sl3.y_disp
sl3.bug2xx = bug2.x
sl3.bug2yy = bug2.y
sl3.mag=1

#sensors for bug2
#lover for the food sr4

# right sensor4
sr4 = NeuronGroup(1, sensor4_eqs, clock=Clock(0.2*ms), threshold = "v>=20", reset = sensor_reset,method='euler')
sr4.v = c
sr4.u = c*b
sr4.x_disp = 4
sr4.y_disp = 6
sr4.x = sr4.x_disp
sr4.y = sr4.y_disp
sr4.foodxx = foodx
sr4.foodyy = foody
sr4.mag=1

# left sensor3
sl4 = NeuronGroup(1, sensor4_eqs, clock=Clock(0.2*ms), threshold = "v>=20", reset = sensor_reset,method='euler')
sl4.v = c
sl4.u = c*b
sl4.x_disp = -4
sl4.y_disp = 6
sl4.x = sl4.x_disp
sl4.y = sl4.y_disp
sl4.foodxx = foodx
sl4.foodyy = foody
sl4.mag=1

#agressor for bug1, but inhibited by the love for food
sensor5_eqs = '''
# equations for neurons
x : 1
y : 1
x_disp : 1
y_disp : 1
bug1xx : 1
bug1yy : 1
mag :1
I = I0 / sqrt(((x-bug1xx)**2+(y-bug1yy)**2)): 1
dv/dt = (0.04*v**2 + 5*v + 140 - u + I - g_alpha*v - 0.1*g_gaba*(v+80)) /ms: 1
du/dt = a*(b*v - u)/ms : 1
dg_alpha/dt = (-g_alpha/(tau_syn/ms) + z)/ms : 1
dg_gaba/dt = (-g_gaba/(tau_syn/ms) + z1)/ms :1
dz/dt = (-z/(tau_syn/ms))/ms : 1
dz1/dt = (-z1/(tau_syn/ms))/ms : 1
'''

# right sensor5
sr5 = NeuronGroup(1, sensor5_eqs, clock=Clock(0.2*ms), threshold = "v>=20", reset = sensor_reset,method='euler')
sr5.v = c
sr5.u = c*b
sr5.x_disp = 6
sr5.y_disp = 4
sr5.x = sr5.x_disp
sr5.y = sr5.y_disp
sr5.bug1xx = bug1.x
sr5.bug1yy = bug1.y
sr5.mag=1

# left sensor5
sl5 = NeuronGroup(1, sensor5_eqs, clock=Clock(0.2*ms), threshold = "v>=20", reset = sensor_reset,method='euler')
sl5.v = c
sl5.u = c*b
sl5.x_disp = -6
sl5.y_disp = 4
sl5.x = sl5.x_disp
sl5.y = sl5.y_disp
sl5.bug1xx = bug1.x
sl5.bug1yy = bug1.y
sl5.mag=1

#motor neuron of bug1 (x_disp&y_disp deleted)
#an aggressor for food, exploror for poison, crowd for bug2
motor1_eqs = '''
# equations for neurons
x : 1
y : 1
foodxx : 1
foodyy : 1
mag :1
I = I0 / sqrt(((x-foodxx)**2+(y-foodyy)**2)) : 1
dv/dt = (0.04*v**2 + 5*v + 140 - u + mag*I - g_alpha1*v - 1.2*g_alpha2*v - g_gaba*(v+80)) /ms: 1
du/dt = a*(b*v - u)/ms : 1
dg_alpha1/dt = (-g_alpha1/(tau_syn/ms) + z0)/ms : 1
dg_alpha2/dt = (-g_alpha2/(tau_syn/ms) + z)/ms : 1
dg_gaba/dt = (-g_gaba/(tau_syn/ms) + z1)/ms :1
dz0/dt = (-z0/(tau_syn/ms))/ms : 1
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


#motor neurons for bug2
#a lover for food and an aggressor for bug1
motor2_eqs = '''
# equations for neurons
x : 1
y : 1
foodxx : 1
foodyy : 1
mag :1
I = I0 / sqrt(((x-foodxx)**2+(y-foodyy)**2)) : 1
dv/dt = (0.04*v**2 + 5*v + 140 - u + mag*I - g_alpha*v  - 1.2*g_gaba*(v+45)) /ms: 1
du/dt = a*(b*v - u)/ms : 1
dg_alpha/dt = (-g_alpha/(tau_syn/ms) + z2)/ms : 1
dg_gaba/dt = (-g_gaba/(tau_syn/ms) + z3)/ms :1
dz2/dt = (-z2/(tau_syn/ms))/ms : 1
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


#inhibitory synapses from sr1 to sr3, food detection > avoiding bug2
syn_lr3 = Synapses(sl1,sr3, clock=Clock(0.2*ms), model='''
                  g_synmax:1
                ''',
		on_pre='''
		z1+= g_synmax
        ''')

syn_lr3.connect(i=[0],j=[0])
syn_lr3.g_synmax = g_synmaxval


syn_rl3 = Synapses(sr1,sl3, clock=Clock(0.2*ms), model='''
                  g_synmax:1
                ''',
		on_pre='''
		z1+= g_synmax
        ''')

syn_rl3.connect(i=[0],j=[0])
syn_rl3.g_synmax = g_synmaxval


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

#sr3 direct excitation for motor neurons
syn_ll2 = Synapses(sl3,sbl1, clock=Clock(0.2*ms), model='''
                  g_synmax:1
                ''',
		on_pre='''
		z0+= g_synmax
        ''')

syn_ll2.connect(i=[0],j=[0])
syn_ll2.g_synmax = g_synmaxval

syn_rr2 = Synapses(sr3,sbr1, clock=Clock(0.2*ms), model='''
                  g_synmax:1
                ''',
		on_pre='''
		z0+= g_synmax
        ''')

syn_rr2.connect(i=[0],j=[0])
syn_rr2.g_synmax = g_synmaxval

#sr4 cross inhibition to sr5
syn_lr4 = Synapses(sl4,sr5, clock=Clock(0.2*ms), model='''
                  g_synmax:1
                ''',
		on_pre='''
		z1+= g_synmax
        ''')

syn_lr4.connect(i=[0],j=[0])
syn_lr4.g_synmax = g_synmaxval

syn_rl4 = Synapses(sr4,sl5, clock=Clock(0.2*ms), model='''
                  g_synmax:1
                ''',
		on_pre='''
		z1+= g_synmax
        ''')

syn_rl4.connect(i=[0],j=[0])
syn_rl4.g_synmax = g_synmaxval


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

#sr5 cross excitation to motor neurons
syn_lr5 = Synapses(sl5,sbr2, clock=Clock(0.2*ms), model='''
                  g_synmax:1
                ''',
		on_pre='''
		z2+= g_synmax
        ''')

syn_lr5.connect(i=[0],j=[0])
syn_lr5.g_synmax = g_synmaxval

syn_rl5 = Synapses(sr5,sbl2, clock=Clock(0.2*ms), model='''
                  g_synmax:1
                ''',
		on_pre='''
		z2+= g_synmax
        ''')

syn_rl5.connect(i=[0],j=[0])
syn_rl5.g_synmax = g_synmaxval


#motor neuron to bug1
syn_r1 = Synapses(sbr1, bug1, clock=Clock(0.2*ms), on_pre='motorr += w')
syn_r1.connect(i=[0],j=[0])
syn_l1 = Synapses(sbl1, bug1, clock=Clock(0.2*ms), on_pre='motorl += w')
syn_l1.connect(i=[0],j=[0])

#motor neuron to bug2
syn_r2 = Synapses(sbr2, bug2, clock=Clock(0.2*ms), on_pre='motorr += w')
syn_r2.connect(i=[0],j=[0])
syn_l2 = Synapses(sbl2, bug2, clock=Clock(0.2*ms), on_pre='motorl += w')
syn_l2.connect(i=[0],j=[0])


#plot
f = figure(1)
bug1_plot = plot(bug1.x, bug1.y, 'ko')
bug2_plot = plot(bug2.x, bug2.y, 'ko')
food_plot = plot(foodx, foody, 'b*')
poison_plot = plot(poisonx, poisony, 'r*')
sr1_plot = plot([0], [25], 'p')
sl1_plot = plot([0], [25], 'p')
sr2_plot = plot([0], [25], 'g')
sl2_plot = plot([0], [25], 'g')
sr3_plot = plot([0], [25], 'y')
sl3_plot = plot([0], [25], 'y')
sr4_plot = plot([0], [-25], 'b')
sl4_plot = plot([0], [-25], 'b')
sr5_plot = plot([0], [-25], 'k')
sl5_plot = plot([0], [-25], 'k')

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
    
    sr3.x = bug1.x + sr3.x_disp*sin(bug1.angle)+ sr3.y_disp*cos(bug1.angle) #right sensor2 x position
    sr3.y = bug1.y + - sr3.x_disp*cos(bug1.angle) + sr3.y_disp*sin(bug1.angle) #right sensor y position

    sl3.x = bug1.x +  sl3.x_disp*sin(bug1.angle)+sl3.y_disp*cos(bug1.angle) #left sensor2 x position
    sl3.y = bug1.y  - sl3.x_disp*cos(bug1.angle)+sl3.y_disp*sin(bug1.angle) #left sensor y position 
    
    sr4.x = bug2.x + sr4.x_disp*sin(bug2.angle)+ sr4.y_disp*cos(bug2.angle) #right sensor2 x position
    sr4.y = bug2.y + - sr4.x_disp*cos(bug2.angle) + sr4.y_disp*sin(bug2.angle) #right sensor y position

    sl4.x = bug2.x +  sl4.x_disp*sin(bug2.angle)+sl4.y_disp*cos(bug2.angle) #left sensor2 x position
    sl4.y = bug2.y  - sl4.x_disp*cos(bug2.angle)+sl4.y_disp*sin(bug2.angle) #left sensor y position 

    sr5.x = bug2.x + sr5.x_disp*sin(bug2.angle)+ sr5.y_disp*cos(bug2.angle) #right sensor2 x position
    sr5.y = bug2.y + - sr5.x_disp*cos(bug2.angle) + sr5.y_disp*sin(bug2.angle) #right sensor y position

    sl5.x = bug2.x +  sl5.x_disp*sin(bug2.angle)+sl5.y_disp*cos(bug2.angle) #left sensor2 x position
    sl5.y = bug2.y  - sl5.x_disp*cos(bug2.angle)+sl5.y_disp*sin(bug2.angle) #left sensor y position 

    if ((bug1.x-foodx)**2+(bug1.y-foody)**2) < 16:
        food_count += 1
        foodx = randint(-map_size+15, map_size-15)
        foody = randint(-map_size+15, map_size-15)
        poisonx = randint(-map_size+15, map_size-15)
        poisony = randint(-map_size+15, map_size-15)
    
    if ((foodx - poisonx)**2+(foody - poisony)**2) < 2500:
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
        
    sr1.foodxx = foodx
    sr1.foodyy = foody
    sl1.foodxx = foodx
    sl1.foodyy = foody
    sr2.poisonxx = poisonx
    sr2.poisonyy = poisony
    sl2.poisonxx = poisonx
    sl2.poisonyy = poisony
    sr3.bug2xx = bug2.x
    sr3.bug2yy = bug2.y
    sl3.bug2xx = bug2.x
    sl3.bug2yy = bug2.y
    sl4.foodxx = foodx
    sl4.foodyy = foody
    sr4.foodxx = foodx
    sr4.foodyy = foody
    sr5.bug1xx = bug1.x
    sr5.bug1yy = bug1.y
    sl5.bug1xx = bug1.x
    sl5.bug1yy = bug1.y

#update bug and sensor location
#rotation matrix
#solve equations other than neuron groups
#where was the bug/for show_bug
@network_operation(dt=2*ms)
def update_plot(t):
    global foodx, foody, poisonx, poisony, poison_plot, bug1_plot, bug2_plot,food_plot, sr1_plot, sl1_plot, sr2_plot, sl2_plot,sr3_plot, sl3_plot,sr4_plot, sl4_plot,sr5_plot, sl5_plot
    indx=int(.5*t/ms+1)
    bug1_plot[0].remove()
    bug2_plot[0].remove()
    food_plot[0].remove()
    poison_plot[0].remove()
    sr1_plot[0].remove()
    sl1_plot[0].remove()
    sr2_plot[0].remove()
    sl2_plot[0].remove()
    sr3_plot[0].remove()
    sl3_plot[0].remove()
    sr4_plot[0].remove()
    sl4_plot[0].remove()
    sr5_plot[0].remove()
    sl5_plot[0].remove()
    bug1_x_coords = [bug1.x, bug1.x-4*cos(bug1.angle), bug1.x-8*cos(bug1.angle)]
    bug1_y_coords = [bug1.y, bug1.y-4*sin(bug1.angle), bug1.y-8*sin(bug1.angle)]
    bug2_x_coords = [bug2.x, bug2.x-4*cos(bug2.angle), bug2.x-8*cos(bug2.angle)]
    bug2_y_coords = [bug2.y, bug2.y-4*sin(bug2.angle), bug2.y-8*sin(bug2.angle)]

#    outbugx[indx-1]=bug.x[0]
#    outbugy[indx-1]=bug.y[0]
#    outbugang[indx-1]=bug.angle[0]
#    outfoodx[indx-1]=foodx
#    outfoody[indx-1]=foody
#    outsr1x[indx-1]=sr1.x[0]
#    outsr1y[indx-1]=sr1.y[0]
#    outsl1x[indx-1]=sl1.x[0]
#    outsl1y[indx-1]=sl1.y[0]
#    outsr2x[indx-1]=sr2.x[0]
#    outsr2y[indx-1]=sr2.y[0]
#    outsl2x[indx-1]=sl2.x[0]
#    outsl2y[indx-1]=sl2.y[0]
    bug1_plot = plot(bug1_x_coords, bug1_y_coords, 'bo') 
    bug2_plot = plot(bug2_x_coords, bug2_y_coords, 'ro')     #bug shape
    sr1_plot = plot([bug1.x, sr1.x], [bug1.y, sr1.y], 'p')
    sl1_plot = plot([bug1.x, sl1.x], [bug1.y, sl1.y], 'p')
    sr2_plot = plot([bug1.x, sr2.x], [bug1.y, sr2.y], 'g')
    sl2_plot = plot([bug1.x, sl2.x], [bug1.y, sl2.y], 'g')
    sr3_plot = plot([bug1.x, sr3.x], [bug1.y, sr3.y], 'y')
    sl3_plot = plot([bug1.x, sl3.x], [bug1.y, sl3.y], 'y')
    sr4_plot = plot([bug2.x, sr4.x], [bug2.y, sr4.y], 'b')
    sl4_plot = plot([bug2.x, sl4.x], [bug2.y, sl4.y], 'b')
    sr5_plot = plot([bug2.x, sr5.x], [bug2.y, sr5.y], 'k')
    sl5_plot = plot([bug2.x, sl5.x], [bug2.y, sl5.y], 'k')
    food_plot = plot(foodx, foody, 'b*') 
    poison_plot = plot(poisonx,poisony,'r*')
    axis([-100,100,-100,100])
    draw()
    #print "."
    pause(0.05)


run(duration*ms,report='text')
#duration0=0.1
#MB = StateMonitor(bug, ('motorl', 'motorr', 'speed', 'angle', 'x', 'y'), record = True)
#np.save('outbugx',outbugx)
#np.save('outbugy',outbugy)
#np.save('outbugang',outbugang)
#np.save('outfoodx',outfoodx)
#np.save('outfoody',outfoody)
#np.save('outsr1x',outsr1x)
#np.save('outsr1y',outsr1y)
#np.save('outsl1x',outsl1x)
#np.save('outsl1y',outsl1y)
#np.save('outsr2x',outsr2x)
#np.save('outsr2y',outsr2y)
#np.save('outsl2x',outsl2x)
#np.save('outsl2y',outsl2y)