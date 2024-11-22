from flask import Flask
from extensions import db
from routes import main

def create_app():
    app=Flask(__name__)

    app.config['SECRET_KEY'] = 'IIT Madras'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    app.register_blueprint(main)

    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True,port=3000)