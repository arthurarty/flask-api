from flask import Flask, request, jsonify


app = Flask(__name__)


@app.route('/')
def hello_world():
    tyk_backend_key = request.headers.get('Tyk-Backend-Key')
    if not tyk_backend_key == 'secret-key':
        return jsonify('Forbidden'), 403
    return jsonify('Hello world!'), 200


if __name__ == '__main__':
    app.run()
