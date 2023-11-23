from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired


class ArtworkForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=255)])
    bio = TextAreaField('Bio')
    image = FileField('Image', validators=[FileRequired(), FileAllowed(['jpg', 'png'],
                                                                       'Only use images with extension jpg and png.')])
    submit = SubmitField('Add Artwork')
