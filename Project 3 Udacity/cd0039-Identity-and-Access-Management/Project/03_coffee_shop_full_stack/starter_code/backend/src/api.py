from black import err
from flask import Flask, request, jsonify, abort, request_started, session
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


#db_drop_and_create_all()

# ROUTES


# get drinks
@app.route("/drinks", methods=["GET"])
def get_drinks():
    """
    Request param: none

    Returns a list of drinks 
    """
    drinks = [drinks.short() for drinks in Drink.query.all()]
    return jsonify({"status": 200, "success": True, "drinks": drinks})


# get drink-details
@app.route("/drinks-detail", methods=["GET"])
@requires_auth("get:drinks-detail")
def drinks_detail():
    """
    Returns a list of drinks
    """
    try:
        drinks = [drink.long() for drink in Drink.query.all()]
        if drinks != []:
            return jsonify({"status code": 200, "success": True, "drinks": drinks})
    except AuthError as err:
        abort(401)

# post a new drink
@app.route("/drinks", methods=["POST"])
@requires_auth("post:drinks")
def post_drink():
    """
    post a new drink

    Body: { "title": "", "recipe": [{"color":"", "parts":""}]}

    """
    req = request.get_json()
    drink_title = req.get("title")
    new_recipe = req.get("recipe")
    drink_recipe = json.dumps(new_recipe)

    try:
        new_drink = Drink(title=drink_title, recipe=drink_recipe)
        new_drink.insert()
    except AuthError as error:
        abort(401)
    
    return jsonify({"success": True, "drinks": [new_drink.long()]})


@app.route("/drinks/<int:id>", methods=["PATCH"])
@requires_auth("patch:drinks")
def update_drink(id):
    """
    Update a drink item

    Body : {"title":""} or {"recipe": [{}]}
    """
    body = request.get_json()
    drink_title = body.get("title", None)
    drink_recipe = body.get("recipe", None)
    try:
        drink = Drink.query.filter(Drink.id == id).first()
        if drink is None:
            abort(404)

        if drink_title:
            drink.title = drink_title
            drink.update()

        if drink_recipe:
            drink.recipe = drink_recipe if type(drink_recipe) == str else json.dumps(drink_recipe)
            drink.update()

        return jsonify({"success": True, "drinks": [drink.long()]})

    except AuthError as auth_error:   
        abort(401)   
    except Exception as error:   
        abort(422)

# delete drink
@app.route("/drinks/<id>", methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drink(id):
    """
    Deletes a drink item


    """
    try:
        drink = Drink.query.filter(Drink.id == id).one_or_none()
        if drink is None:
            abort(404)
        drink.delete()
        return jsonify({"success": True, "deleted": id})

    except AuthError as auth_error:   
        abort(401)   
    except Exception as error:   
        abort(422)


# Error Handling
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


@app.errorhandler(404)
def not_found(error):
    """
    Handles error related to end-points that are defined
    """
    return jsonify({"success": False, "error": 404, "message": "resource not found"}), 404


@app.errorhandler(422)
def unprocessable(error):
    """
    Handles error related to unproccessable requests
    """
    return jsonify({"success": False, "error": 422, "message": "unprcoccesable entity"}), 422


@app.errorhandler(400)
def bad_request(error):
    """
    Handles error related to requests that doesn't meet specification
     """
    return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

@app.errorhandler(403)
def unauthorized_request(error):
    """
    Handles error related to requests that doesn't meet specification
     """
    return jsonify({"success": False, "error": 403, "message": "unauthorized"}), 403


