import bpy

# Clear existing scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# Define dimensions (meters)
wall_height = 2.5
wall_thickness = 0.15

# Define room dimensions based on blueprint (approximate) - Adjust these values as needed to match your blueprint accurately.
#  These values are estimations based on the provided blueprint.  Precise measurements from the blueprint are needed for accurate modeling.
terrace_x = 4
terrace_y = 3
kitchen_x = 4
kitchen_y = 4
livingroom_x = 6
livingroom_y = 4
bathroom_x = 2.5
bathroom_y = 2.5
boiler_x = 2
boiler_y = 2
cabinet_x = 3
cabinet_y = 3
bedroom_x = 4
bedroom_y = 4
children_x = 2.5
children_y = 2.5


# Helper function to create a wall
def create_wall(x, y, z, width, length, height, material):
    bpy.ops.mesh.primitive_cube_add(size=1, enter_editmode=False, align='WORLD', location=(x, y, z), scale=(width, length, height))
    wall = bpy.context.object
    wall.name = f"Wall_{x}_{y}"
    mat = bpy.data.materials.new(name="WallMaterial")
    mat.diffuse_color = material
    wall.data.materials.append(mat)


# Create walls (example - adjust coordinates and dimensions to match your blueprint)
create_wall(0, 0, 0, wall_thickness, terrace_y + kitchen_y + livingroom_y + bedroom_y, wall_height, (0.8, 0.8, 0.8)) # Outer wall
create_wall(terrace_x + kitchen_x + livingroom_x + bedroom_x, 0, 0, wall_thickness, terrace_y + kitchen_y + livingroom_y + bedroom_y, wall_height, (0.8, 0.8, 0.8)) # Outer wall
create_wall(0, 0, 0, terrace_x + kitchen_x + livingroom_x + bedroom_x, wall_thickness, wall_height, (0.8, 0.8, 0.8)) # Outer wall
create_wall(0, terrace_y + kitchen_y + livingroom_y + bedroom_y, 0, terrace_x + kitchen_x + livingroom_x + bedroom_x, wall_thickness, wall_height, (0.8, 0.8, 0.8)) # Outer wall

# Add more walls as needed based on your blueprint


# Add simple lighting
bpy.ops.object.light_add(type='SUN', radius=1, location=(5, 5, 10))


# Set camera position
bpy.data.objects['Camera'].location = (10, 10, 10)
bpy.data.objects['Camera'].rotation_euler = (1.047, 0, 0)


# Export to GLB
bpy.ops.export_scene.gltf(filepath="house.glb", export_format='GLB')