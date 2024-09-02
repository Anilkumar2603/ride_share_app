from flask import Blueprint, render_template
from flask import Blueprint, render_template, request, redirect, url_for, flash

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def home():
    return render_template('main.html')
SECRET_KEY = "hexaware_admin"

@main_routes.route('/secret_admin_access', methods=['GET', 'POST'])
def secret_admin_access():
    if request.method == 'POST':
        entered_key = request.form.get('secret_key')
        if entered_key == SECRET_KEY:
            return redirect(url_for('admin.login'))
        else:
            flash('Invalid secret key. Please try again.')
            return redirect(url_for('main.secret_admin_access'))
    
    return render_template('secret_access.html')