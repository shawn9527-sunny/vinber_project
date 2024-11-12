from flask import Flask
from . import db
from .views.supplier import supplier_blueprint
from .views.customer import customer_blueprint
from .views.index import index_blueprint

def create_app():
    app = Flask(__name__)

    # 註冊 Blueprint
    app.register_blueprint(supplier_blueprint)
    app.register_blueprint(customer_blueprint)
    app.register_blueprint(index_blueprint)
    with app.app_context():
        db.init_db()
    
    return app
