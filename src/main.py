"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Contact
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/contact', methods=['GET'])
def get_all_contacts():

    contacts_query = Contact.query.all()
    all_contacts = list(map(lambda x: x.serialize(), contacts_query))
    return jsonify(all_contacts), 200

@app.route('/contact', methods=['POST'])
def insert_contact():

    body = request.get_json()

    contact1 = Contact(full_name=body["full_name"], email=body["email"], phone=body["phone"], address=body["address"])
    db.session.add(contact1)
    db.session.commit()

    contacts_query = Contact.query.all()
    all_contacts = list(map(lambda x: x.serialize(), contacts_query))
    return jsonify(all_contacts), 200

@app.route('/contact/<int:id>', methods=['PUT'])
def update_contact(id):

    body = request.get_json()

    contact1 = Contact.query.get(id)
    if contact1 is None:
        raise APIException('Contact not found', status_code=404)

    #Checking is key value exists, and then reassign value
    if "full_name" in body:
        contact1.full_name = body["full_name"]
    if "email" in body:
        contact1.email = body["email"]
    if "phone" in body:
        contact1.phone = body["phone"]
    if "address" in body:
        contact1.address = body["address"]
    db.session.commit()

    contacts_query = Contact.query.all()
    all_contacts = list(map(lambda x: x.serialize(), contacts_query))
    return jsonify(all_contacts), 200

@app.route('/contact/<int:id>', methods=['DELETE'])
def delete_contact(id):

    contact1 = Contact.query.get(id)
    if contact1 is None:
        raise APIException('Contact not found', status_code=404)
    db.session.delete(contact1)
    db.session.commit()

    contacts_query = Contact.query.all()
    all_contacts = list(map(lambda x: x.serialize(), contacts_query))
    return jsonify(all_contacts), 200


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
