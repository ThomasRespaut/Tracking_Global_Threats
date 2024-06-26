import json
import os
from googletrans import Translator
from langdetect import detect
from PIL import Image
from io import BytesIO
import requests
from sentence_transformers import SentenceTransformer, util
import openai

key = ""

def get_resume(question, information, language):
    message = [
        {
            "role": "system",
            "content": f"You are an intelligent virtual assistant designed to present articles with great precision and a lot of sentence. You will need to respond in {language}. The user provides you with a question on a specific topic and information from articles. You should use this data to formulate an informative and coherent answer. Remember to add sources (in different languages), publication dates of the articles and relevant details to make the answer as complete as possible."
        },
        {
            "role": "user",
            "content": f"Question : {question}, Information : {information}"
        }
    ]
    openai.api_key = key
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=message
        )
        response = response['choices'][0]['message']['content']
    except Exception as e:
        response = f"Une erreur s'est produite : {e}"
    finally:
        return response

def give_title(resume, language):
    message = [
        {
            "role": "system",
            "content": f"You are an intelligent virtual assistant. Your job is to create catchy article titles (breaking news). Answer in {language}. The user shares his article summary. Use it to create a clear and catchy title. Enter only the title without any other text."
        },
        {
            "role": "user",
            "content": f"Resume Content: {resume}"
        }
    ]
    openai.api_key = key
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=message
        )
        response = response['choices'][0]['message']['content']
    except Exception as e:
        response = f"An error occurred: {e}"
    finally:
        return response

def word_embedding(articles, user_sentence):
    print(f"Nombre d'articles : {len(articles)}")

    model = SentenceTransformer("distiluse-base-multilingual-cased-v2")
    print(f"User sentence : {user_sentence}")
    emb1 = model.encode(user_sentence)

    articles_list = []

    for article in articles:
        title = article[2]
        description = article[3]
        content = article[7]
        publishedAt = article[6]
        source = article[0]
        if title:
            emb2 = model.encode(title)
            similarite_entre_1_et_2 = float(util.cos_sim(emb1, emb2))
            articles_list.append([title, description, content, publishedAt, source, similarite_entre_1_et_2])

    # Trier les articles par rapport à la similitude (élément à l'indice 5)
    articles_list.sort(key=lambda x: x[5], reverse=True)

    return articles_list[:20]

def translate_articles(articles, lg):
    translated_articles = []
    for article in articles:
        title = article[2]
        description = article[3]
        content = article[7]

        try:
            language = detect(title)
        except Exception as e:
            print("Erreur lors de la détection de la langue:", e)
            continue  # Passe à l'article suivant si la détection de la langue échoue

        if language != lg:
            try:
                translator = Translator()
                translated_title = translator.translate(title, dest=lg).text
                translated_description = translator.translate(description, dest=lg).text
                translated_content = translator.translate(content, dest=lg).text
                translated_article = [article[0], article[1], translated_title, translated_description, article[4],
                                      article[5], article[6], translated_content]
                translated_articles.append(translated_article)
            except Exception as e:
                print("Une erreur s'est produite lors de la traduction:", e)
        else:
            translated_articles.append(article)

    return translated_articles

