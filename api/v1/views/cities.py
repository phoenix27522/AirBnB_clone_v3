#!/usr/bin/python3
"""Script that handls City objects"""
from flask import Flask, jsonify, request, abort
from models import storage
from models.city import City
from models.state import State
from api.v1.views import app_views


@app_views.route('/states/<state_id>/cities',
                 methods=['GET'], strict_slashes=False)
def get_cities(state_id):
    """Retrieves the list of all City objects of a State"""
    state = storage.get(State, state_id)
    if state is None:
        abort(404)
    cities = [city.to_dict() for city in state.cities]
    return jsonify(cities)


@app_views.route('/cities/<city_id>', methods=['GET'], strict_slashes=False)
def get_city(city_id):
    """Retrieves a City object"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    return jsonify(city.to_dict())


@app_views.route('/cities/<city_id>', methods=['DELETE'], strict_slashes=False)
def delete_city(city_id):
    """Deletes a City object"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    storage.delete(city)
    storage.save()
    return jsonify({})


@app_views.route('/states/<state_id>/cities',
                 methods=['POST'], strict_slashes=False)
def create_city(state_id):
    """Creates a City"""
    city = request.get_json(silent=True)
    if city is None:
        abort(400, 'Not a JSON')
    if not storage.get("State", str(state_id)):
        abort(404)
    if "name" not in city:
        abort(400, 'Missing name')
    city["state_id"] = state_id
    new_city = City(**city)
    new_city.save()
    response = jsonify(new_city.to_dict())
    response.status_code = 201
    return response


@app_views.route('/cities/<city_id>', methods=['PUT'], strict_slashes=False)
def update_city(city_id):
    """Updates a City object"""
    city = request.get_json(silent=True)
    if city is None:
        abort(400, 'Not a JSON')
    objs = storage.get("City", str(city_id))
    if objs is None:
        abort(404)
    for key, val in city.items():
        if key not in ["id", "created_at", "updated_at", "state_id"]:
            setattr(objs, key, val)
    objs.save()
    return jsonify(objs.to_dict())
