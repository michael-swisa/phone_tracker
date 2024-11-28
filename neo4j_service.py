class PhoneTracker:
    def __init__(self, driver):
        self.driver = driver

    def create_phone_tracker(self, data):
        devices = data.get("devices", [])
        interaction = data.get("interaction", {})

        query_create_device = """
            MERGE (d:Device {id: $id})
            SET d.name = $name,
                d.brand = $brand,
                d.model = $model,
                d.os = $os,
                d.latitude = $latitude,
                d.longitude = $longitude,
                d.altitude_meters = $altitude,
                d.accuracy_meters = $accuracy
        """

        query_create_interaction = """
            MATCH (from:Device {id: $from_device_id}), (to:Device {id: $to_device_id})
            MERGE (from)-[r:CONNECTED {
                method: $method,
                bluetooth_version: $bluetooth_version,
                signal_strength_dbm: $signal_strength,
                distance_meters: $distance,
                duration_seconds: $duration,
                timestamp: $timestamp
            }]->(to)
        """

        with self.driver.session() as session:
            for device in devices:
                device_params = {
                    "id": device["id"],
                    "name": device["name"],
                    "brand": device["brand"],
                    "model": device["model"],
                    "os": device["os"],
                    "latitude": device["location"]["latitude"],
                    "longitude": device["location"]["longitude"],
                    "altitude": device["location"]["altitude_meters"],
                    "accuracy": device["location"]["accuracy_meters"],
                }

                session.run(query_create_device, device_params)

            if interaction:
                interaction_params = {
                    "from_device_id": interaction["from_device"],
                    "to_device_id": interaction["to_device"],
                    "method": interaction["method"],
                    "bluetooth_version": interaction["bluetooth_version"],
                    "signal_strength": interaction["signal_strength_dbm"],
                    "distance": interaction["distance_meters"],
                    "duration": interaction["duration_seconds"],
                    "timestamp": interaction["timestamp"],
                }

                session.run(query_create_interaction, interaction_params)

    def count_bluetooth_connections(self):
        query = """
            MATCH (start:Device)
            MATCH (end:Device)
            WHERE start <> end
            MATCH path = shortestPath((start)-[:CONNECTED*]->(end))
            WHERE ALL(r IN relationships(path) WHERE r.method = 'Bluetooth')
            WITH path, length(path) as pathLength
            ORDER BY pathLength DESC
            LIMIT 1
            RETURN length(path) as length
        """
        with self.driver.session() as session:
            result = session.run(query)

            return result.single()["length"]

    def find_devices_with_signal_strength(self, signal_strength_dbm):
        query = """
            MATCH (d1:Device)-[r:CONNECTED]->(d2:Device)
            WHERE r.signal_strength_dbm > $signal_strength_dbm
            RETURN d1.id AS device_from, d2.id AS device_to, r.signal_strength_dbm AS signal_strength
        """
        with self.driver.session() as session:
            result = session.run(query, {"signal_strength_dbm": signal_strength_dbm})

            devices = []
            for record in result:
                devices.append({
                    "device_from": record["device_from"],
                    "device_to": record["device_to"],
                    "signal_strength_dbm": record["signal_strength"]
                })

        return devices

    def count_device_connections(self, device_id):
        query = """
            MATCH (d:Device)-[r:CONNECTED]-(d2:Device)
            WHERE d.id = $device_id
            RETURN COUNT(r) as connection_count
        """
        with self.driver.session() as session:
            result = session.run(query, {"device_id": device_id})

            return result.single()["connection_count"]

    def is_device_direct_connection(self, from_device_id, to_device_id):
        query = """
            MATCH (d1:Device)-[r:CONNECTED]-(d2:Device)
            WHERE d1.id = $from_device_id AND d2.id = $to_device_id
            RETURN COUNT(r) > 0 as is_connection
        """
        with self.driver.session() as session:
            result = session.run(query, {"from_device_id": from_device_id, "to_device_id": to_device_id})

            return result.single()["is_connection"]

    def find_most_recent_interaction(self, device_id):
        query = """
            MATCH (d:Device)-[r:CONNECTED]-(other:Device)
            WHERE d.id = $device_id
            RETURN other.id AS other_device_id, r.timestamp AS interaction_timestamp
            ORDER BY r.timestamp DESC
            LIMIT 1
        """
        with self.driver.session() as session:
            result = session.run(query, {"device_id": device_id})
            record = result.single()

            if record:
                return {
                    "other_device_id": record["other_device_id"],
                    "interaction_timestamp": record["interaction_timestamp"]
                }
            else:
                return None
