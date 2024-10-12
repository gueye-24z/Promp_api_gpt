import openai
import matplotlib.pyplot as plt
import squarify
import json
import os

# Charger la clé API à partir des variables d'environnement
openai.api_key = os.getenv('OPENAI_API_KEY')


commentaires = input("Veuillez entrer votre liste de commentaires : ")



def call_gpt(prompt):
    try:
        # Appel à GPT-4 
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",  
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3
        )
        return response['choices'][0]['message']['content']
    
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")

# On définit le prompt
prompt = """
Voici une liste de commentaires portant sur un commercant. Pour chaque commentaire fais mois : une analyse de confiance, c est a dire il faut que tu me dises si le client est plutot confiant ou mefiant vis a vis de la societe, une analyse de commentaire cest a dire il faut que tu me dises si le regard du client sur la societe est positif, neutre ou negatif, une analyse de sentiment c est a dire qu il faut que tu me dises si le commentaire est plutot joyeux ou exprime de la colere. Il faut egalement que tu me dises globalement quels sont les points dominants qui reviennent le plus dans ces 20 commentaires et fais moi quelques recommandations en fonction des commentaires pour l entreprise Allianz. Fais moi une synthese de l analyse : Pour l analyse de commentaires, dis moi combien il y a de commentaires positifs, neutres et negatifs. Pareil pour les deux autres types d analyse. Pour les points dominants donne moi le titre de chaque point dominant, dis moi si il est negatif ou positif et donne moi l occurrence. Envoi moi les données en format JSON sans texte ou explication supplémentaire, je veux seulement les acollades du json et ce qui s'y trouve à lintérieur. Pas de "json ''' '''" IL faut également que la réponse me renvoie toujours le même nom des champs sinon je ne pourrai pas créer les graphiques si je réexcute le code
 
""" + commentaires
resultat_json = call_gpt(prompt)
print(resultat_json)

try:
    resultat = json.loads(resultat_json)
except json.JSONDecodeError:
    print("Erreur lors de la conversion de la chaîne en JSON.")
    resultat = None

# Vérifiez si 'resultat' est un dictionnaire avant d'essayer d'y accéder
if resultat:
    data_commentaire = [resultat["analyse_de_commentaire"]["positif"],
                        resultat["analyse_de_commentaire"]["neutre"],
                        resultat["analyse_de_commentaire"]["negatif"]]
    print(data_commentaire)
else:
    print("Impossible d'accéder aux données car la conversion a échoué.")



# Si le JSON est valide, générer les graphiques
if resultat:
    fig, axs = plt.subplots(2, 3, figsize=(18, 12))

    # Donuts pour l'analyse de commentaire
    labels_commentaire = ['Positif', 'Neutre', 'Négatif']
    data_commentaire = [resultat["analyse_de_commentaire"]["positif"],
                        resultat["analyse_de_commentaire"]["neutre"],
                        resultat["analyse_de_commentaire"]["negatif"]]
    axs[0, 0].pie(data_commentaire, labels=labels_commentaire, autopct='%1.1f%%', startangle=90, wedgeprops={'width': 0.3})
    axs[0, 0].set_title("Analyse de Commentaire")

    # Donuts pour l'analyse de sentiment
    labels_sentiment = ['Joyeux', 'Colère']
    data_sentiment = [resultat["analyse_de_sentiment"]["joyeux"],
                      resultat["analyse_de_sentiment"]["colere"]]
    axs[0, 1].pie(data_sentiment, labels=labels_sentiment, autopct='%1.1f%%', startangle=90, wedgeprops={'width': 0.3})
    axs[0, 1].set_title("Analyse de Sentiment")

    # Donuts pour l'analyse de confiance
    labels_confiance = ['Confiant', 'Méfiant']
    data_confiance = [resultat["analyse_de_confiance"]["confiant"],
                      resultat["analyse_de_confiance"]["mefiant"]]
    axs[0, 2].pie(data_confiance, labels=labels_confiance, autopct='%1.1f%%', startangle=90, wedgeprops={'width': 0.3})
    axs[0, 2].set_title("Analyse de Confiance")

    # Treemap des points positifs
    positifs = [point for point in resultat['points_dominants'] if point['type'] == 'positif']
    labels_positifs = [f"{point['titre']} ({point['occurrence']})" for point in positifs]
    sizes_positifs = [point['occurrence'] for point in positifs]
    squarify.plot(sizes=sizes_positifs, label=labels_positifs, ax=axs[1, 0], alpha=0.8)
    axs[1, 0].set_title("Treemap des Points Positifs")
    axs[1, 0].axis('off')

    # Treemap des points négatifs
    negatifs = [point for point in resultat['points_dominants'] if point['type'] == 'negatif']
    labels_negatifs = [f"{point['titre']} ({point['occurrence']})" for point in negatifs]
    sizes_negatifs = [point['occurrence'] for point in negatifs]
    squarify.plot(sizes=sizes_negatifs, label=labels_negatifs, ax=axs[1, 1], alpha=0.8)
    axs[1, 1].set_title("Treemap des Points Négatifs")
    axs[1, 1].axis('off')

    # Masquer le graphique inutile en bas à droite
    axs[1, 2].axis('off')

    # Ajuster l'espacement entre les graphiques
    plt.tight_layout()
    plt.show()
else:
    print("Impossible de générer les graphiques car le JSON est invalide.")