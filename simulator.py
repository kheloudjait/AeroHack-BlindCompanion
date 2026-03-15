from simulateddrone import SimulatedDrone

# On peut ajouter ici des fonctions de simulation 
# si le drone réel n'est pas branché
class DroneSimulator(SimulatedDrone):
    def connect(self):
        print("🔗 [SIMULATION] Connexion au drone virtuelle réussie.")
        return True
    
    def end(self):
        print("🔌 [SIMULATION] Connexion fermée.")