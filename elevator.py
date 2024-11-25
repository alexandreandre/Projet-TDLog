# elevator.py
from user import User


class Elevator:

    def __init__(self, elevator_id, initial_floor=0, controller=None):
        """
        Initialise un ascenseur avec un identifiant unique et un étage initial.
        
        :param elevator_id: L'identifiant unique de l'ascenseur.
        :param initial_floor: L'étage initial de l'ascenseur (par défaut 0).
        :param controller: L'objet ElevatorController auquel cet ascenseur appartient (par défaut None).
        """
        self.pending_destinations = []  # Nouvelle liste pour les destinations en attente
        self.id = elevator_id  # Identifiant unique de l'ascenseur.
        self.current_floor = initial_floor  # Étage actuel de l'ascenseur.
        self.destination_floors = []  # Liste des étages que l'ascenseur doit atteindre.
        self.direction = 0  # Direction : -1 pour descendre, 1 pour monter, 0 pour inactif.
        self.is_moving = False  # Statut de l'ascenseur (en mouvement ou non).
        self.passengers = []  # Liste des passagers actuellement dans l'ascenseur.
        self.controller = controller  # Ajouter une référence à l'objet ElevatorController

    def add_destination(self, floor):
        if floor not in self.destination_floors and floor not in self.pending_destinations:
            if self.direction == 0:
                # Si l'ascenseur est inactif, il accepte la destination
                self.destination_floors.append(floor)
                # Définir la direction
                if floor > self.current_floor:
                    self.direction = 1
                elif floor < self.current_floor:
                    self.direction = -1
                else:
                    self.direction = 0
                # Trier les destinations
                self.destination_floors.sort(reverse=self.direction < 0)
            else:
                # Si l'ascenseur est en mouvement
                if (self.direction == 1 and floor >= self.current_floor) or \
                (self.direction == -1 and floor <= self.current_floor):
                    # La destination est dans la même direction
                    self.destination_floors.append(floor)
                    self.destination_floors.sort(reverse=self.direction < 0)
                else:
                    # La destination est dans la direction opposée
                    self.pending_destinations.append(floor)


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

            if self.current_floor == next_floor:
                # Arrivé à l'étage cible
                departing_passengers = [
                    p for p in self.passengers
                    if p.destination_floor == self.current_floor
                ]
                for passenger in departing_passengers:
                    self.passengers.remove(passenger)
                    passenger.arrived = True

                # Supprimer l'étage atteint de la liste des destinations
                self.destination_floors.pop(0)

                # Mettre à jour les destinations
                self.update_destinations()

                # Si plus de destinations, vérifier les destinations en attente
                if not self.destination_floors and self.pending_destinations:
                    # Déplacer les destinations en attente vers la liste principale
                    self.destination_floors = self.pending_destinations.copy()
                    self.pending_destinations.clear()
                    # Définir la nouvelle direction
                    if self.destination_floors[0] > self.current_floor:
                        self.direction = 1
                    else:
                        self.direction = -1
                    # Trier les destinations
                    self.destination_floors.sort(reverse=self.direction < 0)
                elif not self.destination_floors:
                    self.is_moving = False
                    self.direction = 0
        else:
            if self.pending_destinations:
                self.destination_floors = self.pending_destinations.copy()
                self.pending_destinations.clear()
                if self.destination_floors[0] > self.current_floor:
                    self.direction = 1
                else:
                    self.direction = -1
                self.destination_floors.sort(reverse=self.direction < 0)
                self.is_moving = True
            else:
                self.is_moving = False
                self.direction = 0


    def update_destinations(self):
        # Ajouter les destinations des passagers dans l'ascenseur
        for user in self.passengers:
            if user.destination_floor not in self.destination_floors:
                self.add_destination(user.destination_floor)

        # Vérifier les nouveaux utilisateurs à l'étage actuel
        for user in self.controller.users:
            if user.current_floor == self.current_floor and not user.in_elevator and not user.arrived:
                # Vérifier si le passager va dans la même direction
                if (self.direction == 1 and user.destination_floor > self.current_floor) or \
                (self.direction == -1 and user.destination_floor < self.current_floor) or \
                self.direction == 0:
                    user.in_elevator = True
                    user.elevator_id = self.id
                    self.passengers.append(user)
                    self.add_destination(user.destination_floor)



    def __repr__(self):
        """
        Représentation textuelle de l'ascenseur pour faciliter le débogage et l'affichage.
        """
        return f"Ascenseur {self.id} à l'étage {self.current_floor}"


class ElevatorController:
    def __init__(self, num_elevators, num_floors):
        """
        Initialise le contrôleur avec un nombre d'ascenseurs et un nombre d'étages.
        """
        self.elevators = [Elevator(elevator_id=i, controller=self) for i in range(num_elevators)]  # Passer 'self' comme controller à chaque ascenseur
        self.num_floors = num_floors  # Nombre d'étages dans l'immeuble
        self.users = []  # Liste des utilisateurs (passagers)
        self.user_id_counter = 0  # Compteur d'ID pour les utilisateurs


    def request_elevator(self, user):
        """
        Trouve l'ascenseur le plus proche de l'utilisateur et lui attribue cet ascenseur.
        """
        # Trouve l'ascenseur avec la distance la plus courte par rapport à l'étage de l'utilisateur
        best_elevator = min(
            self.elevators, key=lambda e: abs(e.current_floor - user.current_floor)
        )
        # Ajoute l'étage de l'utilisateur à la liste des destinations de l'ascenseur
        best_elevator.add_destination(user.current_floor)
        user.elevator_id = best_elevator.id  # Associe l'utilisateur à l'ascenseur choisi

    def update_users(self):
        """
        Met à jour les utilisateurs : vérifie s'ils sont dans l'ascenseur et s'ils arrivent à destination.
        """
        for user in self.users:
            if not user.arrived:  # Si l'utilisateur n'est pas encore arrivé
                elevator = self.elevators[user.elevator_id]  # L'ascenseur associé à cet utilisateur
                if user.in_elevator:
                    # L'utilisateur est dans l'ascenseur
                    if elevator.current_floor == user.destination_floor:  # Si l'ascenseur est arrivé à destination
                        user.arrived = True  # L'utilisateur est arrivé
                        elevator.passengers.remove(user)  # Retirer l'utilisateur de la liste des passagers
                    else:
                        # L'utilisateur est toujours dans l'ascenseur,  l'ascenseur bouge encore
                        continue
                else:
                    # Si l'utilisateur n'est pas encore dans l'ascenseur, il attend son ascenseur
                    if elevator.current_floor == user.current_floor and not user.in_elevator:
                        user.in_elevator = True  # L'utilisateur entre dans l'ascenseur
                        elevator.add_destination(user.destination_floor)  # Ajouter sa destination
                        elevator.passengers.append(user)  # Ajouter l'utilisateur à la liste des passagers

    def step(self):
        """
        Effectue une étape de simulation : déplace les ascenseurs et met à jour les utilisateurs.
        """
        for elevator in self.elevators:
            elevator.move()  # Déplace chaque ascenseur
        self.update_users()  # Met à jour l'état des utilisateurs

    def add_user(self, current_floor, destination_floor):
        """
        Crée un utilisateur et lui associe un ascenseur. L'utilisateur est ajouté à la liste des utilisateurs.
        """
        user = User(self.user_id_counter, current_floor, destination_floor)
        self.user_id_counter += 1
        self.users.append(user)  # Ajouter l'utilisateur à la liste des utilisateurs
        self.request_elevator(user)  # Demander un ascenseur pour cet utilisateur
        return user
