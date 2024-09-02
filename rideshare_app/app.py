from flask import Flask
from config import Config
from models import db
from routes.rider_routes import rider_routes
from routes.driver_routes import driver_routes
from routes.admin_routes import admin_routes
from routes.main_routes import main_routes
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    app.register_blueprint(main_routes)
    app.register_blueprint(rider_routes, url_prefix='/rider')
    app.register_blueprint(driver_routes, url_prefix='/driver')
    app.register_blueprint(admin_routes, url_prefix='/admin')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
