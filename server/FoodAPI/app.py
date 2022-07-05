"""Entry point"""
# import argparse
from flask import Flask, request, jsonify, make_response
import requests
import firebase_admin as firebase
from firebase_admin import credentials, firestore



# Place this in the __main__ conditon when importing this as a module
cred = credentials.Certificate("./server/FoodAPI/serviceAccountKey.json")
firebase.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)
URL = "https://api.spoonacular.com/recipes/findByNutrients?"
SPOON_API_KEY = ""



@app.route('/getRecentRecipes/<user_id>', methods=['GET'])
def recommended_recipes(user_id):
    """Recommends recipes."""
    # DEFAULT NORMAL NUTRITION
    max_fat = 15 / 2
    max_calc = 600 / 2
    max_sod = 1000 / 2
    max_carbs = 250 / 2
    max_protein = 40 / 2
    max_iron = 17 / 2
    total_cal = 1600
    sugar = 0.3

    doc = db.collection('user').document(user_id).get()

    if doc.exists:
        print(f'Document data: {doc.to_dict()}')
    else:
        print('No such user')

    user_health = doc.to_dict()['healthConditions']

    # DIET PLAN NUTRITION
    if user_health['diabetes'] or user_health['hBloodPressure'] \
            or user_health['hCholesterol'] or user_health['dyslipidemia']:
        max_fat = 15 / 2  # gm
        max_calc = 600 / 2  # mg
        max_sod = 1000 / 2  # mg
        max_carbs = 250 / 2  # gm
        max_protein = 40 / 2  # gm
        max_iron = 17 / 2  # mg
        total_cal = 1600
        sugar = 0.5

    params = {
        "maxCarbs": max_carbs,  # in gram
        "maxFat": max_fat,  # in gram
        "maxCalcium": max_calc,  # in gram
        "maxSodium": max_sod,  # in gram
        "maxProtein": max_protein,  # in gram
        "maxIron": max_iron,  # in gram
        "maxCalories": total_cal,  # in gram
        "maxSugar": sugar,  # in gram
        "number": 3,
        "apiKey": SPOON_API_KEY
    }

    response = requests.get(url=URL, params=params)
    print(response.json())

    return make_response(jsonify({response.json()}))








###################### RECIPE ####################
@app.route('/search')
def search_recipe():
    """Performs the search function in the recipe page.

    Sending a query to this endpoint returns a list of 3 recipes matching the search term.

        Request example:
        http://127.0.0.1:5000/search?query=apple

        Response example:
    """
    # get the list of query paramters from the request
    args = request.args
    args = args.to_dict()
    query = args.get('query') # get the paramter called 'query'

    url = "https://api.spoonacular.com/recipes/complexSearch?"

    params = {
        "query": query,
        "number": 3,
        "apiKey": SPOON_API_KEY
    }

    response = requests.get(url=url, params=params)
    print(response.json())
    return make_response(jsonify(response.json()))


@app.route('/getRecipes')
def get_recipes_by_nutrition():
    """Get recipes.

    Used to populate the recipes page.
    Request example:
        http://127.0.0.1:5000/getRecipes
    """

    url = "https://api.spoonacular.com/recipes/findByNutrients?"

    params = {
        "maxCarbs": 250,  # in gram
        "maxFat": 5,  # in gram
        "maxCalcium": 24,  # in gram
        "maxSodium": 10,  # in gram
        "maxProtein": 25,  # in gram
        "maxIron": 17,  # in gram
        "maxCalories": 1500,  # in gram
        "maxSugar": 0.45,  # in gram
        "number": 3,
        "random": True,
        "apiKey": SPOON_API_KEY
    }

    response = requests.get(url=url, params=params)
    return make_response(jsonify(response.json()))




@app.route('/getRecipes/ingredients')
def get_recipes_ingredients():
    """Get recipe ingredients.

    Sending a recipe id to this endpoint returns the ingredients, when parsing
    the response "name" or "nameClean" are used to get the ingredient name.

    Request example:
        http://127.0.0.1:5000/getRecipes/ingredients?recipe-id=632485
    """

    # get the list of query paramters
    args = request.args
    args = args.to_dict()
    recipe_id = args.get('recipeID') # get the paramter called 'recipe-id'
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?"


    params = {
        "includeNutrition": False,
        "apiKey": SPOON_API_KEY
    }

    response = requests.get(url=url, params=params)
    response = response.json()['extendedIngredients']

    return make_response(jsonify(response))


@app.route('/addFavorite/<user_id>/<recipe_id>')
def add_favorite(user_id, recipe_id):
    # use the user_id to grab the document reference
    doc_ref = db.collection('user').document(user_id)
    # get the last document snapshot
    old_doc_snap = doc_ref.get()
    doc = old_doc_snap.to_dict()
    print(doc['favorites'])
    favorites = set(doc['favorites'])
    favorites.add(recipe_id)
    print(favorites)
    doc_ref.set({
        'favorites': favorites
    }, merge=True)
    new_doc_snap = doc_ref.get()
    print(new_doc_snap.to_dict())
    return make_response(jsonify({"message": "OK"}))

    

