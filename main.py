import sys
import model
import solver
import display_master as disp


if __name__ == "__main__":
    if len(sys.argv) > 0:
        pb = model.Problem("vols_10_2.txt")
        pb.vehicles = pb.generate_vehicles2()
        x, t = solver.solve_model_pulp(pb)
        pb.make_array_after_plne(x, t)
        pb.fleet_from_plne(x, t)
        disp.display_planning_per_vehicle(pb)
