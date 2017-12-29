"""
Define read-only API that can be used to access Marvel character information
stored in a NoSQL database. I've chosen Firebase.
"""
import json
from flask import Flask, request
import firebase_setup

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hey World"

@app.route('/marvel/characters', methods=['GET'])
@app.route('/marvel/characters/<string:character_id>', methods=['GET'])
def get_character_info(character_id=None):
    """Return character data (JSON) according to the URL args and optional
    query parameters. If a character_id is specified, return data for that
    character. Otherwise return a character collection.

    Query capability is limited here to selecting an order-by key (e.g.
    orderby=First_Appearance) and, if needed, a value to match on that key
    (e.g. equalto=2003-09).

    TODO: (hypothetically) Enhance the database so that character statistics
    are more accessible for querying and analytics. Add more methods and
    implement authentication, esp. if allowing users to edit the database.
    """
    character_ref = firebase_setup.db.reference("Characters")
    if character_id is not None:
        result = character_ref.child(character_id).get()
        return json.dumps(result)
    orderby = request.args.get("orderby") or "Name"
    character_ref = character_ref.order_by_child(orderby)
    equalto = request.args.get("equalto")
    if equalto:
        character_ref = character_ref.equal_to(equalto)
    result = character_ref.get()
    return json.dumps(result)


if __name__ == '__main__':
    app.run(debug=True)