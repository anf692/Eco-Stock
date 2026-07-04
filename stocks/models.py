from django.db import models


class Warehouse(models.Model):
    nom = models.CharField(max_length=100)
    localisation = models.CharField(max_length=100)
    capacite = models.IntegerField()

    def __str__(self):
        return self.nom


class Product(models.Model):
    ETAT_CHOICES = [
        ('disponible', 'Disponible'),
        ('reserve', 'Réservé'),
        ('perime', 'Périmé'),
    ]

    nom = models.CharField(max_length=100)
    quantite = models.PositiveIntegerField()
    date_expiration = models.DateField()
    etat = models.CharField(max_length=20, choices=ETAT_CHOICES, default='disponible')
    entrepot = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name='produits' #on ajoute related_name pour faciliter l'accès aux produits d'un entrepôt
    )

    def __str__(self):
        return self.nom
    
