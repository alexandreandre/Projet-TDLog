# elevator_gui.py

import tkinter as tk
from elevator import ElevatorController
from user import User
import tkinter.simpledialog

class ElevatorGUI:
    def __init__(self, root, controller, num_floors):
        self.root = root
        self.controller = controller
        self.num_floors = num_floors
        self.elevator_width = 50
        self.elevator_height = 30
        self.canvas_width = 100 + len(controller.elevators) * (self.elevator_width + 10)
        self.canvas_height = num_floors * 60
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack(side=tk.RIGHT)
        self.elevator_rects = []
        self.create_elevators()
        self.create_floor_labels()
        self.users = {}
        self.create_floor_buttons()
        self.update_gui()

    def create_elevators(self):
        for i, elevator in enumerate(self.controller.elevators):
            x0 = 50 + i * (self.elevator_width + 10)
            y0 = self.canvas_height - elevator.current_floor * 60 - self.elevator_height - 10
            rect = self.canvas.create_rectangle(
                x0, y0, x0 + self.elevator_width, y0 + self.elevator_height, fill="gray"
            )
            self.elevator_rects.append(rect)

    def create_floor_labels(self):
        for floor in range(self.num_floors):
            y = self.canvas_height - floor * 60 - 20
            self.canvas.create_line(0, y, self.canvas_width, y, fill="lightgray")
            self.canvas.create_text(5, y - 20, anchor="nw", text=f"Étage {floor}")

    def create_floor_buttons(self):
        self.floor_buttons_frame = tk.Frame(self.root)
        self.floor_buttons_frame.pack(side=tk.LEFT, padx=10)
        for floor in reversed(range(self.num_floors)):
            btn = tk.Button(
                self.floor_buttons_frame,
                text=f"Ajouter utilisateur à l'étage {floor}",
                command=lambda f=floor: self.add_user(f)
            )
            btn.pack(pady=2)

    def add_user(self, floor):
        dest_floor = tk.simpledialog.askinteger(
            "Destination",
            f"Entrez l'étage de destination pour l'utilisateur à l'étage {floor}:",
            minvalue=0,
            maxvalue=self.num_floors - 1
        )
        if dest_floor is not None and dest_floor != floor:
            user = self.controller.add_user(floor, dest_floor)
            # Afficher l'utilisateur sur le canvas
            x = 10  # Position x pour les utilisateurs en attente
            y = self.canvas_height - floor * 60 - self.elevator_height - 20
            circle = self.canvas.create_oval(
                x, y, x + 20, y + 20, fill="blue", tags=f"user_{user.id}"
            )
            self.users[user.id] = circle

    def update_gui(self):
        self.controller.step()
        # Mettre à jour les ascenseurs
        for i, elevator in enumerate(self.controller.elevators):
            x0 = 50 + i * (self.elevator_width + 10)
            y0 = self.canvas_height - elevator.current_floor * 60 - self.elevator_height - 10
            self.canvas.coords(
                self.elevator_rects[i],
                x0, y0, x0 + self.elevator_width, y0 + self.elevator_height
            )
            color = "green" if elevator.is_moving else "gray"
            self.canvas.itemconfig(self.elevator_rects[i], fill=color)
        # Mettre à jour les utilisateurs
        for user in list(self.controller.users):
            if not user.arrived:
                if user.in_elevator:
                    # Position de l'utilisateur dans l'ascenseur
                    elevator = self.controller.elevators[user.elevator_id]
                    i = elevator.id
                    x = 50 + i * (self.elevator_width + 10) + 15
                    y = self.canvas_height - elevator.current_floor * 60 - self.elevator_height - 15
                else:
                    # Position de l'utilisateur en attente
                    x = 10
                    y = self.canvas_height - user.current_floor * 60 - self.elevator_height - 20
                self.canvas.coords(
                    self.users[user.id],
                    x, y, x + 20, y + 20
                )
            else:
                # Supprimer l'utilisateur arrivé à destination
                self.canvas.delete(self.users[user.id])
                del self.users[user.id]
                self.controller.users.remove(user)
        self.root.after(1000, self.update_gui)

    def run(self):
        self.root.mainloop()