@app.route('/removeFavorite/<user_id>/<recipe_id>')
def remove_favorite(user_id, recipe_id):
    # use the user_id to grab the document reference
    doc_ref = db.collection('user').document(user_id)
    # get the last document snapshot
    old_doc_snap = doc_ref.get()
    doc = old_doc_snap.to_dict()
    print(doc['favorites'])
    favorites = set(doc['favorites'])
    favorites.add(recipe_id) # Temporary to remove the execption that is thrown
    favorites.remove(recipe_id)
    print(favorites)
    doc_ref.set({
        'favorites': favorites
    }, merge=True)
    new_doc_snap = doc_ref.get()
    print(new_doc_snap.to_dict())
    return make_response(jsonify({"message": "OK"}))


@app.route('/show-favorite')
def show_favorite():
    pass
###################### RECIPE ####################


###################### CAMERA ####################
@app.route('/detectFood')
def detect_food():
    """Detects the food in the picture and their nutritional values."""

    # Mask R-CNN microservice URL
    url = "http://192.168.1.205:5000/pred-img"

    # Sending a POST request to mask R-CNN API and forwarding the image from the client
    response = requests.post(url=url, files={'image': request.files['image']})

    # The response contains the labels of the predicted food
    ingredients = response.json()

    # Dictionary of food nutritions will be converted to json
    nutritions = {}
    for ingredient in ingredients['ingredients']:
        # Get request to get the food ID
        get_ingredient = "https://api.spoonacular.com/food/ingredients/search?"
        params = {
            "query": ingredient,
            "apiKey": SPOON_API_KEY,
            "number": 1
        }
        response = requests.get(url=get_ingredient, params=params)
        ingredient_id = response.json()['results'][0]['id']
        # Get request to get the food nutrition using the food ID
        get_nutritions = \
            f"https://api.spoonacular.com/food/ingredients/{ingredient_id}/information?"
        params = {
            "apiKey": SPOON_API_KEY,
            "amount": 1
        }
        response = requests.get(url=get_nutritions, params=params)
        # From the response we only care about the nutritons of the item
        response = response.json()['nutrition']['nutrients']
        nutritions[ingredient] = response

    return make_response(jsonify(nutritions))



@app.route('/<user_id>/isFoodHealthy')
def is_food_healthy(user_id):
    """Checks food for cholesterol and sugar amount to see if it's healthy.

    Request example:
        http://127.0.0.1:5000/isFoodHealthy?sugar=20&cholesterol=20
    """
    args = request.args
    args = args.to_dict()
    sugar = float(args.get('sugar')) # get the paramter called 'sugar'
    cholesterol = float(args.get('cholesterol')) # get the paramter called 'cholesterol'

    doc = db.collection('user').document(user_id).get().to_dict()

    if doc['healthConditions']['diabetes']:
        if sugar > 20: # greater than 20 mg
            # Warn client that food isn't healthy
            return make_response(jsonify({'isFoodHealthy': False}))

    if doc['healthConditions']['hCholesterol']:
        if cholesterol > 20: # greater than 20 mg
            # Warn client that food isn't healthy
            return make_response(jsonify({'isFoodHealthy': False}))

    return make_response(jsonify({'isFoodHealthy': True}))



# This endpoint function is called if user adds the recipes calories or the food scanned calories
@app.route('/addCalories/<user_id>')
def add_calories(user_id):
    """
    Sending a request to this endpoint adds calories to current calories of the user
    and gives the user 100 xp

    Request example:
        http://127.0.0.1:5000/addCalories/123?cal=20
    """

    args = request.args
    args = args.to_dict()
    cal = float(args.get('cal')) # get the paramter called 'cal'

    # use the user_id to grab the document reference
    doc_ref = db.collection('user').document(user_id)
    # get the last document snapshot
    old_doc_snap = doc_ref.get()
    doc = old_doc_snap.to_dict()
    # print(doc)

    # Add XP
    if doc['currentXP'] == 1000:

        if doc['level'] == 100:
            doc_ref.update({
                'currentCal': doc['currentCal'] + cal,
                'currentXP': 0
            })

        else:

            doc_ref.update({
                'currentCal': doc['currentCal'] + cal,
                'level': doc['level'] + 1,
                'currentXP': 0
            })
    else:
        doc_ref.update({
            'currentCal': doc['currentCal'] + cal,
            'currentXP': doc['currentXP'] + 100
        })

    # Print the user Doc and return it
    # new_doc_snap = doc_ref.get()
    # doc = new_doc_snap.to_dict()
    # print(doc)
    # return make_response(jsonify(doc))
    return make_response(jsonify({'Success': True}))


###################### CAMERA ####################



# Firebase will raise an error if intialize app is used more than one
# using this condition so that when recipe import this module it doesn't
# execute intitializa app twice
if __name__ == '__main__':
    # app.py as script
    app.run(debug=True)
