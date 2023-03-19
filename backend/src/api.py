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
        description = getattr(e, 'message', 'Internal server error')
        code = getattr(e, 'code', 500)
        abort(code, description=description)
    finally:
        db.session.close()


@requires_auth('get:drinks-detail')
@app.route('/drinks-detail', methods=['GET'])
def get_detailed_drinks():
    """Handles GET requests for all available drinks in their detailed format."""
    try:
        print('Request - [GET] /drinks')
        all_drinks = Drink.query.all()
        drinks = [drink.long() for drink in all_drinks]
        return jsonify({
            'success': True,
            'drinks': drinks
        }), 200
    except Exception as e:
        print('Error - [GET] /drinks', e)
        description = getattr(e, 'message', 'Internal server error')
        code = getattr(e, 'code', 500)
        abort(code, description=description)
    finally:
        db.session.close()


@requires_auth('post:drinks')
@app.route('/drinks', methods=['POST'])
def create_drink():
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
        description = getattr(e, 'message', 'Internal server error')
        code = getattr(e, 'code', 500)
        abort(code, description=description)
    finally:
        db.session.close()


'''
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@requires_auth('patch:drinks')
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
def update_drink(drink_id):
    '''Handles PATCH requests to update existing drink entries in the database'''
    try:
        print('Request - [PATCH] /drinks/<id>')
        drink = Drink.query.get(drink_id)

        if not drink:
            abort(404)

        body = request.get_json()

        title = body['title']
        if title:
            drink.title = title

        raw_recipe = body['recipe']
        if raw_recipe:
            recipe = json.dumps(raw_recipe)
            drink.recipe = recipe

        drink.update()

        return jsonify({
            'success': True,
            'drinks': drink.long()
        }), 200
    except Exception as e:
        print('Error - [PATCH] /drinks/<id>', e)
        description = getattr(e, 'message', 'Internal server error')
        code = getattr(e, 'code', 500)
        abort(code, description=description)
    finally:
        db.session.close()


'''
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@requires_auth('delete:drinks')
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
def delete_drink(drink_id):
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
        description = getattr(e, 'message', 'Internal server error')
        code = getattr(e, 'code', 500)
        abort(code, description=description)
    finally:
        db.session.close()


# Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def unreachable(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'unreachable'
    }), 404


@app.errorhandler(401)
def handle_auth_error(error: AuthError):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error['message'],
    }), error.status_code


@app.errorhandler(400)
def handle_bad_request(error: Exception):
    return jsonify({
        'success': False,
        'error': 400,
        'message': error.message
    }), 400
