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
