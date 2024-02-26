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
    """
    Retrieves all Place objects depending on the JSON
    in the body of the request.
    """
    req = request.get_json(silent=True)

    if req is None or all(req.get(key) is None
                          for key in ['states', 'cities', 'amenities']):
        obj_places = storage.all(Place)
        return jsonify([obj.to_dict() for obj in obj_places.values()])

    places = set()

    if req.get('states'):
        obj_states = [storage.get(State, state_id)
                      for state_id in req.get('states')]
        places.update(place for state in obj_states
                      for city in state.cities for place in city.places)

    if req.get('cities'):
        obj_cities = [storage.get(City, city_id)
                      for city_id in req.get('cities')]
        places.update(place for city in obj_cities for place in city.places)

    if not places:
        places.update(storage.all(Place).values())

    if req.get('amenities'):
        obj_amenities = [storage.get(Amenity, amenity_id)
                         for amenity_id in req.get('amenities')]
        places = [place for place in places
                  if set(obj_amenities).issubset(set(place.amenities))]

    return jsonify([obj.to_dict() for obj in places])
