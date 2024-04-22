from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render
from .news_api import get_articles
from .word_embedding import get_resume,word_embedding, give_title, translate_articles
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.views.generic import TemplateView
from django.conf import settings
import mysql.connector
import os
import folium
import json
from django.shortcuts import render, redirect

def get_threats(country):
    title, resume = "", ""

    # Se connecter à la base de données MySQL
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="nato"
    )

    # Créer un curseur pour exécuter les requêtes SQL
    mycursor = mydb.cursor()

    try:
        # Exécuter la requête SQL pour récupérer les données de la base de données MySQL
        sql = "SELECT title, resume FROM map WHERE country = %s"
        val = (country,)
        mycursor.execute(sql, val)

        # Lire tous les résultats de la requête
        result = mycursor.fetchall()

        # Si des résultats sont disponibles, les assigner à title et resume
        if result:
            title, resume = result[0]

    except Exception as e:
        print(e)

    finally:
        # Fermer le curseur et la connexion à la base de données
        mycursor.close()
        mydb.close()

    return title, resume

class Index(TemplateView):
    template_name = 'index.html'

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        nato_countries = [
            "Albania", "Germany", "Belgium", "Bulgaria", "Canada", "Croatia",
            "Denmark", "Spain", "Estonia", "United States", "Finland", "France",
            "Greece", "Hungary", "Iceland", "Italy", "Latvia", "Lithuania",
            "Luxembourg", "North Macedonia", "Montenegro", "Norway", "Netherlands",
            "Poland", "Portugal", "Romania", "United Kingdom", "Slovakia",
            "Slovenia", "Sweden", "Czech Republic", "Turkey"
        ]

        # Define the path to the directory containing GeoJSON files
        geojson_dir = os.path.join(settings.STATICFILES_DIRS[0], 'geojson')

        # Create a Folium map centered at a specific location
        USGS_USImageryTopo = folium.TileLayer(
            tiles='https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryTopo/MapServer/tile/{z}/{y}/{x}',
            max_zoom=20,
            attr='Tiles courtesy of the <a href="https://usgs.gov/">U.S. Geological Survey</a>'
        )

        # Define the initial coordinates and zoom level
        lat = 0
        lon = 0
        zoom_start = 3

        # Create the map with the USGS tile layer
        m = folium.Map(location=[lat, lon], tiles=USGS_USImageryTopo, zoom_start=zoom_start)

        # Iterate over GeoJSON files in the directory and add each to the map
        for filename in os.listdir(geojson_dir):
            if filename.endswith('.geojson'):
                geojson_file = os.path.join(geojson_dir, filename)
                # Load GeoJSON data
                with open(geojson_file, 'r') as f:
                    geojson_data = json.load(f)

                # Iterate over GeoJSON features and add marker for each country
                for feature in geojson_data['features']:
                    # Extract country name and centroid coordinates
                    country_name = feature['properties']['ADMIN']

                    if country_name in nato_countries:
                        fill_color = '#ADD8E6'  # Utilisation d'un bleu clair
                    else:
                        fill_color = 'green'

                    # HTML content for the popup
                    title, resume = get_threats(country_name)
                    html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <style>
                            /* Style pour augmenter la taille de la popup */
                            .leaflet-pane {{
                                width: 25vw;  /* Largeur de la popup */ 
                            }}
                        </style>
                    </head>
                    <body>
                        <h2>{title}</h2>
                        <h4>{resume}</h4>
                    </body>
                    </html>
                    """

                    # Add GeoJSON layer with feature-specific popup
                    folium.GeoJson(
                        feature,
                        style_function=lambda x, fill_color=fill_color: {
                            'fillColor': fill_color,
                            'color': 'black',
                            'weight': 2,
                            'dashArray': '5, 5',
                            'fillOpacity': 0.5,
                        },
                        popup=folium.Popup(html, max_width='100%'),  # Popup with HTML content
                    ).add_to(m)

        # Convert the map to HTML
        map_html = m._repr_html_()

        context['map_html'] = map_html
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if 'search' in request.POST:
            query = request.POST.get('search_query', '')
            self.request.session['search_query'] = query
            context["search_query"] = query

            articles = get_articles(query)
            self.request.session['articles'] = articles
            context['articles'] = self.request.session['articles']

            # Rediriger vers la vue 'Country'
            return redirect('country')

        return render(request, self.template_name, context)


class Country(TemplateView):
    template_name = "country.html"

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'articles' in self.request.session:
            context['articles'] = self.request.session['articles']

        if 'search_query' in self.request.session:
            context["search_query"] = self.request.session['search_query']

        if 'start' and 'end' in self.request.session:
            context["start"] = self.request.session['start']
            context["end"] = self.request.session['end']


        # Obtiens la date actuelle
        current_date = datetime.now().date()
        # Calcul de la date il y a un mois
        one_month_ago = current_date - relativedelta(months=1)
        context["max"] = current_date.strftime("%Y-%m-%d")
        context["min"] = one_month_ago.strftime("%Y-%m-%d")

        if 'sort_by' in self.request.session:
            context["sort_by"] = self.request.session['sort_by']


        return context
    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        if 'search' in request.POST:
            query = request.POST.get('query','')
            self.request.session['search_query'] = query
            context["search_query"] = query

            start = request.POST.get('start','')
            self.request.session['start'] = start
            context["start"] = start

            end = request.POST.get('end','')
            self.request.session['end'] = end
            context["end"] = end

            sort_by = request.POST.get('sort_by','')
            self.request.session['sort_by'] = sort_by
            context["sort_by"] = sort_by

            articles = get_articles(query,start,end,sort_by)
            self.request.session['articles'] = articles
            context['articles'] = self.request.session['articles']

        if 'resume' in request.POST:
            data = request.session.get('articles')
            user_sentence = request.POST.get('user_sentence', '')
            language = request.POST.get('language', '')
            data = word_embedding(data, user_sentence)
            #print(data,"\n")
            resume = get_resume(user_sentence, data, language)
            title = give_title(resume, language)
            print(title)

            #print(resume)
            context['resume'] = resume
            request.session['resume'] = resume

            context['title'] = title
            request.session['title'] = title

        if 'translate' in request.POST:
            if 'articles' in self.request.session:
                articles = self.request.session['articles']
                language = request.POST.get('language_translate','english')

                context["language_translate"] = language
                request.session['language_translate'] = language

                #print(articles)
                articles = translate_articles(articles, language)
                context['articles'] = articles
                request.session['articles'] = articles

        return render(request, self.template_name, context)
