import bpy
import math
import os
import random
import re
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS = os.path.join(ROOT, 'Art', 'Models')
SOURCE = os.path.join(ROOT, 'Art', 'Source')
os.makedirs(MODELS, exist_ok=True)
os.makedirs(SOURCE, exist_ok=True)
random.seed(17)
bpy.context.preferences.filepaths.save_version = 0

def clear():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

def material(name, color, roughness=0.8):
    color = tuple(c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4 for c in color)
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    shader = m.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Roughness'].default_value = roughness
    return m

gold = material('Marigold paint', (0.97, .48, .065), .38)
cream = material('Warm white', (.93, .91, .78))
dark = material('Deep navy', (.035, .075, .09))
rubber = material('Rubber', (.025, .032, .036))
metal = material('Alloy', (.48, .60, .62), .35)
teal = material('Petrol blue', (.025, .35, .39))
red = material('Vermilion', (.76, .16, .075))
grass = material('Meadow', (.28, .48, .29))
asphalt = material('Asphalt', (.15, .20, .22))
bark = material('Wood', (.30, .19, .105))
leaves = [material('Pine '+str(i), c) for i,c in enumerate([(.10,.28,.21),(.16,.36,.25),(.24,.41,.25)])]
hillmat = material('Distant sage', (.34,.49,.40))

def point(p):
    return (p[0], -p[2], p[1])

def cube(name, pos, size, mat, yaw=0, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=point(pos))
    ob = bpy.context.object
    ob.name = name
    ob.dimensions = (size[0], size[2], size[1])
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.rotation_euler.z = yaw
    ob.data.materials.append(mat)
    if bevel:
        mod = ob.modifiers.new('Small bevel', 'BEVEL')
        mod.width = bevel
        mod.segments = 1
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return ob

def cone(name,pos,r1,r2,height,mat,vertices=8):
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=r1, radius2=r2, depth=height, location=point(pos))
    ob=bpy.context.object
    ob.name=name
    ob.data.materials.append(mat)
    return ob

def text(name,body,pos,size,mat,yaw=0):
    curve=bpy.data.curves.new(name,'FONT')
    curve.body=body
    curve.align_x='CENTER'
    curve.align_y='CENTER'
    curve.size=size
    curve.extrude=.008
    ob=bpy.data.objects.new(name,curve)
    bpy.context.collection.objects.link(ob)
    ob.location=point(pos)
    ob.rotation_euler=(math.pi/2,0,yaw)
    ob.data.materials.append(mat)
    bpy.context.view_layer.objects.active=ob
    ob.select_set(True)
    bpy.ops.object.convert(target='MESH')
    ob.select_set(False)

def export(name):
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(SOURCE,name+'.blend'))
    if name == 'oval_course':
        bpy.ops.object.select_all(action='SELECT')
        bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]
        bpy.ops.object.join()
    bpy.ops.export_scene.gltf(filepath=os.path.join(MODELS,name+'.glb'), export_format='GLB', export_yup=True, export_materials='EXPORT')

clear()
cube('Chassis',(0,0,0),(1.48,.28,3.15),dark,bevel=.1)
cube('Body',(0,.22,.10),(1.5,.45,2.55),gold,bevel=.14)
cube('Nose',(0,.18,-1.15),(1.12,.30,.82),gold,bevel=.12)
cube('Nose stripe',(0,.342,-1.16),(.22,.018,.65),cream)
cube('Front wing',(0,-.06,-1.73),(2.05,.13,.30),teal,bevel=.045)
cube('Rear wing',(0,.74,1.52),(2.08,.14,.42),teal,bevel=.05)
for x in [-.64,.64]:
    cube('Wing mount',(x,.42,1.48),(.10,.65,.10),dark)
    cube('Side pod',(x*1.22,.15,.25),(.35,.38,1.45),gold,bevel=.08)
    cube('Headlamp',(x*.68,.22,-1.56),(.30,.10,.04),cream)
    cube('Rear lamp',(x,.25,1.37),(.18,.08,.035),red)
