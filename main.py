import cv2
from ultralytics import YOLO
import openai
from gtts import gTTS
import os
import threading
import time

# --- CONFIGURATION (À REMPLIR) ---
# Colle ta clé API OpenAI ici entre les guillemets
openai.api_key = "VOTRE_CLE_API_ICI"

# Chargement du modèle de vision (YOLOv8)
vision_model = YOLO('yolov8n.pt') 

def parler(texte):
    """Transforme le texte en voix de manière asynchrone"""
    def execution():
        try:
            tts = gTTS(text=texte, lang='fr')
            tts.save("reponse.mp3")
            # Commande Windows pour lire le son
            os.system("start /min mp3play.exe reponse.mp3" if os.name == 'nt' else "afplay reponse.mp3")
        except:
            pass
    threading.Thread(target=execution).start()

def interagir_avec_ia(objets_visibles, question_utilisateur):
    """Envoie les données de vision et la question à OpenAI"""
    print("🧠 L'IA réfléchit...")
    
    # Création du "contexte" pour l'IA
    liste_objets = ", ".join(objets_visibles) if objets_visibles else "aucun objet n'est visible"
    
    # Instructions système pour définir le rôle de l'IA
    contexte_systeme = f"""
    Tu es l'IA compagnon d'une personne aveugle, intégrée dans son drone guide.
    Ta caméra détecte actuellement ces objets : {liste_objets}.
    Ta priorité est la sécurité et l'autonomie de l'utilisateur.
    Réponds à ses questions de manière concise, rassurante et pratique.
    N'invente pas d'objets qui ne sont pas dans la liste.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", # Modèle rapide et moins cher pour un hackathon
            messages=[
                {"role": "system", "content": contexte_systeme},
                {"role": "user", "content": question_utilisateur}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Désolé, j'ai eu un problème de connexion à mon cerveau. Erreur : {e}"

# --- BOUCLE PRINCIPALE SIMULÉE AVEC WEBCAM ---
cap = cv2.VideoCapture(0) # 0 pour la webcam

print("🟢 Compagnon IA AeroHack activé !")
parler("Bonjour, je suis votre compagnon guide. Comment puis-je vous aider ?")

# Variable pour simuler une question de l'utilisateur
# Dans le produit final, cela viendrait de la reconnaissance vocale
question_utilisateur = "Dis-moi ce que tu vois autour de moi ?"

# On simule une seule interaction pour la démo
count = 0
while cap.isOpened() and count < 1:
    ret, frame = cap.read()
    if not ret:
        break

    # 1. ANALYSE VISUELLE
    results = vision_model(frame, conf=0.5, verbose=False)
    objets_detectes = [vision_model.names[int(box.cls[0])] for r in results for box in r.boxes]

    # 2. INTERACTION IA
    # On imagine que l'utilisateur pose sa question ici
    print(f"👤 Utilisateur : {question_utilisateur}")
    reponse_ia = interagir_avec_ia(objets_detectes, question_utilisateur)
    
    print(f"🤖 IA : {reponse_ia}")
    parler(reponse_ia)
    
    # Affichage visuel pour la démo
    annotated_frame = results[0].plot()
    cv2.imshow("Vue du Drone (Webcam)", annotated_frame)
    
    count += 1 # On arrête après une interaction pour le test
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

time.sleep(5) # Laisser le temps à l'audio de finir
cap.release()
cv2.destroyAllWindows()
