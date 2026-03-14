import cv2
from ultralytics import YOLO

class DroneVision:
    def __init__(self):
        # On charge le modèle au démarrage
        # yolov8n.pt est la version "Nano", la plus rapide pour un ordi portable
        self.model = YOLO('yolov8n.pt') 
        self.cap = cv2.VideoCapture(0) # 0 = Webcam de l'ordi

    def obtenir_objets(self):
        """Lit la caméra et retourne la liste des objets détectés"""
        ret, frame = self.cap.read()
        if not ret:
            return [], None

        # L'IA analyse l'image
        results = self.model(frame, conf=0.5, verbose=False)
        
        # On extrait les noms des objets (ex: ['person', 'chair'])
        objets_detectes = []
        for r in results:
            for box in r.boxes:
                nom = self.model.names[int(box.cls[0])]
                objets_detectes.append(nom)
        
        # On garde l'image annotée pour l'affichage
        image_annotee = results[0].plot()
        
        return objets_detectes, image_annotee

    def arreter(self):
        """Ferme la caméra proprement"""
        self.cap.release()
        cv2.destroyAllWindows()