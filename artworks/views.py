from flask import Blueprint, render_template, current_app, redirect, url_for, flash
from .forms import ArtworkForm
from .models import Artwork
from werkzeug.utils import secure_filename
from extensions.db_config import db
import os
from .utils import get_unique_filename
artwork_blueprint = Blueprint('artworks', __name__)


@artwork_blueprint.route('/')
def get_artworks():
    artworks = db.session.query(Artwork).all()
    return render_template('artworks/artworks.html',
                           title='Artworks', artworks=artworks)
    pass


@artwork_blueprint.route('/new', methods=['GET', 'POST'])
def add_artwork():
    form = ArtworkForm()
    if form.validate_on_submit():
        artwork = Artwork(name=form.name.data, bio=form.bio.data)
        uploaded_image = form.image.data
        image_name = secure_filename(uploaded_image.filename)
        image_path = os.path.join(current_app.config['ARTWORK_UPLOAD_PATH'], image_name)
        image_path = get_unique_filename(image_path)
        uploaded_image.save(image_path)
        artwork.image_path = image_path
        db.session.add(artwork)
        db.session.commit()
        flash('Artwork has been successfully added')
        return redirect(url_for('artworks.add_artwork'))
    return render_template('artworks/add_artworks.html', form=form, title='Add Artwork')
    pass
