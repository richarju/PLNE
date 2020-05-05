import model as pbs
import pulp
import display_master as display
import objects


def solve_model_pulp(pb):
    # --------TOOLS----------ok
    m = 100
    # On definit le probleme a minimiser
    n_task = len(pb.all_tasks)
    n_vehicles = len(pb.vehicles)
    print(n_task-2)
    # print(pb.vehicles)
    print(pb.all_tasks[0], pb.all_tasks[n_task - 1])

    # --------PULP PROBLEM----------ok
    prob = pulp.LpProblem("Probleme_organisation_tournees", pulp.LpMinimize)

    # --------VARIABLE DECISIONS----------ok

    x = pulp.LpVariable.dicts("x", [(v, i, j) for i in range(n_task) for j in
                                    range(n_task) for v in range(n_vehicles)], cat="Binary")  # OK

    t = pulp.LpVariable.dicts("t", [(i) for i in range(n_task)], lowBound=0, cat="Integer")

    # --------OBJECTIVE----------ok
    prob += pulp.lpSum(x[k, 0, j] for k in range(n_vehicles) for j in range(1, n_task - 1))

    # --------CONTRAINTE FLOT----------ok
    for v in range(n_vehicles):
        for j in range(1, n_task - 1):  # Sur toutes les tâches qui ne sont ni début ni fin
            prob += pulp.lpSum(x[v, i, j] for i in range(n_task - 1)) == \
                    pulp.lpSum(
                        x[v, j, i] for i in range(1, n_task))  # , "Flot v={} typeVehicule={} tache {} typeTache {}".format(
               # v, pb.vehicles[v].type.name, j, pb.all_tasks[j].type.name)

            # prob += pulp.lpSum(x[v,0,j] for j in range(n_task-1)) == pulp.lpSum(x[v,j,n_task-1] for j in range(n_task-1) )
            # prob += pulp.lpSum(x[v,0,j] for j in range(n_task-1)) == 1
    for v in range(n_vehicles):
        for i in range(1, n_task - 1):
            prob += x[v, i, i] == 0  # , "NePasBouclerSurLaMemeTache v={} typeVehicule={} tache {} typeTache {}".format(v,
                                    #                                                                                pb.vehicles[
                                     #                                                                                   v].type.name,
                                      #                                                                              i,
                                       #                                                                             pb.all_tasks[
                                        #                                                                                i].type.name)


            # --------CONTRAINTE COHERENCE TEMPORELLE----------BUG
    tasks = pb.all_tasks
    for v in range(n_vehicles):
        # print(pb.vehicles[v].type.name,pb.vehicles[v].type.speed )
        for i in range(1, n_task - 1):
            for j in range(1, n_task - 1):
                p_i = pb.all_tasks[i].airplane.parking - 1
                p_j = pb.all_tasks[j].airplane.parking - 1

                prob += t[j] >= t[i] + pb.all_tasks[i].d_i + (
                pb.parkings[p_i][p_j] / float(pb.vehicles[v].type.speed)) - m * (1 - x[
                    v, i, j])  # , "TempBig_M v={} typeVehicule={} tache i={} typeTachei={} tache j={} typeTachej={}".format(
                    #  v, pb.vehicles[v].type.name, i, pb.all_tasks[i].type.name, j, pb.all_tasks[j].type.name)

        for j in range(1, n_task - 1):  # cas des débuts, a voir si c'est utile
            p_0 = pb.vehicles[v].type.base
            p_j = pb.all_tasks[j].airplane.parking - 1
            print(p_0, p_j)

            prob += t[j] >= t[0] + (pb.bases_vehicles[p_0][p_j] / pb.vehicles[v].type.speed) - m * (1 - x[
                v, 0, j])  # , "TempBig_M_Debut v={} typeVehicule={} tache i={} typeTachei={} tache j={} typeTachej={}".format(
                # v, pb.vehicles[v].type.name, 0, pb.all_tasks[0].type.name, j, pb.all_tasks[j].type.name)

    # ---------Contrainte de couverture-------------OK
    ## MAUVAIS
    # for vt in pb.vehicle_types:
    #    for j in range(1, n_task-1):
    #        prob += pulp.lpSum(x[v, i, j] for i in range(n_task-1) for v in
    #                           range(n_vehicles) == pb.all_tasks[j].delta2(vt)
    ##
    # BON
    for j in range(1, n_task - 1):
        prob += pulp.lpSum(x[v, i, j] for v in range(n_vehicles) for i in
                           range(n_task - 1)) == 1  # , "Couverture tache j={} typeTachej={}".format(j, pb.all_tasks[
          #  j].type.name)
        # Les tâches ne peuvent être effectuées que par les bons véhicules
        for v in range(n_vehicles):
            if pb.all_tasks[j].type.name not in pb.vehicles[v].type.can_do_names:
                prob += pulp.lpSum(x[v, i, j] for i in range(
                    n_task - 1)) == 0  # , "BonVehiculeArrive v={} typeVehicule={} tache j={} typeTachej={}".format(v,
                                       #                                                                         pb.vehicles[
                                       #                                                                             v].type.name,
                                       #                                                                         j,
                                       #                                                                         pb.all_tasks[
                                       #                                                                       j].type.name)
                prob += pulp.lpSum(x[v, j, i] for i in range(
                    n_task - 1)) == 0  # , "BonVehiculeRepart v={} typeVehicule={} tache j={} typeTachej={}".format(v,
                                       #                                                                         pb.vehicles[
                                       #                                                                             v].type.name,
                                       #                                                                         j,
                                       #                                                                         pb.all_tasks[
                                       #                                                                             j].type.name)

    # tous les véhicules effectuent la tâche début et la tâche fin : ça rend infaisable !
    for v in range(n_vehicles):
        # print(pb.all_tasks[n_task-1])
        prob += pulp.lpSum(
            x[v, 0, j] for j in range(1, n_task)) == 1  # , "Vehicule v={} typeVehicule={} fait tache debut".format(v,
                                                        #                                                         pb.vehicles[
                                                        #                                                            v].type.name)
        prob += pulp.lpSum(
            x[v, i, n_task - 1] for i in range(n_task - 1)) == 1  # , "Vehicule v={} typeVehicule={} fait tache fin".format(
            # v, pb.vehicles[v].type.name)

    # --------CONTRAINTE PRECEDENCE----------OK

    for aircraft in pb.flights:
        for task in aircraft.task_to_do:
            # print("Task current",task)
            # print("tâches précédentres",task.type.previous_tasks_names)
            for prevTask in task.type.previous_tasks_names:
                for t_todo in aircraft.task_to_do:
                    if prevTask == t_todo.type.name:
                        # print("Numéro tâche à faire : ",t_todo,pb.all_tasks.index(t_todo))
                        prob += t[pb.all_tasks.index(task)] >= t[pb.all_tasks.index(
                            t_todo)] + t_todo.d_i  # , "Precedence {} tache={} typeTache={} precede tache2={}typeTache={}".format(
                            # aircraft.fl_nbr, pb.all_tasks.index(t_todo), t_todo.type.name, pb.all_tasks.index(task),
                            # task.type.name)
        if task.type.name == "Ib":
            prob += t[pb.all_tasks.index(task)] >= aircraft.m_a  # , "InBlock apres arrivee mini {}".format(aircraft.fl_nbr)
        elif task.type.name == "Ob":
            prob += t[pb.all_tasks.index(task)] <= aircraft.m_d  # , "OffBlock avant deadline {}".format(aircraft.fl_nbr)

    # --------CONTRAINTE TEMPORELLE TACHE DEBUT----------
    prob += t[0] == 0  # , "TacheDebutCommenceDebut"

    # --------LES VEHICULES NE COMMENCENT PAS PAR UNE FIN ET NE FINISSENT PAS PAR LE DEBUT----------
    for i in range(n_task):
        for v in range(n_vehicles):
            prob += x[v, i, 0] == 0  # , "Vehicule v={} typeVehicule={} ne fait pas (tache{} {}, debut) ".format(v,
                                     #                                                                        pb.vehicles[
                                     #                                                                            v].type.name,
                                     #                                                                        i,
                                     #                                                                        pb.all_tasks[
                                     #                                                                            i].type.name)
            prob += x[v, n_task - 1, i] == 0  # , "Vehicule v={} typeVehicule={} ne fait pas (fin, tache{} {}) ".format(v,
                                              #                                                                      pb.vehicles[
                                              #                                                                          v].type.name,
                                              #                                                                      i,
                                              #                                                                     pb.all_tasks[
                                              #                                                                          i].type.name)

    # Les véhicules rentrent à la base après avoir tout terminé
    # première version ça bug
    '''
    for i, task_i in enumerate([pb.all_tasks[i] for i in range(1, n_task - 1)]):
        v_type = [v_t for v_t in pb.vehicle_types if task_i.type.can_be_done_by == v_t][0]
        prob += t[i] + (pb.bases_vehicles[v_type.base-1] / v_type.speed) + task_i.d_i <= t[n_task-2],
    '''
    # Autre version. Attention : Les distances base-parking sont stockées dans une matrice différente de celle des distance inter-parking !
    # print(pb.parkings)
    # print(pb.bases_vehicles)
    for i in range(1, n_task - 1):
        for vt in pb.vehicle_types:

            if pb.all_tasks[i].type.can_be_done_by == vt:
                pass  # prob += t[n_task-1] >= t[i] + pb.all_tasks[i].d_i + pb.bases_vehicles[pb.all_tasks[i].airplane.parking-1, vt.base] / vt.speed

    # L'activité i doit commencer entre sa date de début minimal et sa date de début maximale
    for i in range(1, len(pb.all_tasks) - 1):
        task_i = pb.all_tasks[i]
        prob += task_i.e_i <= t[i]  # , "Fenetre tache{} type {}apres {}".format(i, pb.all_tasks[i].type.name, task_i.e_i)
        prob += t[i] <= task_i.l_i  # , "Fenetre tache{} type {}avant {}".format(i, pb.all_tasks[i].type.name, task_i.l_i)

    """
    '''#Redondant et faux dans le modèle recopié (brunal you had one fking job)
    # On commence par le début et on termine par la fin
    for i in pb.all_tasks:
        for v in pb.vehicles:
            prob += x[v, i, pb.all_tasks[0]] == x[v, pb.all_tasks[len(pb.all_tasks)], i]
            prob += x[v, i, pb.all_tasks[0]] == 0
            '''
    """

    # pulp.LpSolverDefault.msg = 1 #pour le solveur de base ça affiche les infos
    # prob.writeLP('test.lp', mip=1)
    prob.solve(pulp.GLPK_CMD(msg=1, options=['--tmlim', '240']))
    print("Statut:", pulp.LpStatus[prob.status])

    for v in range(n_vehicles):
        # print(pb.vehicles[v].type.name,pb.vehicles[v].type.speed )
        for i in range(n_task - 1):
            for j in range(n_task - 1):
                # p_i = pb.all_tasks[i].airplane.parking-1
                # p_j = pb.all_tasks[j].airplane.parking-1
                print(v, i, j, pb.vehicles[v].type.name, pb.all_tasks[i].type.name,
                      pb.all_tasks[j].type.name) if 10 ** (-5) <= x[v, i, j].varValue <= 1 else '------'

                # if 10**(-5) <= x[v, i, j].varValue <= 1:
                #   print(x[v,i,j].varValue, pb.vehicles[v],t[j].varValue -( t[i].varValue + pb.all_tasks[i].d_i + (pb.parkings[p_i][p_j] / pb.vehicles[v].type.speed)))
    # print([t[i].varValue for i in range(n_task)])
    return x, t
    # print(x)
    # print(t)
    # print(x[0,0,0].varValue)
    # display.display_planning_per_vehicle(pb)

