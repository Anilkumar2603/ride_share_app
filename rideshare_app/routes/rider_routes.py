from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.models import db, User, Ride, RideRequest, Feedback
from datetime import datetime

rider_routes = Blueprint('rider', __name__)

# Ensure that only riders can access these routes
def check_rider():
    return session.get('role') == 'rider'

@rider_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password) and user.role == 'rider':
            session['user_id'] = user.user_id
            session['role'] = 'rider'
            return redirect(url_for('rider.dashboard'))
        else:
            flash('Invalid username or password.')
    
    return render_template('rider_login.html')

@rider_routes.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        user = User.query.filter_by(username=username, role='rider').first()
        
        if user:
            # Simplified password reset logic
            flash('A password reset link has been sent to your email address.')
            return redirect(url_for('rider.reset_password'))
        else:
            flash('No user found with that username.')
    
    return render_template('forgot_password.html')

@rider_routes.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        username = request.form['username']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('rider.reset_password'))
        
        user = User.query.filter_by(username=username, role='rider').first()
        
        if user:
            user.set_password(new_password)
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('rider.login'))
        else:
            flash('No user found with that username.')
    
    return render_template('reset_password.html')

@rider_routes.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash('You have been logged out.')
    return redirect(url_for('rider.login'))

@rider_routes.route('/dashboard', methods=['GET'])
def dashboard():
    if not check_rider():
        return redirect(url_for('rider.login'))

    user_id = session.get('user_id')

    # Fetch upcoming rides for the rider
    upcoming_rides = Ride.query.join(RideRequest).filter(
        RideRequest.rider_id == user_id,
        RideRequest.status == 'approved'
    ).all()
    
    return render_template('rider_dashboard.html', upcoming_rides=upcoming_rides)

@rider_routes.route('/search', methods=['GET', 'POST'])
def search_ride():
    if request.method == 'POST':
        destination = request.form.get('destination')
        date = request.form.get('date')
        time = request.form.get('time')
        
        # Fetch rides based on search criteria
        rides = Ride.query.filter(
            Ride.destination.ilike(f'%{destination}%'),
            Ride.date == date,
            Ride.time == time
        ).all()
        
        return render_template('ride_results.html', rides=rides)
    
    return render_template('search_ride.html')

@rider_routes.route('/provide_feedback', methods=['GET', 'POST'])
def provide_feedback():
    if not check_rider():
        return redirect(url_for('rider.login'))

    if request.method == 'POST':
        user_id = session.get('user_id')
        ride_id = request.form.get('ride_id')
        feedback_text = request.form.get('feedback')
        
        if not user_id:
            flash('You need to be logged in to provide feedback.')
            return redirect(url_for('rider.login'))
        
        if not ride_id or not feedback_text:
            flash('Please provide both Ride ID and feedback.')
            return redirect(url_for('rider.provide_feedback'))
        
        # Create new feedback entry
        feedback = Feedback(user_id=user_id, trip_id=ride_id, comments=feedback_text)
        db.session.add(feedback)
        db.session.commit()
        
        flash('Feedback submitted successfully.')
        return redirect(url_for('rider.dashboard'))
    
    return render_template('provide_feedback.html')

@rider_routes.route('/request_ride', methods=['GET', 'POST'])
def request_ride():
    if not check_rider():
        return redirect(url_for('rider.login'))

    if request.method == 'POST':
        ride_id = request.form.get('ride_id')
        rider_id = session.get('user_id')

        # Ensure ride_id and rider_id are valid
        if not Ride.query.get(ride_id):
            flash('Invalid ride.')
            return redirect(url_for('rider.request_ride'))

        # Create a new ride request
        ride_request = RideRequest(ride_id=ride_id, rider_id=rider_id, status='pending')
        db.session.add(ride_request)
        db.session.commit()

        flash('Ride request submitted successfully.')
        return redirect(url_for('rider.dashboard'))

    # Fetch available rides to show on the form
    available_rides = Ride.query.filter(Ride.date >= datetime.today().date()).all()
    return render_template('request_ride.html', available_rides=available_rides)
