# user.py

class User:
    def __init__(self, user_id, current_floor, destination_floor):
        self.id = user_id
        self.current_floor = current_floor
        self.destination_floor = destination_floor
        self.in_elevator = False
        self.arrived = False
        self.elevator_id = None  # ID de l'ascenseur où l'utilisateur se trouve

    def __repr__(self):
        return f"User {self.id} from {self.current_floor} to {self.destination_floor}"