cube('Seat',(0,.5,.40),(.66,.65,.68),dark,bevel=.09)
cube('Cockpit',(0,.48,-.16),(.72,.20,.68),teal,bevel=.07)
cone('Driver suit',(0,.76,.30),.29,.24,.42,cream)
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.30,location=point((0,1.12,.26)))
bpy.context.object.name='Helmet'
bpy.context.object.data.materials.append(teal)
cube('Helmet visor',(0,1.14,.005),(.44,.14,.08),dark,bevel=.045)
for x in [-.3,.3]:
    cube('Arms',(x,.77,-.07),(.16,.16,.48),cream,bevel=.04)
cube('Steering wheel',(0,.79,-.35),(.52,.10,.12),dark,bevel=.03)
text('Race number','07',(0,.46,-.69),.35,cream)
bpy.data.objects['Race number'].rotation_euler = (0,0,0)
export('race_car')

clear()
wheel=cone('Tire',(0,0,0),.43,.43,.32,rubber,12)
wheel.rotation_euler.y=math.pi/2
for x in [-.17,.17]:
    hub=cone('Alloy rim',(x,0,0),.255,.255,.025,metal,10)
    hub.rotation_euler.y=math.pi/2
    cap=cone('Center cap',(x*1.12,0,0),.10,.10,.03,teal,8)
    cap.rotation_euler.y=math.pi/2
    for a in range(5):
        angle=a*math.tau/5
        spoke=cube('Spoke',(x*1.1,math.sin(angle)*.13,math.cos(angle)*.13),(.025,.07,.22),dark)
        spoke.rotation_euler.x=-angle
export('wheel')

clear()
cube('Ground',(0,-.25,0),(320,.5,340),grass)

def ring(name,offset1,offset2,mat,segments=128,start=0,end=math.tau,y=.025):
    verts=[]
    for i in range(segments+1):
        a=start+(end-start)*i/segments
        normal=Vector((math.cos(a)/32,math.sin(a)/52)).normalized()
        for off in [offset1,offset2]:
            verts.append(point((32*math.cos(a)+normal.x*off,y,52*math.sin(a)+normal.y*off)))
    faces=[(i*2,i*2+2,i*2+3,i*2+1) if offset2>offset1 else (i*2,i*2+1,i*2+3,i*2+2) for i in range(segments)]
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces)
    mesh.materials.append(mat)
    ob=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(ob)

ring('Track',-6.5,6.5,asphalt)
ring('Inside white line',-6.4,-6.23,cream,y=.035)
ring('Outside white line',6.23,6.4,cream,y=.035)
for i in range(128):
    a=i*math.tau/128
    b=(i+1)*math.tau/128
    for side in [-1,1]:
        ring('Kerb',side*6.5,side*7.35,cream if i%2 else red,1,a,b,.06)
for i in range(64):
    a=i*math.tau/64
    ring('Center dash',-.065,.065,cream,1,a,a+.028,.035)

for i in range(13):
    for row in range(3):
        cube('Finish checker',(26+i,.045,-.8+row*.55),(1,.025,.55),cream if (i+row)%2 else dark)
for z in [5,10,15]:
    for x in [29.4,34.6]:
        cube('Grid box',(x,.045,z),(2.2,.025,.12),cream)

for x in [23.5,40.5]:
    cube('Finish post',(x,3.1,0),(.42,6.2,.5),teal)
cube('Finish banner',(32,5.8,0),(17.4,1.4,.5),teal)
text('Finish title','Super Duper Racer',(32,5.82,.27),.85,cream)
text('Back of finish','Super Duper Racer',(32,5.82,-.27),.85,cream,math.pi)

def barrier_position(index,side):
    a=index*math.tau/100
    normal=Vector((math.cos(a)/32,math.sin(a)/52)).normalized()
    return Vector((32*math.cos(a),52*math.sin(a)))+normal*side*8.1

