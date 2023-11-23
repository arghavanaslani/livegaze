from flask import Blueprint, render_template, current_app, redirect, url_for, flash
from .forms import ArtworkForm
from .models import Artwork
from werkzeug.utils import secure_filename
from extensions.db_config import db
import os

artwork_blueprint = Blueprint('artwork', __name__)


@artwork_blueprint.route('/')
def get_artworks():
    artworks = Artwork.query.all()
    return render_template('artworks/artworks.html',
                           title='Artworks', artworks=artworks)
    pass


@artwork_blueprint.route('/new', methods=['GET', 'SET'])
def add_new_artwork():
    form = ArtworkForm()
    if form.validate_on_submit():
        artwork = Artwork(name=form.name.data, bio=form.bio.data)
        uploaded_image = form.image.data
        image_name = secure_filename(uploaded_image.filename)
        image_path = os.path.join(current_app.config['ARTWORK_UPLOAD_PATH'], image_name)
        uploaded_image.save(image_path)
        artwork.image_path = image_path
        db.session.add(artwork)
        db.session.commit()

        flash('Artwork has been successfully added')
        return redirect(url_for('artworks.add_new_artwork'))
    return render_template('artworks/add_artworks.html', form=form, title='Add Artwork')
    pass
