from django.db import models

class CountryManager(models.Manager):
    pass

class Country(models.Model):
    name_country = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50)

    objects = CountryManager()  # Ajout de l'attribut objects

    def __str__(self):
        return self.name_country
