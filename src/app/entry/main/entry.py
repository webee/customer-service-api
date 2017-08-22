from flask import Blueprint

name = __package__.rsplit('.', 1)[1]
entry = Blueprint(name, __name__)
