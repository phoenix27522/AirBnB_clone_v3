#!/usr/bin/python3
'''Contains the index view for the API.'''
from api.v1.views import app_views
from flask import jsonify
from models import storage
from models.state import State
from models.city import City
from models.user import User
from models.place import Place
from models.review import Review
from models.amenity import Amenity


@app_views.route('/status', methods=['GET'], strict_slashes=False)
def status():
    """Returns a JSON response with status OK."""
    return jsonify({"status": "OK"})


@app_views.route('/stats', methods=['GET'], strict_slashes=False)
def get_stats():
    """Retrieves the number of each object type"""
    stats = {
        'states': storage.count(State),
        'cities': storage.count(City),
        'users': storage.count(User),
        'places': storage.count(Place),
        'reviews': storage.count(Review),
        'amenities': storage.count(Amenity),
    }
    return jsonify(stats)
