import requests
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta

#api_key = "a82a86471a4b470ebc6a30d9093c526e"
#api_key = "ee1133eafc0d44a285a99145891e4256"
api_key = '13ec9f4822ec4f2c949924d0fc2b3af0'

def get_content(search,date_start,date_end,api_key):
    api_url = f"https://newsapi.org/v2/everything?qInTitle={search}&from={date_start}&to={date_end}&sortBy=popularity&apiKey={api_key}"
    #api_url = f"https://newsapi.org/v2/everything?q={search}&from={date_start}&to={date_end}&language=fr&sortBy=popularity&apiKey={api_key}"
    #api_url = f"https://newsapi.org/v2/top-headlines?q={search}&from={date_start}&to={date_end}&sortBy=popularity&apiKey={api_key}"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        content = response.json()
        return content
    except requests.exceptions.RequestException as e:
        print("Une erreur s'est produite lors de la requête :", e)
        return None

def get_all_content(search, date_start, date_end, sort_by, api_key):
    all_articles = []
    page = 1
    while True:
        api_url = f"https://newsapi.org/v2/everything?q={search}&from={date_start}&to={date_end}&sortBy={sort_by}&page={page}&apiKey={api_key}"
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            content = response.json()
            if content.get('status') == 'error' and content.get('code') == 'maximumResultsReached':
                print("Vous avez atteint le nombre maximum de résultats.")
                break
            elif not content.get('articles'):
                break  # Pas d'articles supplémentaires
            all_articles.extend(content['articles'])
            page += 1
        except requests.exceptions.RequestException as e:
            print("Une erreur s'est produite lors de la requête :", e)
            return all_articles
    return all_articles

def download_json(json_data, file_path):
    try:
        # Séparer chaque article sur une nouvelle ligne
        articles = json_data["articles"]
        totalResults = json_data["totalResults"]
        formatted_articles = [json.dumps(article, ensure_ascii=False) for article in articles]

        # Enregistrer les articles dans un nouveau fichier JSON avec chaque article sur une nouvelle ligne
        with open(file_path, 'w', encoding='utf-8') as f:  # Assurez-vous d'utiliser l'encodage utf-8
            f.write("{\"articles\": [\n")
            f.write(",\n".join(formatted_articles))
            f.write("]}")

        print(f"{totalResults} articles saved successfully: {file_path}")
        return True
    except Exception as e:
        print("An error occurred while saving the JSON file:", e)
        return False

def dowload_all_json(content,search,one_month_ago,current_date):
    if content:
        articles = {"articles": content}
        file_path = f"json/{search}_{one_month_ago}_{current_date}.json"

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=4,
                          ensure_ascii=False)  # Utilise json.dump pour écrire la chaîne JSON dans le fichier
            print(f"Le fichier JSON a été enregistré avec succès : {file_path}")
        except Exception as e:
            print("Une erreur s'est produite lors de l'enregistrement du fichier JSON :", e)
    else:
        print("Aucun contenu à enregistrer.")

def get_articles(search,current_date="",one_month_ago="",sort_by="Relevancy"):
    article_list = []
    # Get the current date

    if current_date== "":
        current_date = datetime.now().date()

        one_month_ago = current_date - relativedelta(months=1)
        current_date = current_date.strftime("%d_%m_%Y")
        one_month_ago = one_month_ago.strftime("%d_%m_%Y")

    content = get_all_content(search, one_month_ago, current_date, sort_by, api_key)

    for article in content:
        source = article["source"] if "source" in article else None
        article_source = source["name"] if "name" in source else None

        article_author = article["author"] if "author" in article else None
        article_title = article["title"] if "title" in article else None
        article_description = article["description"] if "description" in article else None
        article_url = article["url"] if "url" in article else None
        article_urlToImage = article["urlToImage"] if "urlToImage" in article else None
        article_date = article["publishedAt"] if "publishedAt" in article else None
        article_content = article["content"] if "content" in article else None

        if article_title !="[Removed]":
            article_list.append((article_source,article_author,article_title, article_description,article_url,article_urlToImage,article_date,article_content))


    # dowload_all_json(content,search,one_month_ago,current_date)

    return article_list



