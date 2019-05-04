import functools

from flask import (
	Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from fletchr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('register', methods=('GET', 'POST'))
def register():
	if request.method == 'POST': # user just clicked submit

		# get form data
		username = request.form['username']
		password = request.form['password']
		db = get_db() # connect to database
		error = None # init a variable to hold error messages

		# validate the form data
		if not username:
			error = 'Username is required.'
		elif not password:
			error = 'Password is required.'
		# check if the username is taken
		elif db.execute(
			'SELECT id FROM user WHERE username = ?', (username,)
			).fetchone() is not None:
			error = 'User {} is already registered'.format(username)

		if error is None:
			db.execute(
				'INSERT INTO user (username, password) VALUES (?, ?)',
				(username, generate_password_hash(password))
				)
			db.commit()
			return redirect(url_for('auth.login'))
		flash(error)

	# if user just navigated to the page
	return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		db = get_db()
		error = None
		user = db.execute(
			'SELECT * FROM user WHERE username = ?', (username,)).fetchone()

		if user is None:
			error = 'Incorrect username.'
		elif not check_password_hash(user['password'], password):
			error = 'Incorrect passoword.'

		flash(error)

	return render_template('auth/login.html')

@bp.route('/logout') # we have to remove the user from the session
def logout():
	session.clear()
	return redirect(url_for('index'))

# creating editing and deleting blog posts will require user to be logged in
# we use a decorator for this

def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is None: # check if user is loaded
			# redirect to login if not
			return redirect(url_for('auth.login'))
			# if using a blueprint the name is prepended to the name of the
			# view function
		return view(**kwargs)
	return wrapped_view
