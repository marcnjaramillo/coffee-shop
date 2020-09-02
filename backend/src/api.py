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


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

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


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks():
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
def create_drink():
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
def update_drink(id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()

    if not drink:
        abort(404)

    try:
        body = request.get_json()
        drink.title = body.get('title', drink.title)
        drink.recipe = json.dumps(body.get('recipe'))
        drink.update()

        return jsonify({
            'success': True,
            'drinks': drink.long()
        })
    except Exception as e:
        print(e)
        abort(422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
    }), 422


@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Resource not found"
    }), 404
