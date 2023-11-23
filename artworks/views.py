from flask import Blueprint

artwork_blueprint = Blueprint('artwork', __name__)

@artwork_blueprint.route('/')
def get_artworks():

    pass

@artwork_blueprint.route('/new')
def add_new_artwork():

