from flask import jsonify


def return_test():
    return jsonify({'test': 'test'})
