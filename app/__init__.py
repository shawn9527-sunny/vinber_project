from flask import Flask
from .views import db
from .views.supplier import supplier_blueprint
from .views.customer import customer_blueprint
from .views.product import product_blueprint
from .views.index import index_blueprint

def create_app():
    app = Flask(__name__)

    # 設置密鑰，確保它是唯一且不公開的
    app.config['SECRET_KEY'] = 'your_secret_key'  # 請替換為安全的隨機字符串
    # app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default_secret_key')

    # 註冊 Blueprint
    app.register_blueprint(supplier_blueprint)
    app.register_blueprint(customer_blueprint)
    app.register_blueprint(index_blueprint)
    app.register_blueprint(product_blueprint)
    with app.app_context():
        db.init_db()
    
    return app
