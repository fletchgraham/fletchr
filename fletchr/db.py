import sqlite3

import click # I bet this is so we can do database stuff from command line later
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
	if 'db' not in g: # we have to check so we don't make another connec
		g.db = sqlite3.connect(
			current_app.config['DATABASE'],
			detect_types=sqlite3.PARSE_DECLTYPES
		)
		g.db.row_factory = sqlite3.Row 
		# I think that makes it so fetch returns immutable dicts instead of tups

	return g.db

def close_db(e=None):
	db = g.pop('db', None) # people don't use enough pop

	if db is not None: # don't need to close it if it ain't there
		db.close()

def init_db():
	db = get_db()

	with current_app.open_resource('schema.sql') as f:
		db.executescript(f.read().decode('utf8'))
	
	# open_resource opens a file relative to the fletchr package

@click.command('init-db') # create a command line command
@with_appcontext
def init_db_command():
	"""Clear the existing data and create new tables."""
	init_db()
	click.echo('Initialized the database.')

# our functions need to be registered with the app instance, but we are using
# a factory function so the instance isn't available when writing these functions,# so we write a function that takes the app and does this registration.

def init_app(app):
	app.teardown_appcontext(close_db) # call close_db after response
	app.cli.add_command(init_db_command) # can now be called with the flask cmd


