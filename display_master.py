import matplotlib.pyplot as plt
import matplotlib.lines as line


def display_planning_per_vehicle(pb):
    """
    :param pb: problem solved
    :return: a matplotlib display that shows the planning for each vehicle
    """
    scale_n = len(pb.vehicles)
    color_list = ['red', 'blue', 'green', 'black', 'magenta', 'darkred', 'darkblue','orange', 'yellow', 'cyan']
    fig, ax = plt.subplots()
    positions = list()
    label = list()
    parkings_used = list()
    solution_wo_nvr = [vehicle for vehicle in pb.vehicles if vehicle.type.name != 'NVR']
    max_y = len(solution_wo_nvr) + 0.01 * scale_n
    for i, vehicle in enumerate(solution_wo_nvr):
        positions.append(i)
        label.append('APV' + str(i+1) + ' ({})'.format(vehicle.type.name))
        for task in vehicle.tasks:
            print(task)
            beg = task.t_i
            end = task.t_i + task.d_i
            parkings_used.append(task.airplane.parking)
            ax.plot([beg, end], [i, i], linewidth=2, color=color_list[task.airplane.parking-1],
                    label='parking '+str(task.airplane.parking))
            ax.text(beg + 2.5, i + 0.01 * scale_n, '{} - {}'.format(task.type.name, task.airplane.fl_nbr),
                    ha="center", va="center", size=7, weight="bold")
            ax.text(beg, i - 0.012 * scale_n, '{}'.format(beg), ha="center", va="center", size=6)
            ax.text(end, i - 0.012 * scale_n, '{}'.format(end), ha="center", va="center", size=6)
    for flight in pb.flights:
        ax.plot([flight.m_a-0.5, flight.m_a-0.5], [-0.5, max_y + pb.flights.index(flight) % 2],
                linewidth=0.8, color=color_list[flight.parking-1])
        ax.text(flight.m_a, max_y + pb.flights.index(flight) % 2, 'EIBT {}'.format(flight.fl_nbr), size=7, ha="center")
        ax.plot([flight.m_d, flight.m_d], [-0.5, max_y + pb.flights.index(flight) % 2],
                linewidth=0.8, color=color_list[flight.parking-1])
        ax.text(flight.m_d, max_y + pb.flights.index(flight) % 2, 'EOBT {}'.format(flight.fl_nbr), size=7, ha="center")
    ax.grid(axis='y', color='grey')
    plt.yticks(positions, label, size=7)
    labels = ['parking '+str(p) for p in list(set(parkings_used))]
    handles = [line.Line2D([0, 0], [0, 1], color=color_list[p-1]) for p in list(set(parkings_used))]
    ax.legend(handles, labels, prop={'size': 7}, loc=4)
    plt.xlabel('Time (min)')
    plt.ylabel('Airport Vehicles (APV)')
    plt.title("Airport Vehicles Fleet Planning")
    plt.show()
