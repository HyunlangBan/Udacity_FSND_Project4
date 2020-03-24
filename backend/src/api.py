import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


# db_drop_and_create_all()

# ROUTES

@app.route('/drinks')
def get_drinks():
    drink_short_desc = []
    drinks = Drink.query.all()
    for drink in drinks:
        drink_short_desc.append(drink.short())
    return jsonify({
        "success": True,
        "drinks": drink_short_desc
    })


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    drink_desc = []
    drinks = Drink.query.all()

    for drink in drinks:
        drink_desc.append(drink.long())

    return jsonify({
        "success": True,
        "drinks": drink_desc
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_new_drink(jwt):
    body = request.get_json()
    new_title = body.get('title')
    new_recipe = body.get('recipe')
    drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
    drink.insert()

    drink_desc = []
    drinks = Drink.query.all()
    for drink in drinks:
        drink_desc.append(drink.long())

    return jsonify({
        "success": True,
        "drinks": drink_desc
    })


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drinks(jwt, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)

    body = request.get_json()

    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)

    if new_title is None:
        drink.recipe = json.dumps(new_recipe)
    elif new_recipe is None:
        drink.title = new_title
    else:
        drink.recipe = json.dumps(new_recipe)
        drink.title = new_title

    drink.update()

    drinks = Drink.query.all()

    drink_desc = []
    for drink in drinks:
        drink_desc.append(drink.long())

    return jsonify({
        "success": True,
        "drinks": drink_desc
    })


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    if drink is None:
        abort(404)
    drink.delete()

    return jsonify({
        "success": True,
        "delete": id
    })


# Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(AuthError)
def unprocessable(error):
    return jsonify(error.error), error.status_code
