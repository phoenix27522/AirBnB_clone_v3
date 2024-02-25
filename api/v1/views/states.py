#!/usr/bin/python3
"""states"""

from flask import jsonify, request, abort
from models import storage
from models.state import State
from api.v1.views import app_views
import json


@app_views.route('/states', methods = ['GET'], strict_slashes=False)
def states():
    states = [obj.to_dict() for obj in storage.all(State).values()]
    return (jsonify(states))

@app_views.route('/states/<state_id>', methods = ['GET'], strict_slashes=False)
def get_state(state_id):
    """return states by id or all states if there is no id """
    state = None
    state = storage.get(State, state_id)
    if state:
        return (jsonify(state.to_dict()))
    else:
        abort(404)

@app_views.route('states', methods=['POST'], strict_slashes=False)
def create_state():
    """Post request"""
    try:
        data = request.get_json()
    except json.decoder.JSONDecodeError:
        abort(400, "Not a JSON")

    name = data.get("name")
    if not name:
        abort(400, "Missing name")
    
    state = State(name=name)
    state.save()
    return (jsonify(state.to_dict())),201

@app_views.route('states/<state_id>', methods=['DELETE'], strict_slashes=False)
def delete_state(state_id):
    """Delete request"""
    state = storage.get(State, state_id)
    if state:
        state.delete()
        storage.save()
        return (jsonify({}))
    else:
        abort(404)

@app_views.route('states/<state_id>', methods=['PUT'], strict_slashes=False)
def update_state(state_id):
    """PUT method"""
    state = storage.get(State, state_id)
    if state:
        try:
            data = request.get_json()
        except json.decoder.JSONDecodeError:
            abort(400, "Not a JSON")
        state.name = data.get("name")
        storage.save()
        return jsonify(state.to_dict()),200
    else:
        abort(404)
