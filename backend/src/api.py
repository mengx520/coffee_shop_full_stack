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
'''
implement endpoint GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['GET'], endpoint='get_drinks')
def public_get_drinks():
    try:
        drinks = Drink.query.all()
        return jsonify({
            'success': True,
            'drinks': [drink.short() for drink in drinks]
        }), 200
    except:
        raise
        return jsonify({
            'success': False,
            'messages': 'An error occured'}), 500


'''
@mplement endpoint GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=['GET'], endpoint='drinks_detail')
# add permission
@requires_auth('get:drinks-detail')
def get_drink_detail(f):
    try:
        drinks = Drink.query.all()
        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in drinks]
        }), 200
    except:
        return jsonify({
            'success': False,
            'message': 'An error occured'}), 500


'''
@implement endpoint POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=['POST'], endpoint='post_drink')
# add permission
@requires_auth('post:drinks')
def post_drinks(f):
    data = request.get_json()
    try:
        drink = Drink(
            title=data['title'],
            recipe=json.dumps([data['recipe']])
        )
        drink.insert()
        return jsonify({
            'success': True,
            'drinks': drink.long()
        }), 200
    except:
        return jsonify({
            'success': False,
            'message': 'An error occured'
        }), 500


'''
@implement endpoint PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['PATCH'], endpoint='patch_drink')
# add permission
@requires_auth('patch:drinks')
def edit_drinks(payload, id):
    data = request.get_json()
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    # it should respond with a 404 error if <id> is not found
    if not drink:
        abort(404)
    try:
        drink.title = data['title']
        drink.recipe = json.dumps([data['recipe']])

        drink.update()

        return jsonify({
            'success': True,
            'drinks': drink.long()
        }), 200
    except:
        return jsonify({
            'success': False,
            'message': 'An error occured'
        }), 500


'''
@implement endpoint DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<id>', methods=['DELETE'], endpoint='delete_drink')
# add permission
@requires_auth('delete:drinks')
def edit_drinks(payload, id):
    data = request.get_json()
    drink = Drink.query.filter(Drink.id == id).one_or_none()
    # it should respond with a 404 error if <id> is not found
    if not drink:
        abort(404)
    try:
        drink.delete()

        return jsonify({
            'success': True,
            'drinks': drink.id
        }), 200
    except:
        return jsonify({
            'success': False,
            'message': 'An error occured'
        }), 500


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
implement error handlers using the @app.errorhandler(error) decorator
'''


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": 'Bad Request'
    }), 400


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'Unathorized'
    }), 401


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": 'Internal Server Error'
    }), 500


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": "authorization error"
    }), error.status_code
