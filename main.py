import sys
import display_master as disp
import model
import solver



if __name__ == "__main__":
    if len(sys.argv) > 0:
        pb = model.Problem("vols_3.txt")
        x, t = solver.solve_model_pulp(pb)
        pb.make_array_after_plne(x, t)

        print(pb.decision_t)
        print()

        for v in range(len(pb.vehicles)):
            print(pb.vehicles[v], '\n')
            print(pb.decision_x[v])
        pb.fleet_from_plne(x, t)
        disp.display_planning_per_vehicle(pb.vehicles, pb)
