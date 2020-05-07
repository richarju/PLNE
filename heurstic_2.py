import objects as obj
import model

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
    print([(t.type.name, t.e_i) for t in flight.task_to_do])


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


def time_on_task(pb, task,vehicle):
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

test = model.ProblemH('vols_2.txt')
for fl in test.flights:
    make_ei(fl)
    make_li(fl)

