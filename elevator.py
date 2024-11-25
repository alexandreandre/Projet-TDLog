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
        self.id = elevator_id  # Identifiant unique de l'ascenseur.
        self.current_floor = initial_floor  # Étage actuel de l'ascenseur.
        self.destination_floors = []  # Liste des étages que l'ascenseur doit atteindre.
        self.direction = 0  # Direction : -1 pour descendre, 1 pour monter, 0 pour inactif.
        self.is_moving = False  # Statut de l'ascenseur (en mouvement ou non).
        self.passengers = []  # Liste des passagers actuellement dans l'ascenseur.
        self.controller = controller  # Ajouter une référence à l'objet ElevatorController

    def add_destination(self, floor):
        """
        Ajoute une destination à l'ascenseur, si elle n'est pas déjà présente.
        La liste des destinations est triée pour optimiser le mouvement de l'ascenseur.
        """
        if floor not in self.destination_floors:
            # Si l'ascenseur monte et qu'un appel est fait pour un étage inférieur,
            # on l'ajoute à la liste des destinations mais ne change pas la direction immédiatement.
            if self.direction == 1 and floor < self.current_floor:
                self.destination_floors.append(floor)  # Ajout pour plus tard (on va d'abord atteindre les étages supérieurs)
            else:
                self.destination_floors.append(floor)  # Ajout normal

            # Trier les destinations pour optimiser le mouvement de l'ascenseur
            self.destination_floors.sort(reverse=self.direction < 0)  # Trier les destinations en fonction de la direction (descendante ou montante)

    def move(self):
        """
        Effectue le mouvement de l'ascenseur. L'ascenseur se déplace d'un étage à la fois, en fonction de
        ses destinations et de sa direction. Une fois arrivé à une destination, il dépose les passagers.
        """
        # Si des destinations existent
        if self.destination_floors:
            self.is_moving = True  # L'ascenseur commence à bouger
            next_floor = self.destination_floors[0]  # L'étage cible à atteindre

            # Si l'ascenseur doit monter
            if self.current_floor < next_floor:
                self.current_floor += 1  # Monte d'un étage
                self.direction = 1  # Direction vers le haut
            # Si l'ascenseur doit descendre
            elif self.current_floor > next_floor:
                self.current_floor -= 1  # Descend d'un étage
                self.direction = -1  # Direction vers le bas

            # Arrivé à l'étage
            if self.current_floor == next_floor:
                # Traiter les passagers qui descendent à cet étage
                departing_passengers = [
                    p for p in self.passengers
                    if p.destination_floor == self.current_floor
                ]
                for passenger in departing_passengers:
                    self.passengers.remove(passenger)
                    passenger.arrived = True

                # Supprimer l'étage atteint de la liste des destinations
                self.destination_floors.pop(0)

                # Vérifier si d'autres demandes doivent être prises en compte pendant le trajet
                self.update_destinations()

                # Si l'ascenseur n'a plus de destinations et de passagers, il s'arrête
                if not self.destination_floors and not self.passengers:
                    self.is_moving = False  # L'ascenseur arrête son mouvement
                    self.direction = 0  # Réinitialisation de la direction à 0 (inactif)
        else:
            # Si aucune destination n'est définie
            if not self.passengers:  # Si l'ascenseur n'a plus de passagers
                self.is_moving = False  # L'ascenseur reste immobile
                self.direction = 0  # L'ascenseur ne bouge plus

    def update_destinations(self):
        """
        Met à jour la liste des destinations en fonction des nouveaux utilisateurs appelant l'ascenseur.
        Cette méthode doit être appelée à chaque arrêt de l'ascenseur pour s'assurer qu'il réévalue ses destinations.
        """
        # Ajouter des destinations des utilisateurs qui ne sont pas encore à bord
        for user in self.passengers:
            if user.destination_floor not in self.destination_floors:
                self.add_destination(user.destination_floor)

        # Vérifier si de nouveaux utilisateurs ont appelé l'ascenseur pendant son trajet
        for user in self.controller.users:
            if user.current_floor == self.current_floor and not user.in_elevator:
                self.add_destination(user.destination_floor)
                user.in_elevator = True
                self.passengers.append(user)


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
