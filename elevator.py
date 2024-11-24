# elevator.py
from user import User


class Elevator:
    def __init__(self, elevator_id, initial_floor=0):
        """
        Initialise un ascenseur avec un identifiant unique et un étage initial.

        :param elevator_id: L'identifiant unique de l'ascenseur.
        :param initial_floor: L'étage initial de l'ascenseur (par défaut 0).
        """
        self.id = elevator_id  # Identifiant unique de l'ascenseur.
        self.current_floor = initial_floor  # Étage actuel de l'ascenseur.
        self.destination_floors = []  # Liste des étages que l'ascenseur doit atteindre.
        self.direction = (
            0  # Direction : -1 pour descendre, 1 pour monter, 0 pour inactif.
        )
        self.is_moving = False  # Statut de l'ascenseur (en mouvement ou non).

    def add_destination(self, floor):
        if floor not in self.destination_floors:
            self.destination_floors.append(floor)
            self.destination_floors.sort(reverse=self.direction < 0)

    def move(self):
        if self.destination_floors:
            self.is_moving = True
            next_floor = self.destination_floors[0]
            if self.current_floor < next_floor:
                self.current_floor += 1
                self.direction = 1
            elif self.current_floor > next_floor:
                self.current_floor -= 1
                self.direction = -1
            else:
                # Arrivé à l'étage
                self.destination_floors.pop(0)
                self.direction = 0 if not self.destination_floors else self.direction
                # Gérer les passagers qui descendent
                departing_passengers = [
                    p
                    for p in self.passengers
                    if p.destination_floor == self.current_floor
                ]
                for passenger in departing_passengers:
                    self.passengers.remove(passenger)
                    passenger.arrived = True
                # Vérifier si d'autres passagers montent
        else:
            self.is_moving = False
            self.direction = 0

    def __repr__(self):
        return f"Ascenseur {self.id} à l'étage {self.current_floor}"


class ElevatorController:
    def __init__(self, num_elevators, num_floors):
        self.elevators = [Elevator(elevator_id=i) for i in range(num_elevators)]
        self.num_floors = num_floors
        self.users = []
        self.user_id_counter = 0

    def request_elevator(self, user):
        # Trouver le meilleur ascenseur pour l'utilisateur
        best_elevator = min(
            self.elevators, key=lambda e: abs(e.current_floor - user.current_floor)
        )
        best_elevator.add_destination(user.current_floor)
        user.elevator_id = best_elevator.id

    def update_users(self):
        for user in self.users:
            if not user.arrived:
                elevator = self.elevators[user.elevator_id]
                if user.in_elevator:
                    if elevator.current_floor == user.destination_floor:
                        # L'utilisateur est arrivé à destination
                        user.arrived = True
                        elevator.passengers.remove(user)
                else:
                    if (
                        elevator.current_floor == user.current_floor
                        and not user.in_elevator
                    ):
                        # L'utilisateur monte dans l'ascenseur
                        user.in_elevator = True
                        elevator.add_destination(user.destination_floor)
                        elevator.passengers.append(user)

    def step(self):
        for elevator in self.elevators:
            elevator.move()
        self.update_users()

    def add_user(self, current_floor, destination_floor):
        user = User(self.user_id_counter, current_floor, destination_floor)
        self.user_id_counter += 1
        self.users.append(user)
        self.request_elevator(user)
        return user
