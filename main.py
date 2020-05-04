import sys
import display_master as disp
import model
import solver


if __name__ == "__main__":
    if len(sys.argv) > 0:
        pb = model.Problem("vols_2.txt")
        x, t = solver.solve_model_pulp(pb)
        pb.make_array_after_plne(x, t)
        pb.fleet_from_plne(x, t)
        disp.display_planning_per_vehicle(pb)
