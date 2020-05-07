import objects as obj
import model
import display_master as disp

"""
IDEE GENERALE :
la précédence fonctionne dans les deux sens. On peut definir pour chaque tache de chaque vol, un interval de t_i.
OK ça c'est bon
Ensuite, on va fonctionner en triant les types de taches dans l'ordre de la précédence.
Pour chaque liste de taches d'un certain type:
    si il existe un vehicule du bon type disponible:
        on va trifouiller dans son planning pour voir si il peut caser celle là en faisant parcourir tout l'interval pour t_i
        si ça merche, 
            on update les e_i des taches suivantes.
        si ça marche pas,
            on va voir si on peut trifouiller ses taches au vehicule sans toucher à la précédence des autres véhicules
    sinon,
        bah on crée un nouveau véhicule du bon type
"""


def make_ei(flight):
    """
    crée la date minimale de debut de chaque tache pour un vol
    :param flight: vol obj.Airplane()
    :return: rien, mais remplie les e_i de task_to_do
    """

    def sort_tasks(tasks_):
        format_ = ['In', 'Db', 'Ul', 'Lv', 'Ct', 'Cl', 'Fl', 'Bd', 'Ld', 'Pw', 'Pb', 'Ob']
        tasks_.sort(key=lambda t: format_.index(t.type.name))

    tasks = flight.task_to_do
    sort_tasks(tasks)
    init_time = flight.m_a
    for task_ in tasks:
        task_.e_i = max([t.e_i + t.d_i for t in task_.prev] + [init_time])
    flight.task_to_do = tasks


def make_li(flight):

    """
        crée la date maximale de debut de chaque tache pour un vol
        :param flight: vol obj.Airplane()
        :return: rien, mais remplie les l_i de task_to_do
        """

    def sort_tasks(tasks_):      #
        format_ = ['In', 'Db', 'Ul', 'Lv', 'Ct', 'Cl', 'Fl', 'Bd', 'Ld', 'Pw', 'Pb', 'Ob'][::-1]
        tasks_.sort(key=lambda t: format_.index(t.type.name))

    tasks = flight.task_to_do
    sort_tasks(tasks)
    for task_ in tasks[:-1]:
        temp = [t.type.name for t in task_.next]
        if len(temp) != 6:
            task_.l_i = flight.m_d - sum([t.d_i for t in tasks if t.type.name in temp]) - task_.d_i
        else:
            s_t_a = max([t.d_i for t in tasks if t.type.name in temp[:-3]])
            task_.l_i = flight.m_d - sum([t.d_i for t in tasks if t.type.name in temp[3:]]) - task_.d_i - s_t_a
    tasks[-1].l_i = flight.m_a
    flight.task_to_do = tasks[::-1]



def is_available_for_task(pb_, task_, vehicle):
    """
    :param pb_: problem instance
    :param task_: objet de la classe Task
    :param vehicle: objet de la classe Vehicule
    :return: True si le véhicule est du bon type et dispo à l'heure de la tâche
    """
    if task_.type.name in vehicle.type.can_do_names:
        last_task = vehicle.tasks[-1]
        time_to_move = pb_.parkings[last_task.airplane.parking - 1, task_.airplane.parking-1] / vehicle.type.speed
        time_to_start = vehicle.t_dispo + time_to_move
        if time_to_start <= task_.t_i:
            return True
    return False


def time_on_task(pb, task, vehicle):
        last_task = vehicle.tasks[-1]
        time_to_move = pb.parkings[last_task.airplane.parking - 1, task.airplane.parking-1] / vehicle.type.speed
        time_to_start = vehicle.t_dispo + time_to_move
        return time_to_start


def create_new_vehicle(task_):
    """
    :param task_: task that leads to creating the new vehicle
    :param vehicle_types: list of all vehicle types
    :return: a new vehicle that is already set to go to the task in argument
    """
    type_ = task_.type.can_be_done_by
    vehicle = obj.Vehicule(type_)
    vehicle.t_dispo = task_.t_i + task_.d_i
    vehicle.tasks.append(task_)
    return vehicle


