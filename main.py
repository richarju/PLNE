# import sys
import model
import solver
# import heuristic
# import pulp


'''
remains to do --> solve_model_pulp(pb)
"""'''


if __name__ == "__main__":
    # if len(sys.argv) != 2:
        # print("Le programme prend un seul argument")
    # else:
    pb = model.Problem("vols_2.txt")
    # print(pb)
    solver.solve_model_pulp(pb)




