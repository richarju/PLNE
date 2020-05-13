class Verification:

    def __init__(self, pb_initial, pb_solved):
        self.problem_init = pb_initial
        self.problem_solved = pb_solved
        self.executed_tests = list()
        self.vehicles = pb_solved.vehicles
        self.tasks = pb_solved.all_tasks
        self.flights = pb_solved.flights

    def test_precedence_for_a_flight(self, flight):
        tasks = [t for t in self.tasks if t.airplane.fl_nbr == flight.fl_nbr]
        for task in tasks:
            prev_names = [t.type.name for t in task.prev]
            prev_tasks = [t for t in tasks if t.type.name in prev_names]
            for tsk in prev_tasks:
                if tsk.t_i + tsk.d_i <= task.t_i:
                    pass
                else:
                    return False
        return True


    def test_creneau_for_a_flight(self, flight_solved):
        """
        :param flight_solved: flight after resolution
        :return: bool(le creneau prévu est respecté)
        """
        fl_nbr = flight_solved.fl_nbr
        flight_init = [fl for fl in self.problem_init.flights if fl.fl_nbr == fl_nbr][0]
        return flight_solved.m_a >= flight_init.m_a and flight_solved.m_d <= flight_init.m_d

    def task_is_done_once_and_only_once(self, task_init):  # OK
        """
        :param task_init: task avant traitement
        :return: s'assure que la task est faite une fois en tout
        """
        n = 0
        for task in self.problem_solved.all_tasks:
            if task_init.type.name == task.type.name:
                if task_init.airplane.fl_nbr == task.airplane.fl_nbr:
                    n += 1
                else:
                    pass
            else:
                pass
        return n == 1

    def test_all_task_are_done(self):  # OK
        n_i, n_s = 0, 0
        for flight in self.problem_solved.flights:
            n_s += len(flight.task_to_do)
        for flight in self.problem_init.flights:
            n_i += len(flight.task_to_do)
        return n_i == n_s

    def vehicle_has_time_to_move_between_tasks(self, vehicle):  # OK
        tasks = sorted(vehicle.tasks, key=lambda t: t.t_i)
        if vehicle.type.name == 'NVR':
            return True
        else:
            for i in range(len(tasks)-1):
                task_1, task_2 = tasks[i], tasks[i+1]
                delta_move_solution = task_2.t_i - task_1.t_i - task_1.d_i
                p_1 = task_1.airplane.parking-1
                p_2 = task_2.airplane.parking-1
                delta_move_available = self.problem_init.parkings[p_1][p_2] / vehicle.type.speed
                if delta_move_solution >= delta_move_available:
                    pass
                else:
                    return False
            return True

    @staticmethod
    def vehicle_has_one_task_at_a_time(vehicle):  # OK
        tasks = sorted(vehicle.tasks, key=lambda t: t.t_i)
        for i in range(len(tasks) - 1):
            task_1, task_2 = tasks[i], tasks[i + 1]
            if task_1.t_i + task_1.d_i <= task_2.t_i:
                pass
            else:
                return False
        return True

    def examin_vehicles_planning(self):  # OK
        for vehicle_treated in self.vehicles:
            if self.vehicle_has_time_to_move_between_tasks(vehicle_treated):
                pass
            else:
                return False
        return True

    def examin_vehicles_movement(self):  # OK
        for vehicle_treated in self.vehicles:
            if self.vehicle_has_one_task_at_a_time(vehicle_treated):
                pass
            else:
                return False
        return True

    def examin_tasks_once(self):  # OK
        for task_init in self.problem_init.all_tasks:
            if self.task_is_done_once_and_only_once(task_init):
                pass
            else:
                return False
        return True

    def examin_tasks_all(self):  # OK
        return self.test_all_task_are_done()


    def examin_flights_precedence(self):  # OK
        for flight_treated in self.flights:
            if self.test_precedence_for_a_flight(flight_treated):
                pass
            else:
                return False
        return True

    def examin_flights_creneau(self):  # OK
        for flight_treated in self.flights:
            if self.test_creneau_for_a_flight(flight_treated):
                pass
            else:
                return False
        return True


    def execute(self):
        a, b = self.examin_tasks_all(), self.examin_tasks_once()
        c, d = self.examin_flights_precedence(), self.examin_flights_creneau()
        e, f = self.examin_vehicles_movement(), self.examin_vehicles_planning()
        g = a and b and c and d and e and f
        n_vehicles = len([v for v in self.problem_solved.vehicles if v.type.name != 'NVR'])
        print('----------SOLUTION-------------------------------------')
        print('NOMBRE DE VOLS................................... {}'.format(len(self.problem_solved.flights)))
        print('NOMBRE DE TÂCHES................................. {}'.format(len(self.problem_solved.all_tasks)))
        print('NOMBRE DE VÉHICULES NÉCESSAIRES.................. {}'.format(n_vehicles))
        print()
        print('----------TEST EFFECTUÉ----------------------RÉSULTAT--')
        print('Toutes les tâches sont traitées..................', a)
        print('Chaque tâche n\'est faite qu\'une fois.............', b)
        print('La précédence est vérifiée pour chaque tâche.....', c)
        print('Les créneaux de vols sont respectés..............', d)
        print('Les mouvements de véhicules sont réalisables.....', e)
        print('Chaque véhicule a une seule tâche à la fois......', f)
        print()
        print('-------------------------------------------------------')
        if g:
            print('LE PROGRAMME D\'ASSISTANCE EN ESCALE EST RÉALISABLE')
        else:
            print('UNE ERREUR REND IRRÉALISABLE CE PROGRAMME D\'ASSISTANCE EN ESCALE')
        print('-------------------------------------------------------\n')

