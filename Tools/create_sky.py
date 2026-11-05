import bpy
import math
import os
import random

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
random.seed(8)
bpy.context.preferences.filepaths.save_version = 0
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 12
scene.render.resolution_x = 2048
scene.render.resolution_y = 1024
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'Standard'
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.12, .43, .78, 1)
scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = 1

cloud = bpy.data.materials.new('Cloud white')
cloud.diffuse_color = (.95, .97, 1, 1)
cloud.use_nodes = True
cloud.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.95, .97, 1, 1)
cloud.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 1
for i in range(12):
    a = i * math.tau / 12
    center = (100 * math.cos(a), 100 * math.sin(a), random.uniform(7, 22))
    for j in range(5):
        offset = (j - 2) * 4
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8,
            location=(center[0] - math.sin(a)*offset, center[1] + math.cos(a)*offset, center[2]+(3 if j==2 else 0)))
        ob = bpy.context.object
        ob.name = 'Cloud puff'
        ob.scale = (random.uniform(4, 6), random.uniform(4, 6), random.uniform(2.5, 4.5))
        ob.data.materials.append(cloud)
        bpy.ops.object.shade_smooth()

bpy.ops.object.light_add(type='SUN', location=(0, 0, 30))
bpy.context.object.rotation_euler = (.3, -.3, 0)
bpy.context.object.data.energy = 1.5
bpy.ops.object.camera_add(location=(0, 0, 0))
camera = bpy.context.object
camera.rotation_euler = (math.pi/2, 0, 0)
camera.data.type = 'PANO'
camera.data.panorama_type = 'EQUIRECTANGULAR'
scene.camera = camera
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = os.path.join(root, 'Art', 'sky.png')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(root, 'Art', 'Source', 'sky.blend'))
bpy.ops.render.render(write_still=True)
