from flask import Flask
from .routes import main_page
from flask_login import LoginManager
from .database import User ,db , migrate
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView





def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
   
    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        db.create_all()  # Ensure database tables are created

    admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')
    admin.add_view(ModelView(User, db.session))


    app.register_blueprint(main_page)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "main_page.login"  # Redirect to the login page for unauthorized users
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))  # Fetch the user from DB



    return app


