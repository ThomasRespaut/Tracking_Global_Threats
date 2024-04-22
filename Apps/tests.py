import requests
import random
import time
from bs4 import BeautifulSoup
import mysql.connector

# Se connecter à la base de données MySQL
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="nato"
)

# Créer un curseur pour exécuter les requêtes SQL
mycursor = mydb.cursor()


countries = [
    "threat"
]

#countries = ["Russia"]

for country in countries:

    print(country)
    compteur =  0

    for page in range(1, 101):
        print(compteur)
        # URL de la page des nouvelles de l'OTAN
        url = f"https://www.nato.int/cps/en/natohq/news.htm?query={country}&search_types=News&display_mode=news&date_from=dd.mm.yyyy&date_to=dd.mm.yyyy&keywordquery=*&chunk={page}#"

        # Choisir un User-Agent courant
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"

        # Définir les en-têtes de la requête
        headers = {
            "User-Agent": user_agent,
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive"
        }

        # Envoyer la requête en imitant un délai aléatoire entre 1 et 5 secondes
        response = requests.get(url, headers=headers)
        #time.sleep(random.uniform(1, 5))

        soup = BeautifulSoup(response.content, "html.parser")


        # Trouver tous les éléments tr dans la table
        tr_elements = soup.find_all("tr")

        if tr_elements:

            for tr in tr_elements:
                compteur +=1
                # Trouver tous les éléments td à l'intérieur de cet élément tr
                td_elements = tr.find_all("td")

                # Vérifier s'il y a au moins trois éléments td
                if len(td_elements) >= 3:
                    # Récupérer le contenu textuel de chaque élément td
                    date = td_elements[0].text.strip()
                    # Vérifier si un élément img existe dans le deuxième td
                    image_tag = td_elements[1].find("img")
                    image = "https://www.nato.int/" + image_tag['src'].strip() if image_tag else "Pas d'image disponible"

                    content_elements = td_elements[2].find_all(["p", "small"])

                    # Vérifier si des éléments de contenu ont été trouvés
                    if content_elements:
                        # Afficher le premier élément comme titre s'il existe
                        title = content_elements[0].text.strip()
                        #print("Title:", title)

                        # Afficher le deuxième élément comme contenu s'il existe
                        if len(content_elements) > 1:
                            content = content_elements[1].text.strip()
                            #print("Content:", content)

                    # Trouver tous les éléments <p> avec la classe "introtxt" dans le troisième td
                    p_elements = td_elements[2].find_all("p", class_="introtxt")

                    # Parcourir chaque élément <p> avec la classe "introtxt"
                    for p in p_elements:
                        # Trouver l'élément <a> à l'intérieur de cet élément <p>
                        a_element = p.find("a")
                        # Vérifier si l'élément <a> existe
                        if a_element:
                            # Récupérer le lien href
                            link = "https://www.nato.int/cps/fr/natohq/" + a_element.get("href")

                            '''
                            # Envoyer la requête en imitant un délai aléatoire entre 1 et 5 secondes
                            response2 = requests.get(link, headers=headers)
                            time.sleep(random.uniform(1, 5))
    
                            soup2 = BeautifulSoup(response2.content, "html.parser")
    
                            # Trouver l'élément h1 avec la classe "fs-huge"
                            h1_element = soup2.find("h1", class_="fs-huge")
                            title = h1_element.text.strip() if h1_element else "Titre non disponible"
    
                            # Trouver l'élément section avec la classe "cf"
                            section_elements = soup2.find_all("section", class_="content cf")
                            # Parcourir chaque élément section trouvé
                            content = ""
                            for section_element in section_elements:
                                p_elements = section_element.find_all("p")
                                # Parcourir chaque élément <p>
                                for p_element in p_elements:
                                    # Ajouter le texte de l'élément <p> au contenu
                                    content += p_element.text.strip() + "\n" '''

                            try:
                                # Insérer les données dans la base de données MySQL
                                sql = "INSERT INTO news (country, date, image, title, content, link) VALUES (%s, %s, %s, %s, %s, %s)"
                                val = (country, date, image, title, content, link)
                                mycursor.execute(sql, val)
                                mydb.commit()
                                print(f"Insertion : {compteur}")

                            except Exception as e:
                                print(e)

                                break

        else :
            break

# Fermer la connexion à la base de données MySQL
mydb.close()
