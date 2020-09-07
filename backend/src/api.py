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


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

# ROUTES


@app.route('/drinks', methods=['GET'])
def get_drinks():
    all_drinks = Drink.query.all()
    drinks = [drink.short() for drink in all_drinks]

    if len(drinks) == 0:
        abort(404)

    return jsonify({
        'success': True,
        'drinks': drinks
    })


@app.route('/drink-details', methods=['GET'])
@requires_auth('get:drink-details')
def get_drinks_detail(token):
    all_drinks = Drink.query.all()
    drinks = [drink.long() for drink in all_drinks]

    if len(drinks) == 0:
        abort(404)

    return jsonify({
        'success': True,
        'drinks': drinks
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(token):
    body = request.get_json()
    title = body.get('title')
    recipe = body.get('recipe')
    try:
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': drink.long()
        })

    except Exception as e:
        print(e)
        abort(422)


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if drink is None:
        abort(404)

    try:
        body = request.get_json()
        drink.title = json.dumps(body.get('title', drink.title))
        drink.recipe = json.dumps(body.get('recipe'))
        drink.update()

        updated_drink = Drink.query.filter_by(id=id).first()

        return jsonify({
            'success': True,
            'drinks': [updated_drink.long()]
        })
    except Exception as e:
        print(e)
        abort(422)


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(token, id):
    try:
        drink = Drink.query.filter(
            Drink.id == id).one_or_none()

        if drink is None:
            abort(404)

        drink.delete()

        return jsonify({
            'success': True,
            'delete': id
        })

    except Exception as e:
        print(e)
        abort(422)

# Error Handling


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource not found"
    }), 404
