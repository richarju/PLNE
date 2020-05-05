import numpy as np
import objects


def make_parking_matrix():
    """
    crée la matrice de distance entre parkings à partir des données texte
    :return: np.array()
    """
    apt_file = open("data/aeroport_1.txt")
    return np.array([[int(elt) for elt in line.split()[:10]] for line in apt_file.readlines()[:10]])


def make_base_matrix():
    """
    crée la matrice de distance entre les bases des véhicules et les parkings
    :return: np.array()
    """
    base_file = open("data/aeroport_1.txt")
    return np.array([[int(elt) for elt in line.split()[1:]] for line in base_file.readlines()[11:]])


def make_vehicle_types():
    """
    crée des objets VehicleType à partir des données de types de véhicules
    :return: list() contains obj.VehicleTypes
    """
    rule_file = open("data/activites_vehicules_1.txt")
    data = rule_file.readlines()
    returnable_data = list()
    for i, line in enumerate(data[14:]):
        s_line = line.split()
        returnable_data.append(objects.VehiculeType(s_line[0], int(s_line[1]), s_line[2:], i))
    return returnable_data


def make_task_types():
    """
    crée des objets VehicleType à partir des données de types de véhicules
    :return: list() contains obj.TaskTypes
    """
    rule_file = open("data/activites_vehicules_1.txt")
    data = rule_file.readlines()
    returnable_data = [objects.TaskType("TypeBegin", []), objects.TaskType("TypeEnding", ["In", "Db", "Ul", "Lv",
                                                                                          "Ct", "Cl", "Fl", "Bd",
                                                                                          "Ld", "Pw", "Pb", "Ob"])]
    for line in data[1:13]:
        s_line = line.split()
        returnable_data.append(objects.TaskType(s_line[0], s_line[1:]))
    return returnable_data


def make_flight_list(flight_file_name, task_types):
    """
    crée la liste d'objets vols
    :param flight_file_name: fichier des vols en données
    :param task_types: types de tâches (au format list(obj.TaskType()...))
    :return: list() contains obj.Airplane()
    """
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
    """
    crée la liste des taches à effectuer sur la séquence. Inclut la création de TaskDébut et TaskFin
    :param list_of_flights: liste des vols avec chacun leurs tâches
    :return: list() contains obj.Task()
    """
    t_beg = objects.Task(objects.TaskType("TypeBegin", []), 0, None)
    t_end = objects.Task(objects.TaskType("TypeEnding", []), 0, None)
    returnable_data = list()
    returnable_data += [t_beg]
    for flight in list_of_flights:
        returnable_data += flight.task_to_do
    returnable_data += [t_end]
    return returnable_data
