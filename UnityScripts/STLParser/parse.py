import meshio
import numpy as np
import sys
import os
import re


def recenter_mesh(mesh):
    offset = -np.mean(mesh.points, axis=0)
    mesh.points = mesh.points + offset


def main(path, is_file: bool = True):
    if is_file:
        stl_to_obj(path)
    else:
        stl_to_obj_dir_base_function(path)


def stl_to_obj(path, output_path="E:\\ISEF\\VasculAR2\\VascuIAR\\UnityScripts\\STLParser\\output_file.obj"):
    print(path)
    mesh = meshio.read(path)
    newMesh = meshio.Mesh(mesh.points, mesh.cells)

    meshio.write(output_path, newMesh)


def stl_to_obj_with_recenter(path, output_path="E:\\ISEF\\VasculAR2\\VascuIAR\\UnityScripts\\STLParser\\output_file.obj"):
    print(path)
    mesh = meshio.read(path)
    newMesh = meshio.Mesh(mesh.points, mesh.cells)
    recenter_mesh(newMesh)

    meshio.write(output_path, newMesh)


def stl_to_obj_dir_with_recenter(processed_dir_path: list, processed_output_dir_path: list):
    print("called dir with recenter function")
    counter = 0
    vertices_list = []
    cell_list = []
    for file in processed_dir_path:
        mesh = meshio.read(file)
        vertices_list.append(mesh.points)
        cell_list.append(mesh.cells)

    all_vertices = np.concatenate(vertices_list, axis=0)
    centroid = -np.mean(all_vertices, axis=0)

    del all_vertices

    recentered_vertices_list = [vert + centroid for vert in vertices_list]
    for recentered_vertices, current_cell in zip(recentered_vertices_list, cell_list):
        newMesh = meshio.Mesh(recentered_vertices, current_cell)
        meshio.write(processed_output_dir_path[counter], newMesh)
        counter += 1

    del vertices_list
    del recentered_vertices_list
    del cell_list
    del newMesh


def stl_to_obj_dir_base_function(dir_path):
    def extract_numeric_part(file_name):
        matches = re.findall(r'\d+', file_name)
        return [int(match) for match in matches]

    print("called dir function")
    obj_folder_path = "E:\\ISEF\\VasculAR2\\VascuIAR\\UnityScripts\\STLParser\\obj_folder"
    obj_folder = os.listdir(obj_folder_path)
    obj_folder = sorted(obj_folder, key=lambda x: int(
        x.split('_')[1].split('.')[0]))

    for i in range(len(obj_folder)):
        obj_folder[i] = os.path.join(obj_folder_path, obj_folder[i])

    stl_path_list = []
    for file in os.listdir(dir_path):
        if get_file_extension(file):
            stl_path_list.append(os.path.join(dir_path, file))

    stl_path_list = sorted(
        stl_path_list, key=extract_numeric_part)

    stl_to_obj_dir_with_recenter(stl_path_list, obj_folder)


def get_file_extension(file_path):
    return file_path.split(".")[-1] == "stl"


if __name__ == "__main__":
    args = sys.argv
    if len(args) != 2:
        print(
            f"Error, program expects 1 command line argument of type str, but received {len(args) - 1} instead.")
        sys.exit()

    path = args[1]
    if os.path.isfile(path):
        main(path, True)
    elif os.path.isdir(path):
        main(path, False)


# ['E:\\ISEF\\VascuIAR\\UnityScripts\\STLParser\\parse.py',
# 'C:/Users/Acer/Downloads/ct_0096_label.nii/label_6_myocardium.stl']
