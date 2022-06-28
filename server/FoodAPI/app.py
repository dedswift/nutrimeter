from ast import Param
from heapq import merge
# from urllib import response
from flask import Flask, request, jsonify, make_response
import requests
import firebase_admin as firebase
from firebase_admin import credentials, firestore


# TODO
# finish get recipe
# add the diet plan nutritions to user document so we don't have to recompute each time
# test spoontacular API if the food the AI is trained on is there else create nutrition's 
# from scratch

app = Flask(__name__)


URL = "https://api.spoonacular.com/recipes/findByNutrients?"

API_KEY = "API_KEY_REQUIRED"

cred = credentials.Certificate("./server/FoodAPI/serviceAccountKey.json")
firebase.initialize_app(cred)

db = firestore.client()


# Used by the recipe portal to show recipes to the user
@app.route('/getRecipes', methods=['GET'])
def get_recipes_by_nutrition():
    """
    get recipes by nutritions also limiting
    nutritions
    """
    max_fat = 15 / 2
    max_calc = 600 / 2
    max_sod = 1000 / 2
    max_carbs = 250 / 2
    max_protein = 40 / 2
    max_iron = 17 / 2
    total_cal = 1600
    sugar = 0.45

    get_recipes_url = "https://api.spoonacular.com/recipes/findByNutrients?"

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
        "random": True,
        "apiKey": API_KEY
    }

    response = requests.get(url=get_recipes_url, params=params)
    print(type(response))
    return make_response(jsonify(response.json()))

    # return make_response(jsonify(doc.to_dict()))
    # return make_response(jsonify({doc.id: doc.to_dict()}))
    # Get USER ID from request URL
    # Use the USER ID to get the user data from firebase
    # Check if he's diabetic
    # check if he suffers from high cholesterol
    # check if he suffers from high blood pressure
    # check if he suffers from dyslipidemia

    # diabetic diet plan
    # max total fat = 15gm
    # max calcium = 600 mg
    # max sodium = 1000 mg
    # max carbohydrates = 250 gm
    # max protein = 40gm
    # max iron = 17 mg
    # total cal = 1600
    # LOOK FOR LOW SUGAR

    # high cholesterol diet plan
    # max total fat = 20gm
    # max calcium = 600 mg
    # max sodium = 1200 mg
    # max carbohydrates = 400 gm
    # max protein = 60gm
    # max iron = 17 mg
    # total cal = 2000
    # LOOK FOR LOW CHOLESTEROL

    # High blood pressure diet plan
    # max total fat = 15gm
    # max calcium = 500 mg
    # max sodium = 100 mg
    # max carbohydrates = 272 gm
    # max protein = 40gm
    # max iron = 17 mg
    # total cal = 1600

    # Use these value to search for recipes that match these parameters
    # Send 3 recipes after each refresh

    # response = requests.get(url=URL, params=PARAMS)


@app.route('/getRecentRecipes/<user_id>', methods=['GET'])
def recommended_recipes(user_id):
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
        print(u'No such user')

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
        "apiKey": API_KEY
    }

    response = requests.get(url=URL, params=params)
    print(response.json())

    return make_response(jsonify({response.json()}))

# This endpoint function is called if user adds the recipes calories or the food scanned calories
@app.route('/addCalories/<user_id>')
def add_calories(user_id):
    """
    Sending a request to this endpoint adds calories to current calories of the user
    and gives the user 100 xp
    """
    # use the user_id to grab the document reference
    doc_ref = db.collection('user').document(user_id)
    # get the last document snapshot
    old_doc_snap = doc_ref.get()
    doc = old_doc_snap.to_dict()
    print(doc)

    # Add XP
    if doc['currentXP'] == 1000:

        if doc['level'] == 100:
            doc_ref.update({
                'currentXP': 0
            })

        else:

            doc_ref.update({
                'level': doc['level'] + 1,
                'currentXP': 0
            })
    else:
        doc_ref.update({
            'currentXP': doc['currentXP'] + 100
        })

    # Add to current calories
    # doc_ref.update({
    #     'target': old_doc.to_dict()['target'] + 50
    # })
    # use the USER ID to get the user document from firestore
    # check level and check xp
    # if xp > 1500 add 1 to level
    # otherwise add 150 xp

    new_doc_snap = doc_ref.get()
    doc = new_doc_snap.to_dict()
    print(doc)
    return make_response(jsonify(doc))


# http://127.0.0.1:5000/search?query=apple
@app.route('/search')
def search_recipe():
    """
    Sending a query to this endpoint returns a list of 3 recipes
    matching the search term
    """
    # get the list of query paramters
    args = request.args
    args = args.to_dict()
    query = args.get('query') # get the paramter called 'query'

    url = "https://api.spoonacular.com/recipes/complexSearch?"

    params = {
        "query": query,
        "number": 3,
        "apiKey": API_KEY
    }

    response = requests.get(url=url, params=params)
    print(response.json())

    return make_response(jsonify(response.json()))


@app.route('/getRecipes/Ingredients/<recipe_id>')
def get_recipes_ingredients(recipe_id):
    """
    Sending a recipe id to this endpoint returns the ingredients, when parsing
    the response "name" or "nameClean" are used to get the ingredient name
    """
    
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?"

    params = {
        "includeNutrition": False,
        "apiKey": API_KEY
    }

    response = requests.get(url=url, params=params)
    response = response.json()['extendedIngredients']

    return make_response(jsonify(response))


if __name__ == '__main__':
    app.run(debug=True)
