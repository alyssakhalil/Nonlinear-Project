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
    #print(node)
    model.fix(node, (0, 0, 1, 1, 1, 1))  
for node in range(7, 14):
    #print(node)
    model.fix(node, (0, 0, 1, 1, 1, 1))  

# transforms
model.geomTransf("Linear",1,(0,0,1))

# DEFINING MATERIALS AND SECTIONS
# units: kips and ft

# areas -- all units in ft
top_b = 16
top_h = 1
top_area = top_b * top_h
top_Iy = (top_b**3 * top_h)/12
top_Iz = (top_b * top_h**3)/12

bot_h = 2+(1/2)/12
bot_b = 31 + 8/12
bot_area = 0.5 * bot_h * bot_b
bot_Iy = (bot_h * bot_b ** 3)/48
bot_Iz = (bot_b * bot_h ** 3)/36

diag_b = 1+9/12
diag_h = 2
diag_area = diag_b*diag_h
diag_Iz = (diag_b**3 * diag_h)/12
diag_Iy = (diag_b * diag_h**3)/12

side_b = 1+9/12
side_h= 3
side_area = side_b + side_h 
side_Iz = (side_b**3 * side_h)/12
side_Iy = (side_b * side_h**3)/12

# sections
E_conc = 4695*12*12 #k/ft^2 -- this is for 6 ksi concrete
poisson_ratio = 0.15 # assumed
G_conc = E_conc/(2*(1+poisson_ratio)) #k/ft^2

model.section("ElasticFrame", 1, E=E_conc, G=G_conc, A=bot_area, # bottom element 
              Iy=bot_Iy, Iz=bot_Iz, J=bot_Iy + bot_Iz)

model.section("ElasticFrame", 2, E=E_conc, G=G_conc, A=top_area, # top element
              Iy=top_Iy, Iz=top_Iz, J=top_Iy + top_Iz)

model.section("ElasticFrame", 3, E=E_conc, G=G_conc, A=diag_area, # diagonal element
              Iy=diag_Iy, Iz=diag_Iz, J=diag_Iy + diag_Iz)

model.section("ElasticFrame", 4, E=E_conc, G=G_conc, A=side_area, # side element
              Iy=side_Iy, Iz = side_Iz, J=side_Iy + side_Iz)



# define fiber element materials -- CHECK MATERIALS WITH DRAWINGS

model.uniaxialMaterial("Concrete01", 201, -6.0, -0.004, -5.0, -0.014) # core conc -- confined
model.uniaxialMaterial("Concrete01", 202, -5.0, -0.002, -0.0, -0.006) # cover conc -- unconfined
fy =    60.0*12*12;      # Yield stress [k/ft^2]
E  = 29000.0*12*12;      # Young's modulus [k/ft^2]
model.uniaxialMaterial("Steel01", 203, fy, E, 0.01)



# define fiber sections -- CHECK COORDINATES



# define fiber section for diagonal

# ------------------------------------------
# set some parameters -- units in k and ft
colWidth = diag_b
colDepth = diag_h
cover =  2/12
Ds       =  1.75/12      # diameter of PT bars
As = (1/4)*3.1415*Ds**2 # area of pt bars

# some variables derived from the parameters
y1 = colDepth/2.0
z1 = colWidth/2.0
GJ = G_conc * (diag_Iy + diag_Iz)

torsion_GJ_diag = G_conc * (diag_Iy + diag_Iz)
torsion_GJ_side = G_conc * (side_Iy + side_Iz)

torsion_GJ_diag = 100000000
torsion_GJ_side = 100000000

# Use Elastic uniaxial material for torsion
model.uniaxialMaterial("Elastic", 1001, torsion_GJ_diag)  # for diagonal
model.uniaxialMaterial("Elastic", 1002, torsion_GJ_side)  # for side

model.section("Fiber", 5, "-torsion", 1001) 
#model.section("Fiber", 5, "-torsion", GJ)

# Add the concrete core fibers
model.patch("rect", 201, 10, 1, cover-y1, cover-z1, y1-cover, z1-cover, section=5)
# Add the concrete cover fibers (top, bottom, left, right)
model.patch("rect", 202, 10, 1, -y1, z1-cover, y1, z1, section=5)
model.patch("rect", 202, 10, 1, -y1, -z1, y1, cover-z1, section=5)
model.patch("rect", 202,  2, 1, -y1, cover-z1, cover-y1, z1-cover, section=5)
model.patch("rect", 202,  2, 1,  y1-cover, cover-z1, y1, z1-cover, section=5)
# Add the reinforcing fibers (left, middle, right, section=1)
model.layer("straight", 203, 3, As, y1-cover, z1-cover, y1-cover, cover-z1, section=5)
model.layer("straight", 203, 2, As,      0.0, z1-cover,      0.0, cover-z1, section=5)
model.layer("straight", 203, 3, As, cover-y1, z1-cover, cover-y1, cover-z1, section=5)


