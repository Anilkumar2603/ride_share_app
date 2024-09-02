from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    user_id = db.Column(db.String(4), primary_key=True)  # Changed to CHAR(4) for 4-digit user_id
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('rider', 'driver', 'admin'), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Ride(db.Model):
    ride_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    destination = db.Column(db.String(255))  # Updated to VARCHAR(255)
    date = db.Column(db.Date)
    time = db.Column(db.Time)
    seats_available = db.Column(db.Integer)
    driver_id = db.Column(db.String(4), db.ForeignKey('user.user_id'))  # Updated to CHAR(4)

    # Relationships
    driver = db.relationship('User', backref='rides')

class RideRequest(db.Model):
    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ride_id = db.Column(db.Integer, db.ForeignKey('ride.ride_id'), nullable=False)
    rider_id = db.Column(db.String(4), db.ForeignKey('user.user_id'), nullable=False)  # Updated to CHAR(4)
    status = db.Column(db.Enum('pending', 'approved', 'rejected'), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    ride = db.relationship('Ride', backref='requests')
    rider = db.relationship('User', backref='requests')

class Trip(db.Model):
    trip_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ride_id = db.Column(db.Integer, db.ForeignKey('ride.ride_id'), nullable=False)
    driver_id = db.Column(db.String(4), db.ForeignKey('user.user_id'), nullable=False)  # Updated to CHAR(4)
    start_location = db.Column(db.String(255), nullable=False)
    end_location = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Enum('ongoing', 'completed'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Payment(db.Model):
    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.trip_id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_status = db.Column(db.Enum('completed', 'failed'), nullable=False)

class Feedback(db.Model):
    feedback_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(4), db.ForeignKey('user.user_id'), nullable=False)  # Updated to CHAR(4)
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.trip_id'), nullable=False)
    
    comments = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='feedbacks')
    trip = db.relationship('Trip', backref='feedbacks')
