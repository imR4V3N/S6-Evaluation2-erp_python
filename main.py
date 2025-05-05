import csv

# Liste pour stocker les dictionnaires
data = []

# Ouvrir le fichier CSV et le lire
with open('/home/raven/Workspace/Evaluation2/Documents/csv/modele/1.csv', mode='r', newline='', encoding='utf-8') as file:
    reader = csv.reader(file)
    
    # Lire les en-têtes du CSV (première ligne)
    headers = next(reader)
    
    # Lire chaque ligne de données et créer un dictionnaire pour chaque ligne
    for row in reader:
        row_dict = {headers[i]: row[i] for i in range(len(headers))}
        data.append(row_dict)

# Afficher les données
for item in data:
    print(item)
