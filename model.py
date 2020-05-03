import import_data as data
import objects as obj
import numpy as np

class Problem:
    """
    instance totale du probleme reprenant l'ensemble des odonnées de import_data.py
    converties en objets de objects.py parfaitements instanciés pour une résolution algorithmique du problème
    """

    def __init__(self, flight_filename):

        # creation des distances entre parkings
        self.parkings = data.make_parking_matrix()
        # creations des distances des bases aux parkings
        self.bases_vehicles = data.make_base_matrix()

        # creation des types de tasks à faire
        self.task_types = data.make_task_types()
        # creation des types de vehicules disponibles sur la plateforme
        self.vehicle_types = data.make_vehicle_types()
        # Ajout de la passerelle (NO VEHICLE REQUIRED --> NVR) pour pouvoir attribuer chaque tache a un vehicule
        self.vehicle_types.append(obj.VehiculeType('NVR', 1000000, ['In', 'Ob', 'Bd', 'Db'], 1))
        # Attribution des types de véhicules aux types de taches
        self.set_up_what_vehicle_types_can_do_a_task_types()

        # creation du programme de vol
        self.flights = data.make_flight_list(flight_filename, self.task_types)
        # rassemblement de l'ensemble des tasks à faire
        self.nb_vols = len(self.flights)
        # print(self.flights)
        # print(self.flights[1].task_to_do)
        self.all_tasks = data.make_all_tasks(self.flights)

        # creation de la flotte de vehicules
        self.vehicles = self.generate_vehicles2()  # test: self.vehicles.append(obj.Vehicule(self.vehicle_types[0]))

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
            vehicle_type = [vt for vt in self.vehicle_types if t_type.name in vt.can_do_names][0]
            t_type.can_be_done_by = vehicle_type

    def generate_vehicles(self):
        returnable_date = list()
        for type_ in self.vehicle_types:
            for _ in range(self.parkings.shape[0]):
                returnable_date.append(obj.Vehicule(type_))
        return returnable_date

    def generate_vehicles2(self):
        returnable_date = list()

        for type_ in self.vehicle_types:
            for _ in range(self.nb_vols):
                returnable_date.append(obj.Vehicule(type_))
        return returnable_date

    def count_types_vehicle(self):
        ''' returns a list of the number of vehicles of each type, in the order of self.vehicle_type '''
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
            self.decision_t.append(int(t_pulp[i].varValue))

        for index_v, object_v in enumerate(self.vehicles):
            object_v.matrix_x = self.decision_x[index_v]

    def make_index_out_of_plne(self):
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
                tid_final = [task_index_done[0][0]]
            else:
                tid_final = [i[0] for i in task_index_done[:-1]] + [task_index_done[-1][1]]
            vehicule.index_tasks = tid_final

    def attribution_task_to_vehicle(self):
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
        self.make_array_after_plne(x, t)
        self.make_index_out_of_plne()
        self.attribution_task_to_vehicle()

    '''
        for index_v, vehicule in enumerate(self.vehicles):
            tid_final = first_step(index_v)
            print(tid_final)
            if len(tid_final) > 0:
                for ind, task in enumerate(self.all_tasks):
                    if ind in tid_final:
                        task.t_i = self.decision_t[ind]
                        vehicule.tasks.append(task)
        return self.vehicles
    
    def init_matrix_task_following(self):
        """
        :return: list of decision variables (matrix of x(i,j) for all vehicles in self.vehicles)
        """
        for i in range(len(self.vehicles)):
            temp_shape = len(self.all_tasks)
            self.decision_x.append(np.zeros((temp_shape, temp_shape)))  # initiated at 0

    def add_vehicle(self, task):
        """
        adding a vehicle to the fleet also requires to create a new x(i,j) matrix which
        will need tobe updated later
        :param task: the task the vehicle was created for
        :return: nothing
        """
        v_type = task.type.can_be_done_by
        self.vehicles.append(obj.Vehicule(v_type))
        temp_shape = len(self.all_tasks)
        self.decision_x.append(np.zeros((temp_shape, temp_shape)))'''





