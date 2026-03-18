
from flask import Flask, jsonify

def create_app():

    app = Flask(__name__)

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.route("/version")
    def version():
        return jsonify({
            "platform": "Arkansas Civics",
            "api": "v1"
        })

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=8000)
