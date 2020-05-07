import import_data as data
import objects as obj
import numpy as np


class Problem:
    """
    crée une istance du problème avec les bons objets
    """

    def __init__(self, flight_filename, include_beg_end=True):
        """
        :param flight_filename: chaque instance dépend du programme de vol à traiter
        """
        # creation des distances entre parkings
        self.parkings = data.make_parking_matrix()

        # creations des distances des bases aux parkings
        self.bases_vehicles = data.make_base_matrix()

        # creation des types de tasks à faire
        if include_beg_end:
            self.task_types = data.make_task_types()
        else:
            self.task_types = data.make_task_types()[2:]
        # creation des types de vehicules disponibles sur la plateforme
        self.vehicle_types = data.make_vehicle_types()

        # Ajout de la passerelle (NO VEHICLE REQUIRED --> NVR) pour pouvoir attribuer chaque tache a un vehicule
        self.vehicle_types.append(obj.VehiculeType('NVR', 100000000000, ['In', 'Ob', 'Bd', 'Db'], 1))

        # Attribution des types de véhicules aux types de taches
        self.set_up_what_vehicle_types_can_do_a_task_types()

        # creation du programme de vol
        self.flights = data.make_flight_list(flight_filename, self.task_types)

        # rassemblement de l'ensemble des tasks à faire
        self.nb_vols = len(self.flights)

        # creation de la liste de taches à traiter
        self.all_tasks = data.make_all_tasks(self.flights)

        # creation de la flotte de vehicules
        self.vehicles = list()  # test: self.vehicles.append(obj.Vehicule(self.vehicle_types[0]))

        # recuperation des variables de decision en PLNE
        self.decision_x = None
        self.decision_t = list()

    def __repr__(self):
        return "---Problem Object--- \nnbr of flights: {}  \nnbr of tasks: {}  " \
               "\nvehicles used: {}".format(len(self.flights), len(self.all_tasks), len(self.vehicles))

    def set_up_what_vehicle_types_can_do_a_task_types(self):
        """
        is meant to update self.task_types[i].can_be_done_by, for i in range(len(self.task_types)
        --> after that, each type of task knows which type of vehicle can make it.
        The opposite is already true
        """
        for t_type in self.task_types:
            vehicle_type = [vt for vt in self.vehicle_types if t_type.name in vt.can_do_names]
            t_type.can_be_done_by = vehicle_type[0]

    def generate_vehicles(self):
        """
        first attempt to create a fleet before solving with PLNE. not optimized
        :return: list() contains Vehicles
        """
        returnable_date = list()
        for type_ in self.vehicle_types:
            for _ in range(self.parkings.shape[0]):
                returnable_date.append(obj.Vehicule(type_))
        return returnable_date

    def generate_vehicles2(self):
        """
        second attempt to create a fleet before solving with PLNE. more optimized than version 1
        :return:  list() contains Vehicles
        """
        returnable_date = list()
        for type_ in self.vehicle_types:
            for _ in range(self.nb_vols):
                returnable_date.append(obj.Vehicule(type_))
        return returnable_date

    def count_types_vehicle(self):
        """
        returns a list of the number of vehicles of each type, in the order of self.vehicle_type
        :return: list
        """
        return_list = []
        for t in self.vehicle_types:
            c = 0
            for v in self.vehicles:
                if v.type == t:
                    c += 1
            return_list.append(c)
        return return_list

    def make_array_after_plne(self, x_pulp, t_pulp):
        """
        :param x_pulp: result of PLNE execution via pulp GLPK (decision variable X)
        :param t_pulp: result of PLNE execution via pulp GLPK (decision variable T)
        :return: nothing, but gives simple to use types to those variables in pb.
        """
        n_task = len(self.all_tasks)
        n_vehicles = len(self.vehicles)

        result_x = np.zeros((n_vehicles, n_task, n_task))
        for v in range(n_vehicles):
            for i in range(n_task):
                for j in range(n_task):
                    xvij = x_pulp[v, i, j].varValue
                    if xvij is not None:
                        result_x[v, i, j] = int(xvij)
                    else:
                        result_x[v, i, j] = 0
        self.decision_x = result_x
        for i in range(n_task):
            self.decision_t.append(t_pulp[i].varValue)

        for index_v, object_v in enumerate(self.vehicles):
            object_v.matrix_x = self.decision_x[index_v]

    def make_index_out_of_plne(self):
        """
        pour chaque vehicle, cette fonction récupère les indices des taches qu'il effectue
        :return: nothing. donne à chaque véhicle les indices de ses taches
        """
        n_task = len(self.all_tasks)

        for index_v, vehicule in enumerate(self.vehicles):
            task_index_done = list()
            for i in range(n_task):
                for j in range(n_task):
                    if int(vehicule.matrix_x[i][j]) == 1:
                        task_index_done.append((i, j))
            if len(task_index_done) == 0:
                tid_final = list()
            elif len(task_index_done) == 1:
                tid_final = [task_index_done[0][1]]
            else:
                tid_final = [i[1] for i in task_index_done[:-1]] + [task_index_done[-1][1]]
            vehicule.index_tasks = tid_final

    def attribution_task_to_vehicle(self):
        """
        récupère les objets taches à partir des indices récupérés dans la fonction précédente
        :return: nothing. attribue à chaque vehicle ses objects taches
        """
        returnable_data = list()
        for index_v, vehicle in enumerate(self.vehicles):
            vehicle.tasks = list()
            if len(vehicle.index_tasks) != 0:
                for index_of_task in vehicle.index_tasks:
                    self.all_tasks[index_of_task].t_i = self.decision_t[index_of_task]
                    vehicle.tasks.append(self.all_tasks[index_of_task])

                returnable_data.append(vehicle)

        self.vehicles = returnable_data

    def fleet_from_plne(self, x, t):
        """
        fonction de traitement du résultat du plne
        :param x: x from pulp
        :param t: t from pulp
        :return: l'ensemble des trois fonctions précédents
        """
        self.make_array_after_plne(x, t)
        self.make_index_out_of_plne()
        self.attribution_task_to_vehicle()


