from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__, static_url_path="/static")

SWAGGER_URL = "/ml-team-2-service/swagger-ui.html"
API_URL = "/ml-team-2-service/swagger-ui.html/api.yaml"

swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL,)


@app.route("/ml-team-2-service/swagger-ui.html/api.yaml")
def root():
    return app.send_static_file("api.yaml")


app.register_blueprint(swaggerui_blueprint)

app.run(debug=True, port=5000)
