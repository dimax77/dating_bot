# app/api/geo.py
from flask import Blueprint, jsonify, current_app
import json
import os

geo = Blueprint('geo', __name__)

@geo.route('/geo/countries')
def get_countries():
    with open(os.path.join(current_app.static_folder, 'data/countries.json')) as f:
        data = json.load(f)
        countries = sorted([entry['country'] for entry in data])
        return jsonify(countries)

@geo.route('/geo/cities/<country>')
def get_cities(country):
    with open(os.path.join(current_app.static_folder, 'data/countries.json')) as f:
        data = json.load(f)
        for entry in data:
            if entry['country'].lower() == country.lower():
                return jsonify(entry['cities'])
        return jsonify([])  # если не найдено
