import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db, db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
db_drop_and_create_all(app)

# ROUTES


@app.route('/drinks', methods=['GET'])
def get_drinks():
    """Handles GET requests for all available drinks in their short format."""
    try:
        print('Request - [GET] /drinks')
        all_drinks = Drink.query.all()
        drinks = [drink.short() for drink in all_drinks]
        return jsonify({
            'success': True,
            'drinks': drinks
        }), 200
    except Exception as e:
        print('Error - [GET] /drinks', e)
        abort(500, 'Internal server error')
    finally:
        db.session.close()


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_detailed_drinks(payload):
    """Handles GET requests for all available drinks in their detailed format."""
    try:
        print('Request - [GET] /drinks-detail')
        all_drinks = Drink.query.all()
        drinks = [drink.long() for drink in all_drinks]
        return jsonify({
            'success': True,
            'drinks': drinks
        }), 200
    except Exception as e:
        print('Error - [GET] /drinks-detail', e)
        abort(500, 'Internal server error')
    finally:
        db.session.close()


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    """Handles POST requests for new drink entries in the database"""
    try:
        print('Request - [POST] /drinks')
        body = request.get_json()

        title = body['title']
        if not title:
            abort(400, description='Bad request: a drink title is required')

        raw_recipe = body['recipe']
        if not raw_recipe:
            abort(400, description='Bad request: a drink recipe is required')
        recipe = json.dumps(raw_recipe)

        drink = Drink(title=title, recipe=recipe)
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': drink.long()
        }), 200
    except Exception as e:
        print('Error - [POST] /drinks', e)
        abort(500, 'Internal server error')
    finally:
        db.session.close()


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    '''Handles PATCH requests to update existing drink entries in the database'''
    try:
        print('Request - [PATCH] /drinks/<id>')
        drink = Drink.query.get(drink_id)

        if not drink:
            abort(404)

        body = request.get_json()

        if 'title' in body:
            drink.title = body['title']

        if 'recipe' in body:
            drink.recipe = json.dumps(body['recipe'])

        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200
    except Exception as e:
        print('Error - [PATCH] /drinks/<id>', e)
        abort(500, 'Internal server error')
    finally:
        db.session.close()


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    '''Handles DELETE requests for drink entries to be removed from the database'''
    try:
        print('Request - [PATCH] /drinks/<id>')
        drink = Drink.query.get(drink_id)

        if not drink:
            abort(404)

        drink.delete()

        return jsonify({
            'success': True,
            'delete': drink_id
        }), 200
    except Exception as e:
        print('Error - [PATCH] /drinks/<id>', e)
        abort(500, 'Internal server error')
    finally:
        db.session.close()


# Error Handling
@app.errorhandler(422)
def unprocessable():
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def unreachable():
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'unreachable'
    }), 404


@app.errorhandler(AuthError)
def handle_auth_error(error: AuthError):
    print(error)
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error['description']
    }), error.status_code,


@app.errorhandler(401)
def handle_auth_error():
    return jsonify({
        'success': False,
        'error': 'unauthorized',
        'message': 'Request is unauthorized',
    }), 401


@app.errorhandler(400)
def handle_bad_request():
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad request'
    }), 400