# define fiber section for side

# ------------------------------------------
# set some parameters -- units in k and ft
colWidth = side_b
colDepth = side_h
cover =  2/12
Ds       =  1.75/12      # diameter of PT bars
As = (1/4)*3.1415*Ds**2 # area of pt bars

# some variables derived from the parameters
y1 = colDepth/2.0
z1 = colWidth/2.0

model.section("Fiber", 6, "-torsion", 1002)
# Add the concrete core fibers
model.patch("rect", 201, 10, 1, cover-y1, cover-z1, y1-cover, z1-cover, section=6)
# Add the concrete cover fibers (top, bottom, left, right)
model.patch("rect", 202, 10, 1, -y1, z1-cover, y1, z1, section=6)
model.patch("rect", 202, 10, 1, -y1, -z1, y1, cover-z1, section=6)
model.patch("rect", 202,  2, 1, -y1, cover-z1, cover-y1, z1-cover, section=6)
model.patch("rect", 202,  2, 1,  y1-cover, cover-z1, y1, z1-cover, section=6)
# Add the reinforcing fibers (left, middle, right, section=1)
model.layer("straight", 203, 3, As, y1-cover, z1-cover, y1-cover, cover-z1, section=6)
model.layer("straight", 203, 2, As,      0.0, z1-cover,      0.0, cover-z1, section=6)
model.layer("straight", 203, 3, As, cover-y1, z1-cover, cover-y1, cover-z1, section=6)



# elements
elem_type = "PrismFrame"
diag_elem_type = "forceBeamColumn"

model.beamIntegration("Lobatto", 101, 5, 15)  # for diagonal (section 5), 5 integration points
model.beamIntegration("Lobatto", 102, 6, 15)  # for side (section 6), 5 integration points


# bottom elements
for i in range(1,6):
    model.element(elem_type,i,(i,i+1),1,1)

# top elements
for i in range(6,12):
    model.element(elem_type,i,(i+1,i+2), 2,1)

# side elements
model.element(diag_elem_type, 12, (1, 7), section = 6, transform = 1)
model.element(diag_elem_type, 13, (6, 13), section = 6, transform = 1)

# diagonal elements
model.element(diag_elem_type, 14, (1, 8), section = 5,transform = 1) 
model.element(diag_elem_type, 15, (2, 8), section = 5,transform = 1) 
model.element(diag_elem_type, 16, (2, 9), section = 5,transform = 1) 
model.element(diag_elem_type, 17, (3, 9), section = 5,transform = 1) 
model.element(diag_elem_type, 18, (3, 10), section = 5,transform = 1) 
model.element(diag_elem_type, 19, (4, 10), section = 5,transform = 1) 
model.element(diag_elem_type, 20, (4, 11), section = 5,transform = 1) 
model.element(diag_elem_type, 21, (5, 11), section = 5,transform = 1) 
model.element(diag_elem_type, 22, (5, 12), section = 5,transform = 1) 
model.element(diag_elem_type, 23, (6, 12), section = 5,transform = 1) 




conc_weight = 0.15 #k/ft^
l_bridge = 175 #ft
total_weight = (bot_area + top_area) * l_bridge * conc_weight

# weights per bottom node using tributary areas
weight_1 = total_weight*(0.5*33.38/l_bridge)
weight_2 = total_weight*(0.5*(33.38+31.39)/l_bridge)
weight_3 = total_weight*(0.5*(31.39+34.713)/l_bridge)
weight_4 = total_weight*(0.5*(34.713+34.896)/l_bridge)
weight_5 = total_weight*(0.5*(34.896+40.5)/l_bridge)
weight_6 = total_weight*(0.5*40.5/l_bridge)

print(total_weight, weight_1 + weight_2 + weight_3 + weight_4 + weight_5 + weight_6)


loads = {
    1: [0, -weight_1, 0, 0, 0, 0],
    2: [0, -weight_2, 0, 0, 0, 0],
    3: [0, -weight_3, 0, 0, 0, 0],
    4: [0, -weight_4, 0, 0, 0, 0],
    5: [0, -weight_5, 0, 0, 0, 0],
    6: [0, -weight_6, 0, 0, 0, 0],

    #7: [0, -500, 0, 0, 0, 0], # place holders for if adding loads on top nodes
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

model.system("ProfileSPD")
model.constraints("Transformation")
model.numberer("RCM")
model.test("NormDispIncr", 1.0e-12, 10)
model.algorithm("Newton")

num_steps = 50
model.integrator("LoadControl", 1/num_steps)
model.analysis("Static")
model.analyze(num_steps)


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
artist.draw_outlines(state=model.nodeDisp, scale=50)
artist.draw_axes(extrude=True)
artist.draw_nodes()
artist
