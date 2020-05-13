class Airplane:
    """
    Object correspondant à un vol
    """
    def __init__(self, flight_nbr, m_a, m_d, park, list_of_tasks):
        self.fl_nbr = flight_nbr  # id du vol
        self.m_a = m_a  # EIBT
        self.m_d = m_d  # EOBT
        self.parking = park  # numéro de parkin /!\ retirer 1 pour utiliser dans la matrice
        self.task_to_do = list_of_tasks  # liste des instances de tâches qui devront être faites
        #  pour ce vol. Une seule tâche par type de tâche a priori. Ces tâches doivent êtr

    def __repr__(self):
        return "({} park:{} ibt:{} obt:{})\n".format(self.fl_nbr, self.parking, self.m_a, self.m_d)

    def format_list_of_tasks(self, task_types_list):

        """
        :param task_types_list: liste des tasks sans objet
        :return: permet de formater la liste des taches à faire avec un type et un format objet Task
        """
        returnable_data = list()
        names = [self.task_to_do[i] for i in range(0, len(self.task_to_do), 2)]
        durations = [int(self.task_to_do[i]) for i in range(1, len(self.task_to_do), 2)]
        for i, task_name in enumerate(names):
            type_ = [task_type for task_type in task_types_list if task_type.name == task_name][0]
            returnable_data.append(Task(type_, durations[i], self, [task for task in returnable_data if
                                                                    task.type.name in type_.previous_tasks_names]))

        next_dict = {'Ob': [],
                     'Pb': ['Ob'],
                     'Pw': ['Pb', 'Ob'],
                     'Ld': ['Pb', 'Ob'],
                     'Bd': ['Pb', 'Ob'],
                     'Fl': ['Bd', 'Pb', 'Ob'],
                     'Cl': ['Bd', 'Pb', 'Ob'],
                     'Ct': ['Bd', 'Pb', 'Ob'],
                     'Lv': ['Pw', 'Pb', 'Ob'],
                     'Ul': ['Ld', 'Pb', 'Ob'],

                     'Db': ['Fl', 'Ct', 'Cl', 'Bd', 'Pb', 'Ob'],
                     'In': ['Db', 'Ul', 'Lv', 'Ob'],
                     'TypeBegin': [],
                     'TypeEnfding': []}

        for task in returnable_data:
            next_names_list = next_dict[task.type.name]
            next_task = [task_ for task_ in returnable_data if task_.type.name in next_names_list]
            task.next = next_task
        self.task_to_do = returnable_data


class TaskType:
    """
    Object Activité qui va définir l'activité pour chaque type, son graphe de précédence obligatoire et le type de
    véhicule qu'on peut lui attribuer
    """

    def __init__(self, name, previous_task_names, indx):
        self.name = name  # nom de la task
        self.previous_tasks_names = previous_task_names  # graphe de precedence pour une activite (les noms sont ceux des types)
        self.can_be_done_by = None
        self.index = indx

    def __repr__(self):
        return "(--T_TYPE-- {})".format(self.name)

    def __eq__(self, other):
        return self.name == other.name


class Task:

    def __init__(self, type_, d_i, airplane, prev):
        self.type = type_  # expected TaskType object

        self.d_i = d_i  # duration
        self.airplane = airplane  # airplane associated
        self.e_i = self.airplane.m_a if airplane is not None else 0  # initialisation des e_i
        self.l_i = self.airplane.m_d if airplane is not None else 0  # initialisation des l_i
        self.vehicle = None  # instance de Vehicle qui sera concerne par cette tache
        self.t_i = self.e_i  # on place le début de la tâche à l'arrivée de l'avion avant de faire le planning
        self.previous = list()
        self.prev = prev
        self.next = list()

    def __repr__(self):
        return "--{} for {}-- di={}, ti={}\n".format(self.type.name, self.airplane.fl_nbr, self.d_i, self.t_i)

    def delta(self, vehicle):
        """
        :param vehicle:
        :return: vérifie si un véhicule peut bien effectuer cette tache en fonction de son type (cf modèle)
        """
        return 1 if self.type.name in vehicle.type.can_do_names else 0

    def delta2(self, vehicle_type):
        """returns 1 if a a vehicle of type vehicleType can perform such task"""
        return 1 if self.type.name in vehicle_type.can_do_names else 0

    '''def get_previous_tasks(self):
        returnable_data = list()
        prv_names = self.type.previous_tasks_names
        for task in self.airplane.task_to_do:
            # print('ACFT', task.airplane)
            # print('TASK', task)
            print(task)
            print('precedence ::::', prv_names)
            if task in prv_names:
                returnable_data.append(task)
        return returnable_data'''


class VehiculeType:
    """
    types de véhicules utilisés sur la plateforme
    """
    def __init__(self, name, speed, can_do_names, base):
        self.name = name
        self.speed = speed
        # liste des noms d'activités que le véhicule peut faire, il peut faire d'office les activités début et fin
        self.can_do_names = ["TypeBegin", "TypeEnding"] + can_do_names
        self.base = base

    def __repr__(self):
        return "(--V_Type-- {} SP{})".format(self.name, self.speed)

    def __eq__(self, other):
        return self.name == other.name



class Vehicule:
    """
    Objet qui va être instancié pour chaque véhicule de la flotte de l'aérodrome
    """
    def __init__(self, type_):
        self.type = type_  # vehicle type object expected
        self.tasks = []  # other tasks will be added through the process
        self.matrix_x = None  # to be used with plne afterward
        self.index_tasks = list()  # to be used with plne afterward
        self.t_dispo = 0

    def __repr__(self):
        return "--VEHICLE {}-- tasks: {}\n".format(self.type, self.tasks)

    def __eq__(self, other):
        return self.type.name == other.type.name and self.index_tasks == other.index_tasks
