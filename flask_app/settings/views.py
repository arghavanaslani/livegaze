from flask import Blueprint, render_template, request
from flask_login import login_required

from .models import Settings
from flask_app.extensions.db_config import db


settings_blueprint = Blueprint('settings', __name__)


def get_settings_model() -> Settings:
    settings = db.session.query(Settings).first()
    if settings is None:
        settings = Settings()
        db.session.add(settings)
    return settings


@settings_blueprint.route('/')
@login_required
def get_settings():
    settings = db.session.query(Settings).first()
    active_shape = settings.pointer_id
    pointer_size = settings.pointer_size
    return render_template('settings/../templates/settings/settings.html', title='Settings', active_shape=active_shape,
                           pointer_size=pointer_size)


@settings_blueprint.route('/update_slider', methods=['POST'])
@login_required
def update_pointer_size():
    slider_value = request.form.get('slider_value')
    settings = get_settings_model()
    settings.pointer_size = slider_value
    db.session.commit()
    return 'Slider value received'


@settings_blueprint.route('/update_option', methods=['POST'])
@login_required
def update_pointer_shape():
    selected_option = request.form.get('selected_option')
    settings = get_settings_model()
    settings.pointer_id = selected_option
    db.session.commit()
    return 'Point shape received'