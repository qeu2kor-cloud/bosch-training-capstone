from flask import Flask, jsonify, request

from .checker import ValidationError, check_compliance


def create_app() -> Flask:
    app = Flask(__name__)

    @app.post("/check")
    def check_speed():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(error="Request body must be a JSON object"), 400

        try:
            status = check_compliance(
                payload.get("vehicle_speed"),
                payload.get("speed_limit"),
            )
        except ValidationError as error:
            return jsonify(error=str(error)), 400

        return jsonify(status=status.value), 200

    return app


app = create_app()