class ProblemH:
    """
    instance totale du probleme reprenant l'ensemble des odonnées de import_data.py
    converties en objets de objects.py parfaitements instanciés pour une résolution algorithmique du problème
    """

    def __init__(self, flight_filename):

        # creation des distances entre parkings
        self.parkings = data.make_parking_matrix_h()
        # creations des distances des bases aux parkings
        self.bases_vehicles = data.make_base_matrix_h()

        # creation des types de tasks à faire
        self.task_types = data.make_task_types_h()
        # creation des types de vehicules disponibles sur la plateforme
        self.vehicle_types = data.make_vehicle_types_h()
        # Ajout de la passerelle (NO VEHICLE REQUIRED --> NVR) pour pouvoir attribuer chaque tache a un vehicule
        self.vehicle_types.append(obj.VehiculeType('NVR', 1000000000, ['In', 'Ob', 'Bd', 'Db'], 1))
        # Attribution des types de véhicules aux types de taches
        self.set_up_what_vehicle_types_can_do_a_task_types()

        # creation du programme de vol
        self.flights = data.make_flight_list_h(flight_filename, self.task_types)
        # rassemblement de l'ensemble des tasks à faire
        self.all_tasks = data.make_all_tasks_h(self.flights)

        # creation de la flotte de vehicules
        self.vehicles = list()  # test: self.vehicles.append(obj.Vehicule(self.vehicle_types[0]))

        self.decision_x = list()

    def __repr__(self):
        return "---Problem Object--- \nnbr of flights: {}  \nnbr of tasks: {}  " \
               "\nvehicles used: {}".format(len(self.flights), len(self.all_tasks), len(self.vehicles))

    def set_up_what_vehicle_types_can_do_a_task_types(self):
        """
        is meant to update self.task_types[i].can_be_done_by, for i in range(len(self.task_types)
        --> after that, each type of task knows which type of vehicle can make it.
        The opposite is already true
        """
        for t_type in self.task_types:
            vehicle_type = [vt for vt in self.vehicle_types if t_type.name in vt.can_do_names][0]
            t_type.can_be_done_by = vehicle_type
