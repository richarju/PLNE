import model as pbs
import pulp


def solve_model_pulp(pb):

    # m = 10000
    # On definit le probleme a minimiser
    n_task = len(pb.all_tasks)

    prob = pulp.LpProblem("PAE", pulp.LpMinimize)  # OK

    # On definit une matrice binaire de decision x
    x = pulp.LpVariable.dicts("x", [(v, i, j) for i in range(n_task-1) for j in
                                    range(n_task-1) for v in range(len(pb.vehicles))], cat="Binary")  # OK

    # On definit une matrice binaire de decision y
    t = pulp.LpVariable.dicts("t", [(i) for i in range(n_task-1)], lowBound=0, cat="Integer")

    prob += pulp.lpSum(x[k, 0, j] for k in range(len(pb.vehicles))
                       for j in range(n_task-1)), "Objective : Number of vehicles"

    # Contrainte de flot

    for v in range(len(pb.vehicles)):
        for j in range(1, n_task-1):  # Sur toutes les tâches qui ne sont ni début ni fin
            prob += pulp.lpSum(x[v, i, j] for i in range(1, n_task-2)) == \
                    pulp.lpSum(x[v, j, i] for i in range(1, n_task-2))

        prob += pulp.lpSum(x[v, 0, j] for j in range(n_task)) == pulp.lpSum(x[v, j, n_task-1] for j in range(n_task))


    prob.solve(pulp.GLPK_CMD(msg=1))
    print("Statut:", pulp.LpStatus[prob.status])
"""
    # Cohérence temporelle
    for v in range(len(pb.vehicles)):
        for i in range(len(pb.all_tasks)):
            for j in range(1, len(pb.all_tasks)):
                prob += t[j] >= t[i]+pb.parkings[i, j]/pb.vehicles[v].type.speed - m*(1-x[v, i, j])

    # Contrainte de couverture
    # print(pb.vehicle_types)
    for vt in pb.vehicle_types:
        # print('vt=', vt)
        for j in range(len(pb.all_tasks)):
            # print('j=', j)
            print(pb.count_types_vehicle())
            prob += pulp.lpSum((x[v, i, j] for i in range(len(pb.all_tasks))) for v in
                               range(len(pb.count_types_vehicle()))) == pb.all_tasks[j].delta2(vt)




    # Précédence : toutes les tâches à effectuer pour un avion doivent s'effectuer après leurs tâches précédentes

    for aircraft in pb.flights:
        for task in aircraft.task_to_do:
            for prevTask in task.type.previous_task_names:
                for t_todo in aircraft.task_to_do:
                    if prevTask == t_todo.type:
                        prob += t[pb.all_tasks.index(task)] >= t[pb.all_tasks.index(t_todo)]+t_todo.d_i
        if task.type == "Ib":
            prob += t[pb.all_tasks.index(task)] >= aircraft.m_a
        elif task.type == "Ob":
            prob += t[pb.all_tasks.index(task)] <= aircraft.m_d

    # Début
    prob += t[0] == 0

    # Les véhicules rentrent à la base après avoir tout terminé
    for i in [pb.all_tasks[i] for i in range(len(pb.all_tasks) - 1)]:
        prob += t[i] + (pb.bases_vehicles[i] / i.type.can_be_done_by.speed) + i.d_i <= t[len(pb.all_tasks)],

    # Autre version
    '''for i in range(len(pb.all_tasks) - 1):
        for vt in pb.vehicle_types:
            prob += t[-1] >= t[i] + pb.parkings[i, -1] / vt.speed'''

    # L'activité i doit commencer entre sa date de début minimal et sa date de ébut macimale
    for i in pb.all_tasks:
        prob += i.e_i <= t[i],
        prob += t[i] <= i.l_i,

    # On commence par le début et on termine par la fin
    for i in pb.all_tasks:
        for v in pb.vehicles:
            prob += x[v, i, pb.all_tasks[0]] == x[v, pb.all_tasks[len(pb.all_tasks)], i]
            prob += x[v, i, pb.all_tasks[0]] == 0


    '''
    # Contraintes de couverture
    for i in range(pb.nb_vols):
        prob += pulp.lpSum([x[i, k] for k in range(pb.nb_flottes)]) == 1, "contrainte de couverture {}".format(i)

    # Contraintes de flot
    for k in range(pb.nb_flottes):
        for i, v in enumerate(pb.vertices):
            prob += pulp.lpSum([x[(j, k)] for j in v.arcs_vol_in]) \
                    + y[(v.arc_sol_in, k)] \
                    == pulp.lpSum([x[j, k] for j in v.arcs_vol_out]) \
                    + y[(v.arc_sol_out, k)], "contrainte de flot {} {}".format(k, i)

    # Contraintes de ressource
    for k in range(pb.nb_flottes):
        prob += pulp.lpSum([y[g, k] for g in pb.last_arcs_sol]) <= pb.nb_avions_flottes[
            k], "contrainte de ressource {}".format(k)
'''
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