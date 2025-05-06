pip install -U opensees xara veux

import opensees.openseespy as ops
import veux
import sys


ops.wipe()
model = ops.Model(ndm=3, ndf=6)


# create nodes according to engineering drawings
height = 14.9375
model.node(1, (  0.0,  0.0, 0.0))
model.node(2, (  33.385416,  0.0, 0.0))
model.node(3, (  64.776041,  0.0, 0.0))
model.node(4, (  99.489583,  0.0, 0.0))
model.node(5, (  134.3854,  0.0, 0.0))
model.node(6, (  174.885416,  0.0, 0.0))
model.node(7, (  0,  14.9375, 0.0))
model.node(8, (  36.92708,  height, 0.0))
model.node(9, (  64.2395,  height, 0.0))
model.node(10, (  91.65104,  height, 0.0))
model.node(11, (  119.3177083,  height, 0.0))
model.node(12, (  147.71875,  height, 0.0))
model.node(13, (  174.885416,  height, 0.0))

# supports

model.fix(1, (1, 1, 1, 1, 1, 0)) # to make it simply supported
model.fix(6, (0, 1, 1, 1, 1, 0))

for node in range(2, 6): # to prevent out of plane translation
    print(node)
    model.fix(node, (0, 0, 1, 1, 1, 0))  
for node in range(7, 14):
    print(node)
    model.fix(node, (0, 0, 1, 1, 1, 0))  


# transforms
model.geomTransf("Linear",1,(0,0,1))

# DEFINING MATERIALS AND SECTIONS
# units: kips and ft

# areas
top_area = 16 
bot_h = 0.5*(9.5/12 + 2 + 0.5/12)
bot_b = 31 + 8/12
bot_area = bot_h * bot_b
diag_b = 1+9/12
diag_h = 15
diag_area = diag_b*diag_h
side_area = diag_area 

# sections
E_conc = 4694.4 #k/ft^2 -- this is for 6.9 ksi concrete
G_conc = 2044.8 #k/ft^2
model.section("ElasticFrame", 1, E=E_conc, G=G_conc, A=bot_area, # bottom element 
              Iy=(bot_b**3*bot_h)/12, Iz=(bot_b*bot_h**3)/12, J=(bot_b**3*bot_h)/12 + (bot_b*bot_h**3)/12)
model.section("ElasticFrame", 2, E=E_conc, G=G_conc, A=top_area, # top element
              Iy=(1*16**3)/12, Iz=(1**3*16)/12, J=(1*16**3)/12 + (1**3*16)/12)
model.section("ElasticFrame", 3, E=E_conc, G=G_conc, A=diag_area, # diagonal element
              Iy=(diag_b**3*diag_h)/12, Iz=(diag_b*diag_h**3)/12, J=(diag_b**3*diag_h)/12 + (diag_b*diag_h**3)/12)
model.section("ElasticFrame", 4, E=E_conc, G=G_conc, A=side_area, # side element
              Iy=(diag_b**3*diag_h)/12, Iz=(diag_b*diag_h**3)/12, J=(diag_b**3*diag_h)/12 + (diag_b*diag_h**3)/12)

# elements
elem_type = "PrismFrame"
diag_elem_type = "PrismFrame"

# bottom elements
for i in range(1,6):
    model.element(elem_type,i,(i,i+1,1,1))

# top elements
for i in range(6,12):
    model.element(elem_type,i,(i+1,i+2), 2,1)

# side elements
model.element(elem_type, 12, (1, 7), 4,1)
model.element(elem_type, 13, (6, 13), 4,1)

# diagonal elements
model.element(diag_elem_type, 14, (1, 8), 3,1) 
model.element(diag_elem_type, 15, (2, 8), 3,1) 
model.element(diag_elem_type, 16, (2, 9), 3,1) 
model.element(diag_elem_type, 17, (3, 9), 3,1) 
model.element(diag_elem_type, 18, (3, 10), 3,1) 
model.element(diag_elem_type, 19, (4, 10), 3,1) 
model.element(diag_elem_type, 20, (4, 11), 3,1) 
model.element(diag_elem_type, 21, (5, 11), 3,1) 
model.element(diag_elem_type, 22, (5, 12), 3,1) 
model.element(diag_elem_type, 23, (6, 12), 3,1) 


