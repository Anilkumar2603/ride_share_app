from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.models import db, User, Ride, RideRequest, Feedback
from ml.ai_module import load_models, process_search

driver_routes = Blueprint('driver', __name__)

# Ensure that only drivers can access these routes
def check_driver():
    return session.get('role') == 'driver'

@driver_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password) and user.role == 'driver':
            session['user_id'] = user.user_id
            session['role'] = 'driver'
            return redirect(url_for('driver.dashboard'))
        else:
            flash('Invalid username or password.')
    
    return render_template('driver_login.html')

@driver_routes.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('driver.login'))

@driver_routes.route('/dashboard')
def dashboard():
    if not check_driver():
        return redirect(url_for('driver.login'))
    return render_template('driver_dashboard.html')

@driver_routes.route('/post_ride', methods=['GET', 'POST'])
def post_ride():
    if not check_driver():
        return redirect(url_for('driver.login'))

    if request.method == 'POST':
        destination = request.form.get('destination')
        date = request.form.get('date')
        time = request.form.get('time')
        seats_available = request.form.get('seats_available')
        
        if not all([destination, date, time, seats_available]):
            flash('Missing form data.')
            return redirect(url_for('driver.post_ride'))

        driver_id = session.get('user_id')
        
        new_ride = Ride(destination=destination, date=date, time=time, seats_available=seats_available, driver_id=driver_id)
        db.session.add(new_ride)
        db.session.commit()
        flash('Ride posted successfully.')
        return redirect(url_for('driver.dashboard'))

    return render_template('post_ride.html')

@driver_routes.route('/ride_requests', methods=['GET', 'POST'])
def ride_requests():
    if not check_driver():
        return redirect(url_for('driver.login'))

    driver_id = session.get('user_id')

    if driver_id is None:
        flash('You must be logged in to view ride requests.')
        return redirect(url_for('driver.login'))

    # Fetch ride requests for the current driver
    ride_requests = RideRequest.query.join(Ride).filter(
        RideRequest.ride_id == Ride.ride_id,
        Ride.driver_id == driver_id,
        RideRequest.status == 'pending'
    ).all()

    if request.method == 'POST':
        action = request.form.get('action')
        request_id = request.form.get('request_id')

        ride_request = RideRequest.query.get(request_id)
        if ride_request:
            if action == 'approve':
                ride_request.status = 'approved'
                # Notify the rider
                notify_rider(ride_request)
                flash('Ride request approved.')
            elif action == 'reject':
                ride_request.status = 'rejected'
                flash('Ride request rejected.')
            db.session.commit()

        return redirect(url_for('driver.ride_requests'))

    return render_template('ride_requests.html', ride_requests=ride_requests)



@driver_routes.route('/notify_rider', methods=['POST'])
def notify_rider(ride_request):
    rider = User.query.get(ride_request.rider_id)
    if rider:
        # Send a notification (you can implement email or other notification systems)
        flash(f'Notification sent to {rider.username} about ride request approval.')


@driver_routes.route('/trip_details/<int:ride_id>')
def trip_details(ride_id):
    if not check_driver():
        return redirect(url_for('driver.login'))

    ride = Ride.query.get(ride_id)
    if ride and ride.driver_id == session.get('user_id'):
        return render_template('trip_details.html', ride=ride)
    else:
        flash('No such ride or you are not authorized to view this trip.')
        return redirect(url_for('driver.dashboard'))

@driver_routes.route('/provide_feedback', methods=['GET', 'POST'])
def provide_feedback():
    if not check_driver():
        return redirect(url_for('driver.login'))

    if request.method == 'POST':
        ride_id = request.form.get('ride_id')
        rider_id = request.form.get('rider_id')
        feedback_text = request.form.get('feedback')
        
        feedback = Feedback(user_id=rider_id, trip_id=ride_id, comments=feedback_text)
        db.session.add(feedback)
        db.session.commit()
        
        flash('Feedback submitted successfully.')
        return redirect(url_for('driver.dashboard'))

    return render_template('provide_feedback.html')

models = load_models()

@driver_routes.route('/match_rides', methods=['POST'])
def match_rides():
    search_criteria = request.json
    
    # Process the search criteria with the AI models
    distances, indices = process_search(search_criteria, models)
    
    def fetch_ride_details(indices):
        ride_details = []
        for idx in indices[0]:
            ride = Ride.query.get(idx)
            if ride:
                ride_details.append({
                    'ride_id': ride.ride_id,
                    'destination': ride.destination,
                    'date': ride.date,
                    'time': ride.time,
                    'seats_available': ride.seats_available,
                    'distance': distances[0][list(indices[0]).index(idx)]
                })
        return ride_details
    
    matched_rides = fetch_ride_details(indices)
    return jsonify(matched_rides)
