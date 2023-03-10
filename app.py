from flask import Flask
from models.models import db, loginManager
from routes.routes import routes
from routes.api import apiRoutes
import os

app = Flask(__name__)
app.secret_key = "OMG_so_secret"
app.template_folder = 'templates'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL") or "sqlite:///database.db"
app.register_blueprint(routes)
app.register_blueprint(apiRoutes, name="apiRoutes")
loginManager.init_app(app)
loginManager.login_view = "routes.login"
loginManager.login_message_category = "warning"
db.init_app(app)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=False, port=int(os.environ.get("PORT", 5000)))
