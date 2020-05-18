import sys
import model
import solver
import heuristic
import display_master as disp
import verification as vnv
import matplotlib.pyplot as plt


if __name__ == "__main__":
    if sys.argv[2] == '-heuritest':
        if len(sys.argv) == 3:
            try:
                pb = model.ProblemH(sys.argv[1])
                pb.vehicles, historic_fleet = heuristic.heuristic_glouton(pb)
                pb_init = model.ProblemH(sys.argv[1])
                test = vnv.Verification(pb_init, pb)
                test.execute()
                for flt in historic_fleet:
                    fig, ax = plt.subplots()
                    pb.vehicles = flt
                    disp.display_planning_per_vehicle_heuristic(pb, fig, ax)
                    plt.show(block=False)
                    plt.pause(0.03)
                    plt.close(fig)
                # print(pb)
                fig, ax = plt.subplots()
                disp.display_planning_per_vehicle_heuristic(pb, fig, ax)
                plt.show(block=True)

            except FileNotFoundError:
                print('--Le fichier de vol mentionné n\'est pas répertorié--')
        else:
            print('--L\'exécution du test d\'heuristique ne prend pas d\'autres arguments--')

    elif sys.argv[2] == '-heuristic':
        if len(sys.argv) == 3:
            try:
                pb = model.ProblemH(sys.argv[1])
                print('-------HEURISTIC SOLVER------')
                pb.vehicles, historic_of_fleet = heuristic.heuristic_glouton(pb)
                print(pb)
                fig, ax = plt.subplots()
                disp.display_planning_per_vehicle_heuristic(pb, fig, ax)
                plt.show(block=True)
            except FileNotFoundError:
                print('--Le fichier de vol mentionné n\'est pas répertorié--')
        elif len(sys.argv) == 4:
            if sys.argv[3] == '-nodisp':
                try:
                    pb = model.ProblemH(sys.argv[1])
                    print('-------HEURISTIC SOLVER------')
                    pb.vehicles = heuristic.heuristic_glouton(pb)
                    print(pb)
                    print(pb.vehicles)
                except FileNotFoundError:
                    print('--Le fichier de vol mentionné n\'est pas répertorié--')

    elif sys.argv[2] == '-plne':
        if len(sys.argv) == 3:
            try:
                pb = model.Problem(sys.argv[1])
                print(pb)
                print('-------PLNE SOLVER------')
                pb.vehicles = pb.generate_vehicles2()
                x, t = solver.solve_model_pulp(pb)
                pb.make_array_after_plne(x, t)
                pb.fleet_from_plne(x, t)
                disp.display_planning_per_vehicle(pb)
            except FileNotFoundError:
                print('--Le fichier de vol mentionné n\'est pas répertorié--')


        elif len(sys.argv) == 4:
            if sys.argv[3] == '-nodisp':
                try:
                    pb = model.Problem(sys.argv[1])
                    print(pb)
                    print('-------PLNE SOLVER------')
                    pb.vehicles = pb.generate_vehicles2()
                    x, t = solver.solve_model_pulp(pb)
                    pb.make_array_after_plne(x, t)
                    pb.fleet_from_plne(x, t)
                except FileNotFoundError:
                    print('--Le fichier de vol mentionné n\'est pas répertorié--')

            elif int(sys.argv[3][2:]):
                try:
                    try:
                        time_n = int(sys.argv[3][1:])
                        pb = model.Problem(sys.argv[1])
                        print(pb)
                        print('-------PLNE SOLVER------')
                        pb.vehicles = pb.generate_vehicles2()
                        x, t = solver.solve_model_pulp(pb, time_n)
                        pb.make_array_after_plne(x, t)
                        pb.fleet_from_plne(x, t)
                        disp.display_planning_per_vehicle(pb)
                    except FileNotFoundError:
                        print('--Le fichier de vol mentionné n\'est pas répertorié--')
                except ValueError:
                    print('--Le temps d\'execution mentionné n\'est pas correct--')

            else:
                print('--L\'un des trois arguments n\'est pas bon : merci de préciser -nodisp si '
                      'vous ne voulez pas d\'affichage, \nou -nnn si vous voulez limiter le temps de calcul à nnn--')

        elif len(sys.argv) == 5:
            if sys.argv[3] == '-nodisp' and int(sys.argv[4][1:]):
                try:
                    time_n = int(sys.argv[4][1:])
                    pb = model.Problem(sys.argv[1])
                    print(pb)
                    print('-------PLNE SOLVER------')
                    pb.vehicles = pb.generate_vehicles2()
                    x, t = solver.solve_model_pulp(pb, time_n)
                    pb.make_array_after_plne(x, t)
                    pb.fleet_from_plne(x, t)
                except ValueError:
                    print('--Le fichier de vol mentionné n\'est pas répertorié--')

        else:
            print('--Le solveur PLNE prend un seul argument de base (\"fichier_de_vol.txt\")--')