# loading on nodes

conc_weight = 0.15 #k/ft^
l_bridge = 175 #ft
bot_weight = bot_area * l_bridge * conc_weight
top_weight = top_area * l_bridge * conc_weight
total_weight = bot_weight + top_weight
weight_node = total_weight/6
print("weight node = ", weight_node)

loads = {
    1: [0, -weight_node, 0, 0, 0, 0],
    2: [0, -weight_node, 0, 0, 0, 0],
    3: [0, -weight_node, 0, 0, 0, 0],
    4: [0, -weight_node, 0, 0, 0, 0],
    5: [0, -weight_node, 0, 0, 0, 0],
    6: [0, -weight_node, 0, 0, 0, 0],

    #7: [0, -500, 0, 0, 0, 0],
    #8: [0, -500, 0, 0, 0, 0],
    #9: [0, -500, 0, 0, 0, 0],
    #10: [0, -500, 0, 0, 0, 0],
    #11: [0, -500, 0, 0, 0, 0],
    #12: [0, -500, 0, 0, 0, 0],
    #13: [0, -500, 0, 0, 0, 0],
}


model.pattern("Plain", 1, "Constant")
for node, load in loads.items():
    print("node = ", node, " load = ", load)
    model.load(node, *load) 


# analysis

model.system("BandGeneral")
#model.constraints("Transformation")
model.numberer("RCM")
model.algorithm("Linear")
model.integrator("LoadControl", 1.0)
model.analysis("Static")
model.analyze(1)


for node in range(1,14):
    print("node: ", node, " disp: ", model.nodeDisp(node))

# get forces

for ele_id in range(1, 24): 
    response = model.eleResponse(ele_id, 'forces')
    #print(f"Element {ele_id} response: {response}")

axial_forces = {}
shear_forces = {}
z_forces = {}
Mx = {}
My = {}
Mz = {}


for ele_id in range(1, 24):  # Update as needed
    response = model.eleResponse(ele_id, "localForce")
    Fx_i = response[0]  # Axial at end I
    Fy_i = response[1]
    Fz_i = response[2]
    Mx_i = response[3]
    My_i = response[4]
    Mz_i = response[5]

    Fx_j = response[6]  # Axial at end J
    Fy_j = response[7]
    Fz_j = response[8]
    Mx_j = response[9]
    My_j = response[10]
    Mz_j = response[11]

    axial_forces[ele_id] = [Fx_i, Fx_j]
    shear_forces[ele_id] = [Fy_i, Fy_j]
    z_forces[ele_id] = [Fz_i, Fz_j]
    Mx[ele_id] = [Mx_i, Mx_j]
    My[ele_id] = [My_i, My_j]
    Mz[ele_id] = [Mz_i, Mz_j]


import csv

# File to write
csv_file = "element_forces.csv"

with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)

    # Write header
    writer.writerow(["Element", "End", "Fx", "Fy", "Fz", "Mx", "My", "Mz"])

    for ele_id in range(1, 24):  # Elements 1 to 23
        writer.writerow([
            ele_id, "I",
            axial_forces[ele_id][0],
            shear_forces[ele_id][0],
            z_forces[ele_id][0],
            Mx[ele_id][0],
            My[ele_id][0],
            Mz[ele_id][0]
        ])
        writer.writerow([
            "", "J",
            axial_forces[ele_id][1],
            shear_forces[ele_id][1],
            z_forces[ele_id][1],
            Mx[ele_id][1],
            My[ele_id][1],
            Mz[ele_id][1]
        ])

print(f"Force table written to {csv_file}")

print("starting veux")

artist = veux.create_artist(model, vertical=2)
artist.draw_outlines()
artist.draw_outlines(state=model.nodeDisp, scale=5)
#artist.draw_axes(extrude=True)
artist.draw_nodes()
veux.serve(artist)

