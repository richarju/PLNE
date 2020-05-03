import numpy as np
import objects


def make_parking_matrix():
    apt_file = open("data/aeroport_1.txt")
    return np.array([[int(elt) for elt in line.split()[:10]] for line in apt_file.readlines()[:10]])


def make_base_matrix():
    base_file = open("data/aeroport_1.txt")
    return np.array([[int(elt) for elt in line.split()[1:]] for line in base_file.readlines()[11:]])


def make_vehicle_types():
    rule_file = open("data/activites_vehicules_1.txt")
    data = rule_file.readlines()
    returnable_data = list()
    for i, line in enumerate(data[14:]):
        s_line = line.split()
        returnable_data.append(objects.VehiculeType(s_line[0], int(s_line[1]), s_line[2:], i))
    return returnable_data


def make_task_types():
    rule_file = open("data/activites_vehicules_1.txt")
    data = rule_file.readlines()
    returnable_data = [objects.TaskType("TypeBegin", []), objects.TaskType("TypeEnding", ["In", "Db", "Ul", "Lv", "Ct", "Cl", "Fl", "Bd", "Ld", "Pw", "Pb", "Ob"])]
    for line in data[1:13]:
        s_line = line.split()
        returnable_data.append(objects.TaskType(s_line[0], s_line[1:]))
    return returnable_data


def make_flight_list(flight_file_name, task_types):
    flight_file = open("data/"+flight_file_name)
    data = flight_file.readlines()
    returnable_data = list()
    for line in data:
        s_line = line.split()
        affect = objects.Airplane(s_line[0], int(s_line[2]), int(s_line[3]), int(s_line[1]), s_line[5:])
        affect.format_list_of_tasks(task_types)
        returnable_data.append(affect)
    return returnable_data


def make_all_tasks(list_of_flights):
    returnable_data = list()
    returnable_data += [objects.Task(objects.TaskType("TypeBegin", []), 0, None)]
    for flight in list_of_flights:
        returnable_data += flight.task_to_do
    returnable_data += [objects.Task(objects.TaskType("TypeEnding", []), 0, None)]
    return returnable_data
