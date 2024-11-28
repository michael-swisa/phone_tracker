from flask import request, jsonify, Blueprint
from db_init import neo4j_driver
from neo4j_service import PhoneTracker

phone_blueprint = Blueprint('phone_tracker', __name__)


@phone_blueprint.route("/api/phone_tracker", methods=['POST'])
def get_interaction():
    data = request.get_json()


    if not data:
        return jsonify({"error": "No data provided"}), 400

    interaction = data.get("interaction", {})
    if interaction:
        from_device_id = interaction.get("from_device")
        to_device_id = interaction.get("to_device")

        if from_device_id == to_device_id:
            return jsonify({"error": "The phone is calling itself."}), 400

    tracker = PhoneTracker(neo4j_driver)
    tracker.create_phone_tracker(data)

    return jsonify({"status": "success"}), 200


@phone_blueprint.route("/api/bluetooth_connections", methods=['GET'])
def get_bluetooth_connections():
    tracker = PhoneTracker(neo4j_driver)
    bluetooth_connections = tracker.count_bluetooth_connections()

    return jsonify({'result': bluetooth_connections}), 200


@phone_blueprint.route("/api/strong_signal_devices", methods=['GET'])
def get_strong_signal_devices():
    data = request.args.get('signal_strength_dbm', -60)
    tracker = PhoneTracker(neo4j_driver)
    strong_signal_devices = tracker.find_devices_with_signal_strength(int(data))

    return jsonify({'result': strong_signal_devices}), 200


@phone_blueprint.route("/api/device_connections", methods=['GET'])
def get_device_connections():
    device_id = request.args.get('device_id')
    tracker = PhoneTracker(neo4j_driver)
    device_connections = tracker.count_device_connections(device_id)

    return jsonify({'result': device_connections}), 200


@phone_blueprint.route("/api/direct_connection", methods=['GET'])
def get_direct_connection():
    from_device_id = request.args.get('from_device_id')
    to_device_id = request.args.get('to_device_id')
    tracker = PhoneTracker(neo4j_driver)
    is_direct_connection = tracker.is_device_direct_connection(from_device_id, to_device_id)

    return jsonify({'result': is_direct_connection}), 200


@phone_blueprint.route("/api/most_recent_interaction", methods=['GET'])
def get_most_recent_interaction():
    device_id = request.args.get('device_id')
    tracker = PhoneTracker(neo4j_driver)
    most_recent_interaction = tracker.find_most_recent_interaction(device_id)

    return jsonify({'result': most_recent_interaction}), 200
