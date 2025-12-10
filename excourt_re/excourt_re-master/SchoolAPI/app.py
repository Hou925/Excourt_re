from app import create_app
from flask_swagger_ui import get_swaggerui_blueprint

app = create_app()

# Swagger configuration
SWAGGER_URL = '/api/docs'
API_URL = '/static/swagger.yaml'

# Create Swagger UI blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "School API Documentation"
    }
)

# Register Swagger UI blueprint
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

if __name__ == "__main__":
    print(f"Swagger Docs Running on http://localhost:5000{SWAGGER_URL}")
    app.run(host="0.0.0.0", debug=True)