def decaler_ti(task_name, flight, offset, pos=True):
    task = [task for task in flight.task_to_do if task_name == task.type.name][0]
    try:
        assert max([t.t_i + t.d_i for t in task.prev]) <= task.t_i + offset
        assert task.t_i + offset + task.d_i <= min([t.t_i for t in task.next])
        return True, 2
    except AssertionError:
        try:
            if pos:
                lasttask_fin = [t.t_i + t.d_i for t in flight.task_to_do if t.type.name == 'Ob']
                assert lasttask_fin + offset <= flight.m_d
            else:
                firsttask_deb = [t.t_i for t in flight.task_to_do if t.type.name == 'In']
                assert firsttask_deb + offset >= flight.m_a
            return True, 1
        except AssertionError:
            return False, 0


def heuristic_glouton(pb_):
    """
    :param pb_: problem completed with objects from obj
    :return: une flotte avec toutes les infos de planning
    """
    list_of_flights = pb_.flights
    all_tasks_to_do, fleet = list(), list()

    # step 1 - position e_i and l_i for all tasks and put them as to be treated
    actual_list_of_flights = sorted(list_of_flights, key=lambda fl_: fl_.m_d)
    for fli in actual_list_of_flights:
        make_ei(fli)
        make_li(fli)
        all_tasks_to_do += fli.task_to_do

    for task in all_tasks_to_do:
        task.t_i = task.e_i
    dict_of_tasks = dict()
    for v_type in pb_.vehicle_types:
        dict_of_tasks[v_type.name] = [task for task in all_tasks_to_do if v_type == task.type.can_be_done_by]

    fleet_dict = dict()
    for vehicle_type, associated_tasks in dict_of_tasks.items():
        while len(associated_tasks) > 0:
            print(associated_tasks)
            if vehicle_type not in fleet_dict.keys():
                fleet_dict[vehicle_type] = list()
            else:
                task = associated_tasks.pop()
                fleet_for_task = fleet_dict[vehicle_type]
                if len(fleet_for_task) == 0:
                    fleet_dict[vehicle_type].append(create_new_vehicle(task))
                else:
                    check = False
                    for vehicle in fleet_for_task:
                        if is_available_for_task(pb_, task, vehicle):
                            vehicle.tasks.append(task)
                            vehicle.t_dispo = task.t_i + task.d_i
                            check = True
                            break
                        else:
                            pass
                            # on fera notre tambouille ici

                    if check is False:
                        new_vehicle = create_new_vehicle(task)
                        fleet_dict[vehicle_type].append(new_vehicle)
    print(fleet_dict)
    fleet = list()
    for fleet_t in fleet_dict.values():
        fleet += fleet_t

    return fleet




'''
    # step 2 - if fleet is empty, let's create a first vehicle for a first task
    if len(fleet) == 0:
        task_considered = all_tasks_to_do.pop(0)
        new_vehicle = create_new_vehicle(task_considered)
        fleet.append(new_vehicle)


    # step 3 - for each task, if one of the vehicles is available, he will do it
    while len(all_tasks_to_do) > 0:
        task_considered = all_tasks_to_do.pop(0)
        check = False
        for vehicle in fleet:
            mav_task = time_on_task(pb_, task_considered, vehicle)

            if is_available_for_task(pb_, task_considered, vehicle):
                vehicle.tasks.append(task_considered)
                vehicle.t_dispo = task_considered.t_i + task_considered.d_i
                check = True
                break

    # step 5 - if no vehicle got it, let's create a new one
        if check is False:
            new_vehicle = create_new_vehicle(task_considered)
            fleet.append(new_vehicle)

    # step 5 bis (optional) calculate the time at which each vehicle of the fleet should leave and return its base

    # step 6 - all of our vehicles are given tasks and all tasks are given vehicles. Return the fleet.
    return fleet
'''

test = model.ProblemH('vols_2.txt')
test.vehicles = heuristic_glouton(test)
disp.display_planning_per_vehicle_heuristic(test)
