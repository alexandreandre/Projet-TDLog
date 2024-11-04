class Elevator:
    def __init__(self, elevator_id, initial_floor=0):
        """
        Initialise un ascenseur avec un identifiant unique et un étage initial.
        
        :param elevator_id: L'identifiant unique de l'ascenseur.
        :param initial_floor: L'étage initial de l'ascenseur (par défaut 0).
        """
        self.id = elevator_id  #Identifiant unique de l'ascenseur.
        self.current_floor = initial_floor  #Étage actuel de l'ascenseur.
        self.destination_floors = []  #Liste des étages que l'ascenseur doit atteindre.
        self.direction = 0  #Direction : -1 pour descendre, 1 pour monter, 0 pour inactif.
        self.is_moving = False  #Statut de l'ascenseur (en mouvement ou non).

    def add_destination(self, floor):
        if floor not in self.destination_floors:
            self.destination_floors.append(floor)
            self.destination_floors.sort(reverse=self.direction < 0)

