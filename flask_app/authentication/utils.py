from flask_bcrypt import Bcrypt
from flask_login import LoginManager

bcrypt = Bcrypt()
login_manager = LoginManager()

def set_app_for_auth(app):
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'authentication.login'