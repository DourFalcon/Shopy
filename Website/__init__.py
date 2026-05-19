from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_login import current_user

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Note
    
    with app.app_context():
        db.create_all()
        # Seed sample ecommerce data if none exists
        try:
            from .models import Category, Product
            if Category.query.count() == 0 and Product.query.count() == 0:
                cat1 = Category(name='Books', description='Books and literature')
                cat2 = Category(name='Electronics', description='Gadgets and devices')
                cat3 = Category(name='Home', description='Home and kitchen')
                db.session.add_all([cat1, cat2, cat3])
                db.session.commit()
                p1 = Product(name='The Great Gatsby', description='Classic novel by F. Scott Fitzgerald', price=9.99, category_id=cat1.id)
                p2 = Product(name='Wireless Headphones', description='Noise cancelling over-ear headphones', price=59.99, category_id=cat2.id)
                p3 = Product(name='Coffee Maker', description='12-cup programmable coffee maker', price=29.99, category_id=cat3.id)
                db.session.add_all([p1, p2, p3])
                db.session.commit()
        except Exception:
            # If models are not available or DB locked, skip seeding quietly
            pass

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @app.context_processor
    def inject_user():
        cart = session.get('cart', {})
        cart_count = sum(cart.values()) if isinstance(cart, dict) else 0
        return {'user': current_user, 'cart_count': cart_count}

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')