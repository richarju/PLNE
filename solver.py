import model as pbs
import pulp


def solve_model_pulp(pb):

    # --------TOOLS----------ok
    m = 10000
    # On definit le probleme a minimiser
    n_task = len(pb.all_tasks)
    n_vehicles = len(pb.vehicles)
    # print(pb.vehicles)

    # --------PULP PROBLEM----------ok
    prob = pulp.LpProblem("PAE", pulp.LpMinimize)


    # --------VARIABLE DECISIONS----------ok

    x = pulp.LpVariable.dicts("x", [(v, i, j) for i in range(n_task) for j in
                                    range(n_task) for v in range(n_vehicles)], cat="Binary")  # OK

    t = pulp.LpVariable.dicts("t", [(i) for i in range(n_task)], lowBound=0, cat="Integer")

    # --------OBJECTIVE----------ok
    prob += pulp.lpSum(x[k, 0, j] for k in range(n_vehicles) for j in range(n_task))

    # --------CONTRAINTE FLOW----------ok
    for v in range(n_vehicles):
        for j in range(1, n_task-1):  # Sur toutes les tâches qui ne sont ni début ni fin
            prob += pulp.lpSum(x[v, i, j] for i in range(1, n_task-1)) == \
                    pulp.lpSum(x[v, j, i] for i in range(1, n_task-1))

        # prob += pulp.lpSum(x[v, 1, k] for k in range(n_task-1)) - pulp.lpSum(x[v, k, n_task-2] for k in range(n_task-1)) == 0

        # --------CONTRAINTE COHERENCE TEMPORELLE----------
    tasks = pb.all_tasks
    for v in range(n_vehicles):
        for i in range(1, n_task-2):
            for j in range(1, n_task-2):
                p_i = tasks[i].airplane.parking-1
                p_j = tasks[j].airplane.parking-1

                prob += t[j] >= t[i] + pb.parkings[p_i][p_j] / pb.vehicles[v].type.speed - m * (1 - x[v, i, j])

    #Contrainte de couverture
    ## MAUVAIS
    #for vt in pb.vehicle_types:
    #    for j in range(1, n_task-1):
    #        prob += pulp.lpSum(x[v, i, j] for i in range(n_task-1) for v in
    #                           range(n_vehicles) == pb.all_tasks[j].delta2(vt)
    ##
    #BON
    #Toutes les tâches sont effectuées une et une seule fois
    for j in range(1, n_task-1):
        prob += pulp.lpSum(x[v,i,j]for v in range(n_vehicles) for i in range(n_task-1)) == 1
        #Les tâches ne peuvent être effectuées que par les bons véhicules
        for v in range(n_vehicles):
            prob += pulp.lpSum(x[v,i,j]for i in range(n_task-1)) <= pb.all_tasks[j].delta(pb.vehicles[v])

    # --------CONTRAINTE PRECEDENCE----------
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

    # --------CONTRAINTE DE DEBUT----------
    prob += t[0] == 0

    # --------CONTRAINTE DE DEBUT ET FIN PAR VEHICULE----------
    for i in range(n_task):
        for v in range(n_vehicles):
            prob += x[v, i, 0] == x[v, n_task-1, i]
            prob += x[v, i, 0] == 0

    # Les véhicules rentrent à la base après avoir tout terminé
    #première version ça bug
    '''
    for i, task_i in enumerate([pb.all_tasks[i] for i in range(1, n_task - 1)]):
        v_type = [v_t for v_t in pb.vehicle_types if task_i.type.can_be_done_by == v_t][0]
        prob += t[i] + (pb.bases_vehicles[v_type.base-1] / v_type.speed) + task_i.d_i <= t[n_task-2],
    '''
    # Autre version. Attention : Les distances base-parking sont stockées dans une matrice différente de celle des distance inter-parking !
    #print(pb.parkings)
    #print(pb.bases_vehicles)
    for i in range(1,n_task - 1):
        for vt in pb.vehicle_types:

            if pb.all_tasks[i].type.can_be_done_by == vt : prob += t[n_task-1] >= t[i] + pb.bases_vehicles[pb.all_tasks[i].airplane.parking-1, vt.base] / vt.speed


    # L'activité i doit commencer entre sa date de début minimal et sa date de début maximale
    for i, task_i in enumerate(pb.all_tasks):
        prob += task_i.e_i <= t[i]
        prob += t[i] <= task_i.l_i

    '''#Redondant et faux dans le modèle recopié (brunal you had one fking job)
    # On commence par le début et on termine par la fin
    for i in pb.all_tasks:
        for v in pb.vehicles:
            prob += x[v, i, pb.all_tasks[0]] == x[v, pb.all_tasks[len(pb.all_tasks)], i]
            prob += x[v, i, pb.all_tasks[0]] == 0
            '''

    prob.solve(pulp.GLPK_CMD(msg=1))
    print("Statut:", pulp.LpStatus[prob.status])



    

    




    

    

    """

    #####
    # Resolution du modele par PLNE (appel au solveur GLPK)
    #####

    # Le probleme est resolu en utilisant un solver disponible avec PuLP
    # ici on utilise GLPK (on pourra faire appel a Gurobi et comparer l efficacite des solveurs)

    # avec/sans la sortie de GLPK si msg=1/0
    prob.solve(pulp.GLPK_CMD(msg=1))
    
    
    

    # il est possible d'ajouter des options de GLPK,
    # par exemple le time limit avec
    # prob.solve(pulp.GLPK_CMD(msg=1, options=["--tmlim", "10"])) #A PERSONNALISER ET DECOMMENTER au besoin

    #####
    # Recuperation de la solution du modele
    #####

    # Le statut de la solution est affichee : "Not Solved", "Infeasible", "Unbounded", "Undefined" ou "Optimal"
    print("Statut:", pulp.LpStatus[prob.status])

    # Les valeurs des variables d'affectation obtenues a l'issue de la resolution sont affichees
    sol = [None] * pb.nb_vols
    for v in prob.variables():
        if v.varValue == 1 and v.name[0] == 'x':
            vol = int(v.name.split(',_')[0].split('(')[1])
            fleet = int(v.name.split(',_')[1].split(')')[0])
            sol[vol] = fleet
    for k, f in pb.flights.items():
        print("{}({:02}) : {}".format(k, f.no, sol[f.no]))

    # La valeur de la fonction objectif a l'issue de la resolution est affichee
    print("Valeur de la fonction objectif = ", pulp.value(prob.objective))
"""
