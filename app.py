from flask import Flask
from routes import phone_blueprint

app = Flask(__name__)
app.register_blueprint(phone_blueprint)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)