barrier_shapes=[]
minimum_gap=100
for side in [-1,1]:
    barriers=[]
    for i in range(100):
        a=i*math.tau/100
        center=barrier_position(i,side)
        previous=barrier_position(i-1,side)
        following=barrier_position(i+1,side)
        length=min((center-previous).length,(following-center).length)-.30
        tangent=Vector((-32*math.sin(a),52*math.cos(a))).normalized()
        x,z=center
        yaw=math.atan2(-tangent.x,-tangent.y)
        cube('Barrier',(x,.52,z),(.48,1.04,length),cream if i%4<2 else teal,yaw,bevel=.06)
        suffix='Inner' if side<0 else 'Outer'
        barrier_shapes.append(f'[sub_resource type="BoxShape3D" id="Wall{i}_{suffix}"]\nsize = Vector3(0.48, 1.04, {length})\n')
        barriers.append((center,tangent,length))
    for i,(center,tangent,length) in enumerate(barriers):
        other,other_tangent,other_length=barriers[(i+1)%100]
        direction=(other-center).normalized()
        extent=abs(tangent.dot(direction))*length/2+abs(Vector((-tangent.y,tangent.x)).dot(direction))*.24
        other_extent=abs(other_tangent.dot(direction))*other_length/2+abs(Vector((-other_tangent.y,other_tangent.x)).dot(direction))*.24
        gap=(other-center).length-extent-other_extent
        minimum_gap=min(minimum_gap,gap)
assert minimum_gap>.20, f'Barrier gap too small: {minimum_gap}'
print(f'All 200 adjacent barrier pairs separated; minimum gap {minimum_gap:.3f} metres.')

course_path=os.path.join(ROOT,'Scenes','Course.tscn')
if os.path.exists(course_path):
    with open(course_path,encoding='utf-8-sig') as f:
        course_scene=f.read()
    course_scene=re.sub(r'\[sub_resource type="BoxShape3D" id="Wall\d+(?:_Inner|_Outer)?"\]\nsize = Vector3\([^\n]+\)\n', '',course_scene)
    course_scene=course_scene.replace('[node name="Course"', '\n'.join(barrier_shapes)+'\n[node name="Course"',1)
    for i in range(100):
        for suffix in ['Inner','Outer']:
            course_scene=re.sub(r'(\[node name="Wall'+str(i)+'_'+suffix+r'"[^\]]+\][\s\S]*?shape = SubResource\(")Wall\d+(?:_Inner|_Outer)?("\))',r'\g<1>Wall'+str(i)+'_'+suffix+r'\2',course_scene)
    course_scene=re.sub(r'load_steps=\d+','load_steps=205',course_scene,count=1)
    with open(course_path,'w',encoding='utf-8') as f:
        f.write(re.sub(r'\n{3,}', '\n\n', course_scene))

def tree(x,z,s):
    cone('Trunk',(x,s*.75,z),.16*s,.12*s,s*1.5,bark,6)
    cone('Pine lower',(x,2.0*s,z),1.05*s,0,2.1*s,leaves[random.randrange(3)],7)
    cone('Pine crown',(x,2.8*s,z),.75*s,0,1.6*s,leaves[random.randrange(3)],7)

for i in range(62):
    a=random.random()*math.tau
    d=random.uniform(18,52)
    tree((32+d)*math.cos(a),(52+d)*math.sin(a),random.uniform(.9,2.1))
for x,z,s in [(-12,16,1.7),(7,24,1.5),(-9,-23,2.1),(12,-12,1.6),(0,5,1.8),(-13,4,1.1),(10,10,1.0)]:
    tree(x,z,s)
for i in range(14):
    a=i*math.tau/14
    cone('Low poly hills',(110*math.cos(a),5,125*math.sin(a)),random.uniform(20,40),0,random.uniform(18,40),hillmat,6)

for side in [-1,1]:
    x=side*49
    for step in range(4):
        cube('Grandstand',(x+side*step*.8,.4+step*.65,16),(1.6,.65,16),teal if step%2 else cream)
        for j in range(12):
            cube('Spectator',(x+side*step*.8,1+step*.65,9.5+j*1.1),(.36,.65,.4),[gold,red,teal,cream][(j+step)%4],bevel=.06)
    cube('Stand roof',(x+side*1.2,4.6,16),(5.2,.18,18),teal)
    for z in [8,24]:
        cube('Roof pillar',(x+side*2.5,2.3,z),(.15,4.6,.15),dark)

export('oval_course')
print('Created three editable Blender files and three GLB models.')
