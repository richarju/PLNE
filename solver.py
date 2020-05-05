import pulp



def solve_model_pulp(pb):
    m = 1000
    n_task = len(pb.all_tasks)
    n_vehicles = len(pb.vehicles)

    # --------PULP PROBLEM----------
    prob = pulp.LpProblem("Probleme_Assistance_en_Escale", pulp.LpMinimize)

    # --------VARIABLE DECISIONS----------

    x = pulp.LpVariable.dicts("x", [(v, i, j) for i in range(n_task) for j in
                                    range(n_task) for v in range(n_vehicles)], cat="Binary")

    t = pulp.LpVariable.dicts("t", [(i) for i in range(n_task)], lowBound=0, cat="Integer")

    # --------OBJECTIVE----------
    prob += pulp.lpSum(x[k, 0, j] for k in range(n_vehicles) for j in range(1, n_task - 1))

    # --------CONTRAINTE FLOT----------
    for v in range(n_vehicles):
        for j in range(1, n_task - 1):  # Sur toutes les tâches qui ne sont ni début ni fin
            prob += pulp.lpSum(x[v, i, j] for i in range(n_task - 1)) == \
                    pulp.lpSum(
                        x[v, j, i] for i in range(1, n_task))

    for v in range(n_vehicles):
        for i in range(1, n_task - 1):
            prob += x[v, i, i] == 0

    # --------CONTRAINTE COHERENCE TEMPORELLE----------

    for v in range(n_vehicles):
        for i in range(1, n_task - 1):
            for j in range(1, n_task - 1):
                p_i = pb.all_tasks[i].airplane.parking - 1
                p_j = pb.all_tasks[j].airplane.parking - 1

                prob += t[j] >= t[i] + pb.all_tasks[i].d_i + (pb.parkings[p_i][p_j] /
                                                              float(pb.vehicles[v].type.speed)) - m * (1 - x[v, i, j])
        for j in range(1, n_task - 1):
            p_0 = pb.vehicles[v].type.base - 1
            p_j = pb.all_tasks[j].airplane.parking - 1
            prob += t[j] >= t[0] + (pb.bases_vehicles[p_0][p_j] / pb.vehicles[v].type.speed) - m * (1 - x[v, 0, j])

    # ---------CONTRAINTE COUVERTURE-------------
    for j in range(1, n_task - 1):
        prob += pulp.lpSum(x[v, i, j] for v in range(n_vehicles) for i in range(n_task - 1)) == 1

    #  --------CONTRAINTE AFFECTATION TYPE DE VEHICLE-------------
        for v in range(n_vehicles):
            if pb.all_tasks[j].type.name not in pb.vehicles[v].type.can_do_names:
                prob += pulp.lpSum(x[v, i, j] for i in range(n_task - 1)) == 0
                prob += pulp.lpSum(x[v, j, i] for i in range(n_task - 1)) == 0

    #  --------CONTRAINTE DE DEPART ET D'ARRIVEE POUR TOUS LES VEHICLES-------------
    for v in range(n_vehicles):
        prob += pulp.lpSum(x[v, 0, j] for j in range(1, n_task)) == 1
        prob += pulp.lpSum(x[v, i, n_task - 1] for i in range(n_task - 1)) == 1

    #  --------CONTRAINTE PRECEDENCE----------
    for aircraft in pb.flights:
        for task in aircraft.task_to_do:
            for prevTask in task.type.previous_tasks_names:
                for t_todo in aircraft.task_to_do:
                    if prevTask == t_todo.type.name:
                        prob += t[pb.all_tasks.index(task)] >= t[pb.all_tasks.index(t_todo)] + t_todo.d_i
        if task.type.name == "Ib":
            prob += t[pb.all_tasks.index(task)] >= aircraft.m_a
        elif task.type.name == "Ob":
            prob += t[pb.all_tasks.index(task)] <= aircraft.m_d

    # --------CONTRAINTE TEMPORELLE TACHE DEBUT----------
    prob += t[0] == 0

    # --------LES VEHICULES NE COMMENCENT PAS PAR UNE FIN ET NE FINISSENT PAS PAR LE DEBUT----------
    for i in range(n_task):
        for v in range(n_vehicles):
            prob += x[v, i, 0] == 0
            prob += x[v, n_task - 1, i] == 0

    # --------CONTRAINTE FENETRE D'EXECUTION DES TACHES----------
    for i in range(1, len(pb.all_tasks) - 1):
        task_i = pb.all_tasks[i]
        prob += task_i.e_i <= t[i]
        prob += t[i] <= task_i.l_i

    # --------EXECUTION DU MODELE PAR PULP---------
    # prob.writeLP('test.lp', mip=1)
    prob.solve(pulp.GLPK_CMD(msg=1, options=['--tmlim', '240']))
    print("Statut:", pulp.LpStatus[prob.status])

    return x, t
