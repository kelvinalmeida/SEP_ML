from flask import Flask

app = Flask(__name__) 

from routes.gateway_routes import gateway_bp
app.register_blueprint(gateway_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
