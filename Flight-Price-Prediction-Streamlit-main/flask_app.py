from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import numpy as np
import pickle
import os
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None
from utils.preferences import UserPreferences
from utils.analytics import FlightAnalytics

if load_dotenv:
    load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flight_predictions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Secret key for sessions/CSRF - prefer environment variable, fallback to random
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(24)
db = SQLAlchemy(app)

# Login manager setup
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Load the model
model_path = os.path.join(os.path.dirname(__file__), 'model', 'flight_prediction.pkl')
model = pickle.load(open(model_path, 'rb'))

class PredictionHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    source = db.Column(db.String(50), nullable=False)
    destination = db.Column(db.String(50), nullable=False)
    airline = db.Column(db.String(100), nullable=False)
    stops = db.Column(db.Integer, nullable=False)
    duration_hours = db.Column(db.Integer, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    predicted_price = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    # Optional: store settings as JSON string if needed later
    settings = db.Column(db.JSON, nullable=True)
    predictions = db.relationship('PredictionHistory', backref='user', lazy=True)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# No global redirect; '/' will render login when unauthenticated

def flight_prediction(input_data):
    input_data_as_numpy_array = np.asarray(input_data)
    input_data_reshaped = input_data_as_numpy_array.reshape(1,-1)
    prediction = model.predict(input_data_reshaped)
    return round(prediction[0], 2)

@app.route('/')
def home():
    return render_template('home.html')
    sources = ['Chennai', 'Delhi', 'Kolkata', 'Mumbai']
    destinations = ['Cochin', 'Delhi', 'Hyderabad', 'Kolkata']
    airlines = ['Air India', 'GoAir', 'IndiGo', 'Jet Airways', 'Jet Airways Business',
                'Multiple carriers', 'Multiple carriers Premium economy', 'SpiceJet', 
                'Trujet', 'Vistara', 'Vistara Premium economy']
    return render_template('index.html', 
                         sources=sources,
                         destinations=destinations,
                         airlines=airlines)

@app.route('/predict-page')
@login_required
def predict_page():
    # Render the prediction dashboard (same data as previous home)
    sources = ['Chennai', 'Delhi', 'Kolkata', 'Mumbai']
    destinations = ['Cochin', 'Delhi', 'Hyderabad', 'Kolkata']
    airlines = ['Air India', 'GoAir', 'IndiGo', 'Jet Airways', 'Jet Airways Business',
                'Multiple carriers', 'Multiple carriers Premium economy', 'SpiceJet', 
                'Trujet', 'Vistara', 'Vistara Premium economy']
    return render_template('index.html', 
                         sources=sources,
                         destinations=destinations,
                         airlines=airlines)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not email or not password:
            flash('Email and password are required')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match')
            return render_template('register.html')

        existing = User.query.filter_by(email=email).first()
        if existing:
            flash('Email already registered')
            return render_template('register.html')

        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('home'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('predict_page'))

        flash('Invalid email or password')
        return render_template('login.html')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.before_request
def _require_login_for_app():
    # Allow access to public endpoints without authentication
    public_endpoints = {'home', 'login', 'register', 'static'}
    if not current_user.is_authenticated and request.endpoint not in public_endpoints:
        return redirect(url_for('login', next=request.url))

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    try:
        data = request.json
        
        # Process source
        sources = ['Chennai', 'Delhi', 'Kolkata', 'Mumbai']
        source_mapping = {source: 1 if source == data['source'] else 0 for source in sources}
        Source = list(source_mapping.values())

        # Process destination
        destinations = ['Cochin', 'Delhi', 'Hyderabad', 'Kolkata']
        destination_mapping = {dest: 1 if dest == data['destination'] else 0 for dest in destinations}
        Destination = list(destination_mapping.values())

        # Process dates and times
        dep_datetime = datetime.fromisoformat(data['departure'])
        arr_datetime = datetime.fromisoformat(data['arrival'])
        
        duration = arr_datetime - dep_datetime
        Duration_Hours = duration.days * 24 + duration.seconds // 3600
        Duration_Minutes = (duration.seconds % 3600) // 60

        # Process airline
        airlines = ['Air India', 'GoAir', 'IndiGo', 'Jet Airways', 'Jet Airways Business',
                   'Multiple carriers', 'Multiple carriers Premium economy', 'SpiceJet',
                   'Trujet', 'Vistara', 'Vistara Premium economy']
        airline_mapping = {airline: 1 if airline == data['airline'] else 0 for airline in airlines}
        Airlines = list(airline_mapping.values())

        # Create input vector
        journey_input = [
            data['stops'],
            dep_datetime.day,
            dep_datetime.month,
            dep_datetime.hour,
            dep_datetime.minute,
            arr_datetime.hour,
            arr_datetime.minute,
            Duration_Hours,
            Duration_Minutes
        ]
        
        Input = journey_input + Airlines + Source + Destination
        predicted_price = flight_prediction(Input)

        # Save prediction to database
        prediction_record = PredictionHistory(
            source=data['source'],
            destination=data['destination'],
            airline=data['airline'],
            stops=data['stops'],
            duration_hours=Duration_Hours,
            duration_minutes=Duration_Minutes,
            predicted_price=predicted_price,
            user_id=(current_user.id if current_user.is_authenticated else None)
        )
        db.session.add(prediction_record)
        db.session.commit()

        return jsonify({
            'success': True,
            'price': predicted_price,
            'duration': {
                'hours': Duration_Hours,
                'minutes': Duration_Minutes
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/history')
@login_required
def get_history():
    predictions = PredictionHistory.query.filter_by(user_id=current_user.id).order_by(PredictionHistory.timestamp.desc()).all()
    history_data = [{
        'id': p.id,
        'timestamp': p.timestamp.isoformat(),
        'source': p.source,
        'destination': p.destination,
        'airline': p.airline,
        'stops': p.stops,
        'duration': f"{p.duration_hours}h {p.duration_minutes}m",
        'price': p.predicted_price
    } for p in predictions]
    return jsonify(history_data)

@app.route('/history-page')
@login_required
def history_page():
    return render_template('history.html')

@app.route('/export')
@login_required
def export_history():
    import csv
    from io import StringIO
    from flask import make_response
    
    si = StringIO()
    cw = csv.writer(si)
    
    # Write headers
    cw.writerow(['Timestamp', 'Source', 'Destination', 'Airline', 'Stops', 
                 'Duration (hours)', 'Duration (minutes)', 'Predicted Price'])
    
    # Write data
    predictions = PredictionHistory.query.filter_by(user_id=current_user.id).order_by(PredictionHistory.timestamp.desc()).all()
    for p in predictions:
        cw.writerow([
            p.timestamp.isoformat(),
            p.source,
            p.destination,
            p.airline,
            p.stops,
            p.duration_hours,
            p.duration_minutes,
            p.predicted_price
        ])
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=flight_predictions.csv"
    output.headers["Content-type"] = "text/csv"
    return output

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)