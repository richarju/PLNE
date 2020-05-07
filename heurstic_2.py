import objects as obj
import model

"""
IDEE GENERALE :
la précédence fonctionne dans les deux sens. On peut definir pour chaque tache de chaque vol, un interval de t_i.
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

    def sort_tasks(tasks_):
        format_ = ['In', 'Db', 'Ul', 'Lv', 'Ct', 'Cl', 'Fl', 'Bd', 'Ld', 'Pw', 'Pb', 'Ob'][::-1]
        tasks_.sort(key=lambda t: format_.index(t.type.name))

    tasks = flight.task_to_do
    sort_tasks(tasks)
    maxi_time = flight.m_d
    for task_ in [t for t in tasks if t.type.name in ['In', 'Ob', 'Pb']]:
        if task_.type.name == 'In':
            task_.l_i = flight.m_a
            task_.e_i = flight.m_a
        elif task_.type.name == 'Ob':
            task_.l_i = flight.m_d
            task_.e_i = flight.m_d
        else:
            task_.l_i = flight.m_d - task_.d_i
    for task_ in [t for t in tasks if t.type.name not in ['In', 'Ob', 'Pb']]:
        task_.l_i = min([t.l_i - t.d_i for t in task_.next] + [maxi_time])
    flight.task_to_do = tasks[::-1]
    print([(t.type.name, t.l_i) for t in flight.task_to_do])


test = model.ProblemH('vols_2.txt')
for fl in test.flights:
    make_ei(fl)
    make_li(fl)
    print('#########')
