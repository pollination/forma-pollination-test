import json

from ladybug_geometry.geometry3d import Point3D, Face3D
from ladybug_geometry.bounding import bounding_box

from dragonfly.room2d import Room2D
from dragonfly.story import Story
from dragonfly.building import Building
from dragonfly.model import Model
from dragonfly.context import ContextShade

from dragonfly.windowparameter import RepeatingWindowWidthHeight

from honeybee.model import Model as HBModel

from ladybug_geometry.geometry3d.plane import Plane
from ladybug_geometry.geometry3d.face import Face3D
from ladybug_geometry.geometry3d.mesh import Mesh3D
from honeybee.room import Room
from honeybee.facetype import Floor, Wall
from honeybee.typing import clean_rad_string
from honeybee_radiance.sensorgrid import SensorGrid


def split_list_to_equal_3_items(list1):
  """Splits a list to equal 3 items without using the itertools module.

  Args:
    list1: A list.

  Returns:
    A list of lists, each containing 3 items.
  """

  split_list = []
  chunk_size = 3

  # Iterate over the list in chunks of size 3.
  for i in range(0, len(list1), chunk_size):
    # Create a new list for each chunk.
    new_list = []

    # Add the elements from the current chunk to the new list.
    for j in range(i, i + chunk_size):
      if j < len(list1):
        new_list.append(list1[j])

    # Add the new list to the split list.
    split_list.append(new_list)

  return split_list


def create_context_shade(vertices, center, dist):
    points = [Point3D(*p) for p in split_list_to_equal_3_items(vertices)]
    faces = [Face3D(f) for f in split_list_to_equal_3_items(points)]
    faces = [f for f in faces if f.center.distance_to_point(center) < dist]
    return ContextShade('context-shade', faces)


def build_dragonfly_model(org_data):
    """Build a Dragonfly Model from Forma's strange JSON.
    
    Args:
        json_file_path: Path to Forma's JSON.
    """
    # load the JSON file
    context = None
    data = None
    if 'volumes' in org_data:
        data = org_data['volumes']

    # loop through the features and create Room2Ds
    room_2ds, room_count = [], 1
    for feature in data['features']:
        if feature['geometry']['type'] == 'Polygon':
            flr_hgt = feature['properties']['elevation']
            flr_to_ceil = feature['properties']['height']
            loops = []
            for loop in feature['geometry']['coordinates']:
                loops.append([Point3D(pt[0], pt[1], flr_hgt) for pt in loop])
            room_geo = Face3D(loops[0], holes=loops[1:])
            room_geo = room_geo.remove_colinear_vertices(0.01)
            room = Room2D('Room_{}'.format(room_count), room_geo, flr_to_ceil)
            room_2ds.append(room)
            room_count += 1

    # group the rooms by floor elevation
    min_difference = 2  # minimum difference in floor heights that makes a new story
    # loop through each of the rooms and get the floor height
    flrhgt_dict = {}
    for room in room_2ds:
        flrhgt = room.floor_height
        try:  # assume there is already a story with the room's floor height
            flrhgt_dict[flrhgt].append(room)
        except KeyError:  # this is the first room with this floor height
            flrhgt_dict[flrhgt] = []
            flrhgt_dict[flrhgt].append(room)

    # sort the rooms by floor heights
    room_mtx = sorted(flrhgt_dict.items(), key=lambda d: float(d[0]))
    flr_hgts = [r_tup[0] for r_tup in room_mtx]
    room_2ds = [r_tup[1] for r_tup in room_mtx]

    # group floor heights if they differ by less than the min_difference
    floor_heights = [flr_hgts[0]]
    grouped_rooms = [room_2ds[0]]
    for flrh, rm in zip(flr_hgts[1:], room_2ds[1:]):
        if flrh - floor_heights[-1] < min_difference:
            grouped_rooms[-1].extend(rm)
        else:
            grouped_rooms.append(rm)
            floor_heights.append(flrh)

    # create the stories from room groups and make the Building
    stories = []
    for i, room_group in enumerate(grouped_rooms):
        story = Story('Floor_{}'.format(i), room_group)
        stories.append(story)
    building = Building('Building_From_FORMA', stories)
    building.separate_top_bottom_floors()
    for story in building.unique_stories:
        story.solve_room_2d_adjacency()

    floors = [room.floor_geometry for room in building.all_room_2ds()]
    pt1, pt2 = bounding_box(floors)
    center = (pt1 + pt2) / 2

    if 'triangles' in org_data:
       context = create_context_shade(org_data['triangles'], center, 250)
       return Model('Forma_Model', [building], [context])

    return Model('Forma_Model', [building])


def add_apertures(model: Model, win_height: float, win_width: float):
    win_par = RepeatingWindowWidthHeight(win_height, win_width, 0.8, 3)
    model.set_outdoor_window_parameters(win_par)
    return model


def df_to_hb(model: Model):
    return model.to_honeybee('District')[0]


def add_sensor_grids(model: HBModel, grid_size=0.5, dist=0.8):
    grids = []
    for room in model.rooms:
        grid = room.properties.radiance.generate_sensor_grid(
            x_dim=grid_size, y_dim=None, offset=dist, remove_out=True, wall_offset=0
        )
        grids.append(grid)
    
    model.properties.radiance.add_sensor_grids(grids)
    return model