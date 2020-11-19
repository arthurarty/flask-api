from flask import Flask, request, jsonify
import functools


app = Flask(__name__)


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


if __name__ == '__main__':
    app.run()
