# main.py

import tkinter as tk
from elevator import ElevatorController
from elevator_gui import ElevatorGUI

if __name__ == "__main__":
    # Créer la fenêtre principale Tkinter
    root = tk.Tk()
    root.title("Simulation d'Ascenseurs")

    # Définir le nombre d'ascenseurs et d'étages
    num_elevators = 2
    num_floors = 10

    # Créer une instance du contrôleur d'ascenseur
    controller = ElevatorController(num_elevators, num_floors)

    # Créer et lancer l'interface graphique
    gui = ElevatorGUI(root, controller, num_floors)
    gui.run()
