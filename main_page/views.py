from flask import Blueprint, render_template, current_app, redirect, url_for, flash, Response
from artworks.models import Artwork
from extensions.db_config import db



main_page_blueprint = Blueprint('main_page', __name__)


@main_page_blueprint.route('/')
def main_page():
    paintings = db.session.query(Artwork).all()
    return render_template('main_page.html', boards=[ {"id": painting.id , "image_path": painting.image_path ,
                                                      "name": painting.name } for painting in paintings])