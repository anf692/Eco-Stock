# 🥫 Eco-Stock API

API REST pour la gestion de stocks alimentaires permet de centraliser les surplus des commerces locaux et de les redistribuer avant péremption via un réseau d'entrepôts (redistributeurs).

## Sommaire

- [Contexte](#contexte)
- [Stack technique](#stack-technique)
- [Installation](#installation)
- [Modélisation](#modélisation)
- [Authentification](#authentification)
- [Endpoints API](#endpoints-api)
- [Flux métier : Transfert de produit](#flux-métier--transfert-de-produit)
- [Codes de statut HTTP](#codes-de-statut-http)

---

## Contexte

Eco-Stock digitalise la gestion de son inventaire et de ses flux de marchandises en temps réel entre plusieurs entrepôts de redistribution.

## Stack technique

- **Backend** : Django REST Framework
- **Authentification** : JWT (`djangorestframework-simplejwt`)
- **Documentation API** : OpenAPI / Swagger (`drf-spectacular`)
- **Base de données** : SQLite (dev) / PostgreSQL (prod recommandé)

## Installation

```bash
# 1. Cloner le dépôt
git clone <url-du-repo>
cd eco-stock

# 2. Créer et activer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows : venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Appliquer les migrations
python manage.py makemigrations
python manage.py migrate

# 5. Créer un superutilisateur (pour tester l'authentification)
python manage.py createsuperuser

# 6. Lancer le serveur
python manage.py runserver
```

L'API est accessible sur `http://127.0.0.1:8000/api/`

---

## Modélisation

### Warehouse (Entrepôt)

| Champ | Type | Description |
|---|---|---|
| `id` | Integer | Identifiant unique (auto) |
| `nom` | CharField | Nom de l'entrepôt |
| `localisation` | CharField | Localisation géographique |
| `capacite` | Integer | Capacité maximale de stockage |

### Product (Produit)

| Champ | Type | Description |
|---|---|---|
| `id` | Integer | Identifiant unique (auto) |
| `nom` | CharField | Nom du produit |
| `quantite` | PositiveIntegerField | Quantité en stock (jamais négative) |
| `date_expiration` | DateField | Date de péremption |
| `etat` | CharField (choices) | `disponible` / `reserve` / `perime` |
| `entrepot` | ForeignKey → Warehouse | Entrepôt de rattachement (`on_delete=PROTECT`) |

**Relation** : Un `Warehouse` peut contenir plusieurs `Product` (1-N). La suppression d'un entrepôt est **bloquée** (`PROTECT`) tant qu'il contient des produits, afin d'éviter toute perte accidentelle de denrées en cours de redistribution.

---

## Documentation interactive (Swagger)

En complément de ce README, l'API expose une documentation **OpenAPI générée automatiquement** via `drf-spectacular`, toujours synchronisée avec le code réel.

| Endpoint | Description |
|---|---|
| `/api/schema/` | Schéma OpenAPI brut (JSON) |
| `/api/docs/` | Interface Swagger UI — visualisation et test interactif des endpoints |

Une fois le serveur lancé, ouvrir [`http://127.0.0.1:8000/api/docs/`](http://127.0.0.1:8000/api/docs/) pour explorer et tester chaque endpoint directement dans le navigateur (bouton **"Try it out"**), y compris les routes protégées par JWT (bouton **"Authorize"** en haut de la page pour renseigner le token `Bearer`).

### Configuration (déjà en place dans ce projet)

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'drf_spectacular',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'ecoStock API',
    'DESCRIPTION': 'API pour la gestion des entrepôts et des produits',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
```

```python
# urls.py
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # ...
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
```

---

## Authentification

L'API utilise **JWT** (JSON Web Token) via `simple-jwt`.

- **Lecture (`GET`)** : accessible sans authentification
- **Écriture (`POST`, `PUT`, `PATCH`, `DELETE`)** : réservée aux utilisateurs authentifiés (`IsAuthenticatedOrReadOnly`)

### Obtenir un token

```
POST /api/token/
```

**Body :**
```json
{
    "username": "votre_username",
    "password": "votre_password"
}
```

**Réponse `200 OK` :**
```json
{
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Rafraîchir un token expiré

```
POST /api/token/refresh/
```

**Body :**
```json
{
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Utiliser le token

Ajouter l'en-tête suivant à chaque requête protégée :

```
Authorization: Bearer <votre_access_token>
```

---

## Endpoints API

### Warehouses (Entrepôts)

| Méthode | Endpoint | Description | Auth requise |
|---|---|---|---|
| `GET` | `/api/warehouses/` | Liste tous les entrepôts | Non |
| `POST` | `/api/warehouses/` | Crée un entrepôt | Oui |
| `GET` | `/api/warehouses/{id}/` | Détail d'un entrepôt | Non |
| `PUT`/`PATCH` | `/api/warehouses/{id}/` | Modifie un entrepôt | Oui |
| `DELETE` | `/api/warehouses/{id}/` | Supprime un entrepôt (bloqué si produits liés) | Oui |
| `GET` | `/api/warehouses/{id}/audit/` | Audit du stock de l'entrepôt | Non |

#### `GET /api/warehouses/{id}/audit/`

Retourne le nombre total de produits d'un entrepôt, réparti par état.

**Réponse `200 OK` :**
```json
{
    "entrepot": "Entrepôt Dakar Nord",
    "total_produits": 50,
    "disponible": 30,
    "reserve": 15,
    "perime": 5
}
```

---

### Products (Produits)

| Méthode | Endpoint | Description | Auth requise |
|---|---|---|---|
| `GET` | `/api/products/` | Liste tous les produits | Non |
| `POST` | `/api/products/` | Crée un produit | Oui |
| `GET` | `/api/products/{id}/` | Détail d'un produit | Non |
| `PUT`/`PATCH` | `/api/products/{id}/` | Modifie un produit | Oui |
| `DELETE` | `/api/products/{id}/` | Supprime un produit | Oui |
| `POST` | `/api/products/{id}/move/` | Transfère un produit vers un autre entrepôt | Oui |

#### Exemple — Créer un produit

```
POST /api/products/
Authorization: Bearer <token>
```

**Body :**
```json
{
    "nom": "Riz 25kg",
    "quantite": 10,
    "date_expiration": "2026-12-31",
    "etat": "disponible",
    "entrepot": 1
}
```

**Réponse `201 Created` :**
```json
{
    "id": 4,
    "nom": "Riz 25kg",
    "quantite": 10,
    "date_expiration": "2026-12-31",
    "etat": "disponible",
    "entrepot": 1,
    "entrepot_nom": "Entrepôt Dakar Nord"
}
```

#### `POST /api/products/{id}/move/`

Transfère un produit vers un nouvel entrepôt. **Refusé si le produit est périmé.**

**Body :**
```json
{
    "new_warehouse_id": 2
}
```

**Réponse `200 OK` :**
```json
{
    "status": "Produit déplacé avec succès."
}
```

**Réponse `400 Bad Request`** (produit périmé) :
```json
{
    "error": "Impossible de déplacer un produit périmé."
}
```

**Réponse `404 Not Found`** (entrepôt cible inexistant) :
```json
{
    "error": "Entrepôt non trouvé."
}
```

---

## Flux métier : Transfert de produit

```
┌─────────────────────────────────────────────────────────────┐
│  POST /api/products/{id}/move/                               │
│  Body : { "new_warehouse_id": X }                             │
└────────────────────────┬────────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ Utilisateur authentifié ?│
              └───────────┬───────────┘
                    Non   │   Oui
              ┌───────────┴───────────┐
              ▼                       ▼
      401 Unauthorized      Récupération du produit
                             (self.get_object())
                                      │
                                      ▼
                          ┌───────────────────────┐
                          │ Produit.etat == 'perime' ?│
                          └───────────┬───────────┘
                              Oui     │     Non
                    ┌───────────────┐ │
                    ▼               │ ▼
          400 Bad Request           │  Recherche du nouvel entrepôt
    "Impossible de déplacer         │  (Warehouse.objects.get(id=X))
     un produit périmé."            │        │
                                     │        ▼
                                     │  ┌─────────────────────┐
                                     │  │ Entrepôt trouvé ?    │
                                     │  └──────────┬──────────┘
                                     │       Non   │   Oui
                                     │  ┌──────────┴──────────┐
                                     │  ▼                     ▼
                                     │ 404 Not Found    Mise à jour :
                                     │ "Entrepôt non    product.entrepot = new_warehouse
                                     │  trouvé."        product.save()
                                     │                        │
                                     │                        ▼
                                     │              200 OK
                                     │        "Produit déplacé
                                     │         avec succès."
                                     └────────────────────────┘
```

---

## Codes de statut HTTP

| Code | Signification | Cas d'usage dans l'API |
|---|---|---|
| `200 OK` | Succès | Lecture, mise à jour, transfert réussi |
| `201 Created` | Ressource créée | Création d'un produit/entrepôt |
| `400 Bad Request` | Violation de règle métier | Transfert d'un produit périmé |
| `401 Unauthorized` | Authentification manquante/invalide | Requête d'écriture sans token JWT |
| `403 Forbidden` | Authentifié mais non autorisé | Droits insuffisants |
| `404 Not Found` | Ressource inexistante | Produit ou entrepôt introuvable |

---

## Auteur

Projet réalisé dans le cadre de la formation **Développeur Web / Web Mobile + IA** — Simplon Senegal.