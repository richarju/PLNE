import sys
import model
import solver
import display_master as disp


if __name__ == "__main__":
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

        else:
            print('--L\'un des deux arguments n\'est pas bon : merci de préciser -nodisp si '
                  'vous ne voulez pas d\'affichage--')

    else:
        print('--Le solveur PLNE prend un seul argument de base (\"fichier_de_vol.txt\")--')



