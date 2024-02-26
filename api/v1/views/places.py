#!/usr/bin/python3
"""handels places"""
from flask import jsonify, request, abort
from models import storage
from models.place import Place
from api.v1.views import app_views
from models.amenity import Amenity
from models.city import City
from models.place import Place
from models.state import State
from models.user import User


@app_views.route('/cities/<city_id>/places',
                 methods=['GET'], strict_slashes=False)
def get_places(city_id):
    """Retrieves the list of all Place objects of a City"""
    city = storage.get("City", str(city_id))
    if city is None:
        abort(404)
    places = [place.to_dict() for place in city.places]
    return jsonify(places)


@app_views.route('/places/<place_id>', methods=['GET'], strict_slashes=False)
def get_place(place_id):
    """Retrieves a Place object"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route('/places/<place_id>',
                 methods=['DELETE'], strict_slashes=False)
def delete_place(place_id):
    """Deletes a Place object"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    storage.delete(place)
    storage.save()
    return jsonify({})


@app_views.route('/cities/<city_id>/places',
                 methods=['POST'], strict_slashes=False)
def create_place(city_id):
    """Creates a Place"""
    city = storage.get("City", str(city_id))
    if city is None:
        abort(404)

    data = request.get_json(silent=True)
    if data is None:
        abort(400, 'Not a JSON')
    if 'user_id' not in data:
        abort(400, 'Missing user_id')
    if 'name' not in data:
        abort(400, 'Missing name')

    user = storage.get("User", str(data['user_id']))
    if user is None:
        abort(404)

    new_place = Place(city_id=city_id, **data)
    storage.new(new_place)
    storage.save()

    return jsonify(new_place.to_dict()), 201


@app_views.route('/places/<place_id>', methods=['PUT'], strict_slashes=False)
def update_place(place_id):
    """Updates a Place object"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)

    data = request.get_json(silent=True)
    if data is None:
        abort(400, 'Not a JSON')

    ignore_keys = ['id', 'user_id', 'city_id', 'created_at', 'updated_at']
    for key, value in data.items():
        if key not in ignore_keys:
            setattr(place, key, value)

    storage.save()
    return jsonify(place.to_dict()), 200


@app_views.route('/places_search', methods=['POST'], strict_slashes=False)
def places_search():
    """Search for Place objects based on JSON in the request body"""
    try:
        request_json = request.get_json()
    except Exception:
        abort(400, 'Not a JSON')

    if not request_json or not any(key in request_json
                                   for key in ['states',
                                               'cities', 'amenities']):
        places = storage.all("Place").values()
        return jsonify([place.to_dict() for place in places])

    states = request_json.get('states', [])
    cities = request_json.get('cities', [])
    amenities = request_json.get('amenities', [])

    if not all(isinstance(lst, list) for lst in [states, cities, amenities]):
        abort(400, 'Invalid JSON format')

    places_result = set()

    for state_id in states:
        state = storage.get("State", state_id)
        if state:
            places_result.update(state.places)

    for city_id in cities:
        city = storage.get("City", city_id)
        if city:
            places_result.update(city.places)

    if not states and not cities:
        places_result.update(storage.all("Place").values())

    if amenities:
        filtered_places = []
        for place in places_result:
            place_amenities = {amenity.id for amenity in place.amenities}
            if set(amenities).issubset(place_amenities):
                filtered_places.append(place)
        places_result = filtered_places

    return jsonify([place.to_dict() for place in places_result])
