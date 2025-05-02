import opensees.openseespy as ops
import veux


# QUESTIONS / TO DO
    # check fixing truss elements


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

model.fix(1, (1, 1, 1, 1, 1, 1)) # to make it simply supported
model.fix(6, (0, 1, 1, 1, 1, 1))

for node in range(2, 5): # to prevent out of plane translation
    model.fix(node, (0, 0, 1, 0, 0, 0))  
for node in range(7, 13):
    model.fix(node, (0, 0, 1, 0, 0, 0))  



# element constraints -- these would make it move as a rigid body 
'''
for i in range(1,12):
    model.equalDOF(i,i+1,(1,2,3))

for i in range(1,5):
    model.equalDOF(i,7+1,(1,2,3))
    model.equalDOF(7+i,i+1,(1,2,3))

model.equalDOF(1,7,(1,2,3))
model.equalDOF(6,13,(1,2,3))
'''


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
model.section("ElasticFrame", 1, E=E_conc, G=G_conc, A=bot_area, 
              Iy=(bot_b**3*bot_h)/12, Iz=(bot_b*bot_h**3)/12, J=(bot_b**3*bot_h)/12 + (bot_b*bot_h**3)/12)
model.section("ElasticFrame", 2, E=E_conc, G=G_conc, A=top_area, 
              Iy=(1*16**3)/12, Iz=(1**3*16)/12, J=(1*16**3)/12 + (1**3*16)/12)
model.section("ElasticFrame", 3, E=E_conc, G=G_conc, A=diag_area, 
              Iy=(diag_b**3*diag_h)/12, Iz=(diag_b*diag_h**3)/12, J=(diag_b**3*diag_h)/12 + (diag_b*diag_h**3)/12)
model.section("ElasticFrame", 4, E=E_conc, G=G_conc, A=side_area, 
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
    model.load(node, *load) 


# analysis

model.system("BandGeneral")
model.constraints("Plain")
model.numberer("RCM")
model.algorithm("Linear")
model.integrator("LoadControl", 1.0)
model.analysis("Static")
model.analyze(1)

print(model.nodeDisp(3))
print(model.nodeDisp(4))

print("analysis done")

'''
# Render the model
artist = veux.render(model, canvas="plotly")
artist.draw_outlines(model.nodeDisp, scale=10.0)
veux.serve(artist)
'''
