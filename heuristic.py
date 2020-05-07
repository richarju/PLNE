import objects as obj


def make_time_for_task(flight):
    """
    fonction attribuant un t_i à chaque tache d'un vol en fonction de sa précédence
    :param flight: objet de la classe Airplane
    :return: le même vol avec les bons t_i pour chaque task

    """
    def sort_tasks(tasks_):
        format_ = ['In', 'Db', 'Ul', 'Lv', 'Ct', 'Cl', 'Fl', 'Bd', 'Ld', 'Pw', 'Pb', 'Ob']
        tasks_.sort(key=lambda t: format_.index(t.type.name))

    tasks = flight.task_to_do
    sort_tasks(tasks)
    init_time = flight.m_a
    for task_ in tasks:
        print(task_.prev)
        task_.t_i = max([t.t_i + t.d_i for t in task_.prev]+[init_time])
    flight.task_to_do = tasks


def move_the_task_will_not_change_the_planning_but_create_less_vehicle(task, m_a_v_task):
    """
    :param task: task considered
    :param m_a_v_task: date d'arrivée du vehicule considéré sur le parking de task
    :return: vérifie si en décalant le reste des tâches pour ce vol, dans la limite de
    m_d, le vehicule qui n'aurait pas pu faire la tache pourrait le faire
    """
    max_time_for_end_of_psh = task.airplane.m_d
    psh = [t for t in task.airplane.task_to_do if t.type.name == 'Pb'][0]
    delta_time = max_time_for_end_of_psh - psh.t_i - psh.d_i
    delta_eff = abs(task.t_i - m_a_v_task)
    if delta_eff < delta_time:
        task.t_i += int(delta_eff)
        tasks_to_move = [t for t in task.airplane.task_to_do if task.airplane.task_to_do.index(t) >
                         task.airplane.task_to_do.index(task)]
        for tsk in tasks_to_move:
            tsk.t_i += int(delta_eff)


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


def time_on_task(pb, task,vehicle):
        last_task = vehicle.tasks[-1]
        time_to_move = pb.parkings[last_task.airplane.parking - 1, task.airplane.parking-1] / vehicle.type.speed
        time_to_start = vehicle.t_dispo + time_to_move
        return time_to_start


def create_new_vehicle(task_, vehicle_types):
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


def heuristic_glouton(pb_):
    """
    :param pb_: problem completed with objects from obj
    :return: une flotte avec toutes les infos de planning
    """
    list_of_flights = pb_.flights
    vehicle_types = pb_.vehicle_types
    all_tasks_to_do, fleet = list(), list()

    # step 1 - position t_i for all tasks and put them as to be treated
    actual_list_of_flights = sorted([fl for fl in list_of_flights], key=lambda fl: fl.m_d)
    for fl in actual_list_of_flights:
        make_time_for_task(fl)
        all_tasks_to_do += fl.task_to_do

    # step 2 - if fleet is empty, let's create a first vehicle for a first task
    if len(fleet) == 0:
        task_considered = all_tasks_to_do.pop(0)
        new_vehicle = create_new_vehicle(task_considered, vehicle_types)
        fleet.append(new_vehicle)

    # step 3 - for each task, if one of the vehicles is available, he will do it
    while len(all_tasks_to_do) > 0:
        task_considered = all_tasks_to_do.pop(0)
        check = False
        for vehicle in fleet:
            mav_task = time_on_task(pb_, task_considered, vehicle)
            move_the_task_will_not_change_the_planning_but_create_less_vehicle(task_considered, mav_task)
            if is_available_for_task(pb_, task_considered, vehicle):
                vehicle.tasks.append(task_considered)
                vehicle.t_dispo = task_considered.t_i + task_considered.d_i
                check = True
                break

    # step 5 - if no vehicle got it, let's create a new one
        if check is False:
            new_vehicle = create_new_vehicle(task_considered, vehicle_types)
            fleet.append(new_vehicle)

    # step 5 bis (optional) calculate the time at which each vehicle of the fleet should leave and return its base

    # step 6 - all of our vehicles are given tasks and all tasks are given vehicles. Return the fleet.
    return fleet
