# import sys
import model
# import solver
import heuristic
import display_master as disp


if __name__ == "__main__":
    pb = model.Problem("vols_2.txt")
    print(pb)
    pb.vehicles = heuristic.heuristic_glouton(pb)
    disp.display_planning_per_vehicle(pb)
    """
    if len(sys.argv) == 2:
        try:
            pb = model.Problem(sys.argv[1])
            pb.vehicles = pb.generate_vehicles2()
            x, t = solver.solve_model_pulp(pb)
            pb.make_array_after_plne(x, t)
            pb.fleet_from_plne(x, t)
            disp.display_planning_per_vehicle(pb)
        except FileNotFoundError:
            print('--Le fichier de vol mentionné n\'est pas répertorié--')


    elif len(sys.argv) == 3:
        if sys.argv[2] == '-nodisp':
            try:
                pb = model.Problem(sys.argv[1])
                pb.vehicles = pb.generate_vehicles2()
                x, t = solver.solve_model_pulp(pb)
                pb.make_array_after_plne(x, t)
                pb.fleet_from_plne(x, t)
            except FileNotFoundError:
                print('--Le fichier de vol mentionné n\'est pas répertorié--')

        elif int(sys.argv[2][1:]):
            try:
                try:
                    time_n = int(sys.argv[2][1:])
                    pb = model.Problem(sys.argv[1])
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

    elif len(sys.argv) == 4:
        if sys.argv[2] == '-nodisp' and int(sys.argv[3][1:]):
            try:
                time_n = int(sys.argv[3][1:])
                pb = model.Problem(sys.argv[1])
                pb.vehicles = pb.generate_vehicles2()
                x, t = solver.solve_model_pulp(pb, time_n)
                pb.make_array_after_plne(x, t)
                pb.fleet_from_plne(x, t)
            except ValueError:
                print('--Le fichier de vol mentionné n\'est pas répertorié--')

    else:
        print('--Le solveur PLNE prend un seul argument de base (\"fichier_de_vol.txt\")--')
    """



