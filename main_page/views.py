from flask import Blueprint, render_template, current_app, redirect, url_for, flash, Response
from boards.models import Board
from extensions.db_config import db


main_page_blueprint = Blueprint('main_page', __name__)


@main_page_blueprint.route('/')
def index():
    paintings = db.session.query(Board).all()
    return render_template('main_page.html', boards=[ {"id": painting.id , "image_path": painting.image_path ,
                                                      "name": painting.name } for painting in paintings])