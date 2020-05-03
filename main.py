import sys
import display_master as disp
import model
import solver



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Le programme prend un seul argument")
    else:
        print("----------CREATION DU PROBLEME----------")
        pb = model.Problem(sys.argv[1])
        print(pb, '\n')
        print("------EXECUTION PLNE VIA PULP.GLPK------")
        x, t = solver.solve_model_pulp(pb)
        print('\n')
        print("Valeur de la Fonction Objectif :", len([v for v in pb.vehicles if v.type.name != "NVR"]))
        print("Variables de décisions récupérables par \"pb.decision_x\" ou \"pb.decision_t\"")
        print('\n')
        print("--------TRAITEMENT DE LA FLOTTE---------")
        print("Variables de décisions récupérables par \"pb.decision_x\" ou \"pb.decision_t\"")
        print('\n')
        pb.fleet_from_plne(x, t)
        print("---------AFFICHAGE DU PLANNING----------")
        disp.display_planning_per_vehicle(pb)

