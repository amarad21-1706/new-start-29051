from flask import Blueprint

login = Blueprint('login', __name__)
menubuilder = Blueprint('menubuilder', __name__)

from . import login, menubuilder  # Import your login and menubuilder routes