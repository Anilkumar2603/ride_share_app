from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.models import db, User, Ride, RideRequest, Feedback
from datetime import datetime
import random

admin_routes = Blueprint('admin', __name__)

# Ensure user management functionality is restricted to admins
def check_admin():
    return session.get('role') == 'admin'

def generate_user_id():
    # Generates a unique 4-digit user ID
    while True:
        user_id = str(random.randint(1000, 9999))
        if not User.query.get(user_id):
            return user_id

@admin_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password) and user.role == 'admin':
            session['user_id'] = user.user_id
            session['role'] = 'admin'
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password.')
    
    return render_template('login.html')

@admin_routes.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('admin.login'))

@admin_routes.route('/dashboard')
def dashboard():
    if not check_admin():
        return redirect(url_for('admin.login'))
    return render_template('admin_dashboard.html')

@admin_routes.route('/user_management', methods=['GET', 'POST'])
def user_management():
    if not check_admin():
        return redirect(url_for('admin.login'))

    search_query = request.args.get('search', '')
    users = User.query.filter(User.username.contains(search_query), User.role.in_(['rider', 'driver'])).all()
    
    if request.method == 'POST':
        action = request.form.get('action')
        user_id = request.form.get('user_id')
        
        if action == 'delete':
            user = User.query.get(user_id)
            if user:
                db.session.delete(user)
                db.session.commit()
                flash('User deleted successfully.')
        elif action == 'edit':
            return redirect(url_for('admin.edit_user', user_id=user_id))
        elif action == 'add':
            return redirect(url_for('admin.add_user'))

    return render_template('user_management.html', users=users)

@admin_routes.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if not check_admin():
        return redirect(url_for('admin.login'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        email = request.form['email']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('admin.add_user'))
        
        user_id = generate_user_id()  # Generate a unique 4-digit user ID
        new_user = User(user_id=user_id, username=username, role=role, email=email)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        flash('User added successfully.')
        return redirect(url_for('admin.user_management'))
    
    return render_template('add_user.html')

@admin_routes.route('/edit_user/<string:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if not check_admin():
        return redirect(url_for('admin.login'))
    
    user = User.query.get(user_id)
    
    if not user or user.role == 'admin':
        flash('User not found or cannot be edited.')
        return redirect(url_for('admin.user_management'))
    
    if request.method == 'POST':
        user.username = request.form['username']
        user.set_password(request.form['password'])
        user.role = request.form['role']
        db.session.commit()
        flash('User updated successfully.')
        return redirect(url_for('admin.user_management'))
    
    return render_template('edit_user.html', user=user)

@admin_routes.route('/ride_monitoring', methods=['GET'])
def ride_monitoring():
    if not check_admin():
        return redirect(url_for('admin.login'))
    
    # Fetch active rides and user activities
    active_rides = Ride.query.join(RideRequest).filter(RideRequest.status == 'approved').all()
    user_activities = User.query.all()  # Modify this to get specific activities if needed
    
    # Example: Alerts could be based on criteria like overdue rides, etc.
    alerts = []
    for ride in active_rides:
        if ride.date < datetime.today().date():  # Example condition for overdue rides
            alerts.append(f"Ride {ride.ride_id} is overdue.")
    
    return render_template(
        'ride_monitoring.html',
        active_rides=active_rides,
        user_activities=user_activities,
        alerts=alerts
    )

@admin_routes.route('/reports', methods=['GET'])
def reports():
    if not check_admin():
        return redirect(url_for('admin.login'))
    
    # Placeholder for report data
    report_data = {}  # Replace with actual report generation logic
    
    return render_template('reports.html', report_data=report_data)

@admin_routes.route('/issue_management', methods=['GET'])
def issue_management():
    if not check_admin():
        return redirect(url_for('admin.login'))
    
    # Fetch issue data (this is a placeholder; replace with actual data)
    issues = []  # Replace with actual issue query
    
    return render_template('issue_management.html', issues=issues)

@admin_routes.route('/policy_management', methods=['GET'])
def policy_management():
    if not check_admin():
        return redirect(url_for('admin.login'))
    
    # Fetch policy data (this is a placeholder; replace with actual data)
    policies = []  # Replace with actual policy query
    
    return render_template('policy_management.html', policies=policies)
