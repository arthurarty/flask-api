from flask import Flask, request, jsonify
import functools
import json
import requests
import os
from dotenv import load_dotenv
from flasgger import Swagger, swag_from
import random
from time import sleep

load_dotenv()

app = Flask(__name__)
swagger = Swagger(app)


def accept_only_tyk_requests(func):
    """
    Check header for Tyk-Backend header
    :param func:
    :return:
    """

    @functools.wraps(func)
    def check_header(*args, **kwargs):
        tyk_backend_key = request.headers.get('Tyk-Backend-Key')
        if not tyk_backend_key == 'secret-key':
            return jsonify('Forbidden'), 403
        func(*args, **kwargs)
        return func(*args, **kwargs)
    return check_header


@app.route('/')
@accept_only_tyk_requests
def hello_world():
    return jsonify('Hello world!'), 200


@app.route('/tyk')
@accept_only_tyk_requests
def test_tyk_gateway():
    sleep(3)
    return jsonify(number=random.random())



@app.route('/login/', methods=['POST', 'GET'])
@swag_from('docs/login.yml')
def tyk_login_with_email():
    """
    Login method servers a firebase proxy so that users can access the tyk
    dashboard using already existing console(firebase) credentials.
    """
    email = request.args.get('email') or request.form.get('email')
    password = request.args.get('password') or request.form.get('password')
    if not email or not password:
        return (
            jsonify(
                {
                    "status": "error",
                    "error_code": "BAD_REQUEST_MISSING_FIELD",
                    "error": "Missing Required Field",
                }
            ),
            400,
        )

    firebase_api_key = os.getenv('FIREBASE_API_KEY')
    response = requests.post(
        f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebase_api_key}',
        json={'email': email, 'password': password})
    json_resp = json.loads(response.text)
    if json_resp.get('error'):
        error = json_resp.get('error')
        return jsonify(json_resp), error.get('code')
    return jsonify(json_resp)


if __name__ == '__main__':
    app.run()
