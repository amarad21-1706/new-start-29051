
from flask import Flask, jsonify
from forms.forms import MainForm
import requests

from flask import Blueprint, render_template, jsonify, request

import geocoder
from opencage.geocoder import OpenCageGeocode
import pycountry
import phonenumbers
from phonenumbers.phonenumberutil import region_code_for_country_code
from phonenumbers.phonenumberutil import NumberParseException, PhoneNumberType

app = Flask(__name__)

# Create the blueprint object
geonames_bp = Blueprint('geonames', __name__)

@app.route('/api/increment', methods=['POST'])
def increment():
   # Process request and return response
   return jsonify({"message": "Incremented successfully"})


# Function to fetch phone prefixes
# @cached(cache)
def fetch_phone_prefixes():
    prefixes = []
    for country in pycountry.countries:
        try:
            example_number = phonenumbers.example_number_for_type(country.alpha_2, PhoneNumberType.MOBILE)
            phone_prefix = f"+{example_number.country_code}" if example_number else None
            if phone_prefix:
                prefixes.append({'prefix': phone_prefix, 'country': country.name})
        except (NumberParseException, AttributeError, KeyError) as e:
            print(f"Error with country {country.name}: {e}")
            continue  # Skip countries that cause exceptions
    return prefixes

@geonames_bp.route('/phone_prefixes', methods=['GET'])
def get_phone_prefixes():
    return jsonify(fetch_phone_prefixes())

# Function to fetch regions
@geonames_bp.route('/regions')
# @cached(cache)
def get_regions():
    country_code = request.args.get('country_code')
    if not country_code:
        return jsonify({'error': 'Country code is required'}), 400

    url = f'http://api.geonames.org/countryInfoJSON?country={country_code}&username=amarad21'
    response = requests.get(url)
    data = response.json()

    if 'geonames' not in data:
        return jsonify({'error': 'Invalid response from GeoNames API'}), 500

    country_geoname_id = data['geonames'][0].get('geonameId', None)
    if not country_geoname_id:
        return jsonify({'error': 'Could not find geonameId for the country'}), 500

    url = f'http://api.geonames.org/childrenJSON?geonameId={country_geoname_id}&username=amarad21'
    response = requests.get(url)
    data = response.json()

    if 'geonames' not in data:
        return jsonify({'error': 'Invalid response from GeoNames API'}), 500

    regions = [{'code': region.get('geonameId', 'No geonameId'), 'name': region.get('name', 'No name')} for region in data.get('geonames', [])]
    return jsonify(regions)


@geonames_bp.route('/provinces')
def get_provinces():
    region_code = request.args.get('region_code')
    if not region_code:
        return jsonify({'error': 'Region code is required'}), 400

    url = f'http://api.geonames.org/childrenJSON?geonameId={region_code}&username=amarad21'
    response = requests.get(url)
    data = response.json()

    if 'geonames' not in data:
        return jsonify({'error': 'Invalid response from GeoNames API'}), 500

    provinces = [{'code': province.get('geonameId', 'No geonameId'), 'name': province.get('name', 'No name')} for province in data.get('geonames', [])]
    return jsonify(provinces)


@geonames_bp.route('/cities')
def get_cities():
    province_code = request.args.get('province_code')
    if not province_code:
        return jsonify({'error': 'Province code is required'}), 400

    url = f'http://api.geonames.org/childrenJSON?geonameId={province_code}&username=amarad21'
    response = requests.get(url)

    # Check if the response status code is OK (200)
    if response.status_code != 200:
        return jsonify({'error': f'GeoNames API request failed with status code {response.status_code}'}), 500

    data = response.json()

    if 'geonames' not in data:
        return jsonify({'error': 'Invalid response from GeoNames API'}), 500

    cities = [{'name': city.get('name', 'No name'), 'geonameId': city.get('geonameId', 'No geonameId')} for city in
              data.get('geonames', [])]
    return jsonify(cities)

@geonames_bp.route('/streets')
def get_streets():
    city_name = request.args.get('city_name')
    if not city_name:
        return jsonify({'error': 'City name is required'}), 400

    # Use Nominatim to get the bounding box of the city
    nominatim_url = f'https://nominatim.openstreetmap.org/search?q={city_name}&format=json&addressdetails=1&limit=1'
    response = requests.get(nominatim_url)
    if response.status_code != 200:
        return jsonify({'error': 'Nominatim API request failed'}), 500

    try:
        city_data = response.json()
        if not city_data:
            return jsonify({'error': 'City not found in Nominatim data'}), 404
        bbox = city_data[0]['boundingbox']  # Get the city's bounding box
    except requests.exceptions.JSONDecodeError:
        return jsonify({'error': 'Invalid response from Nominatim API'}), 500

    # Use the Overpass API to fetch streets within the bounding box
    overpass_url = f'http://overpass-api.de/api/interpreter?data=[out:json];way["highway"]({bbox[0]},{bbox[2]},{bbox[1]},{bbox[3]});out;'
    overpass_response = requests.get(overpass_url)
    if overpass_response.status_code != 200:
        return jsonify({'error': 'Overpass API request failed'}), 500

    try:
        overpass_data = overpass_response.json()
        streets = [{'name': element['tags'].get('name', 'Unnamed Street')} for element in overpass_data['elements'] if 'tags' in element and 'name' in element['tags']]
    except requests.exceptions.JSONDecodeError:
        return jsonify({'error': 'Invalid response from Overpass API'}), 500

    return jsonify(streets)

@geonames_bp.route('/zip_codes')
def get_zip_codes():
    city_name = request.args.get('city_name')
    if not city_name:
        return jsonify({'error': 'City name is required'}), 400

    url = f'http://api.geonames.org/postalCodeSearchJSON?placename={city_name}&maxRows=1000&username=amarad21'
    response = requests.get(url)

    # Check if the response status code is OK (200)
    if response.status_code != 200:
        return jsonify({'error': f'GeoNames API request failed with status code {response.status_code}'}), 500

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        return jsonify({'error': 'GeoNames API returned an invalid JSON response or no data'}), 500

    zip_codes = [{'postalCode': place.get('postalCode', 'Undefined')} for place in data.get('postalCodes', [])]
    return jsonify(zip_codes)


@geonames_bp.route('/countries', methods=['GET'])
def get_countries():
    countries = [{'alpha2Code': country.alpha_2, 'name': country.name} for country in pycountry.countries]
    return jsonify(countries)
