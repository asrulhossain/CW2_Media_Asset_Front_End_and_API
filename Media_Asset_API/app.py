from flask import Flask
from flask_cors import CORS
from Blueprint.admin.admin import admin_bp
from Blueprint.assets.assets import assets_bp
from Blueprint.audit_logs.audit_logs import audit_logs_bp
from Blueprint.auth.auth import auth_bp
from Blueprint.projects.projects import projects_bp
from Blueprint.tags.tags import tags_bp

app = Flask(__name__)
CORS(app)

# Blueprints
app.register_blueprint(assets_bp)
app.register_blueprint(audit_logs_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(projects_bp)
app.register_blueprint(tags_bp)
app.register_blueprint(admin_bp)

if __name__ == "__main__":
  app.run(debug=True, port=5001)
