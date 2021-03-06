import os

from flask import Flask


def create_app(test_config=None):
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_mapping(
		SECRET_KEY='dev',
		DATABASE=os.path.join(app.instance_path, 'fletchr.sqlite'),
	)

	if test_config is None:
		# load the instance config, if it exists, when not testing
		app.config.from_pyfile('config.py', silent=True)
	else:
		# load the test config if passed in
		app.config.from_mapping(test_config)

	# ensure the instance folder exists
	try: # is this breaking the 'ask forgiveness rule?'
		os.makedirs(app.instance_path)
	except OSError:
		pass

	# a simple page that says hello
	@app.route('/hello')
	def hello():
		return 'Hello, World!'

	from . import db # relative import
	db.init_app(app)

	# instead of defining all the routes here, they are defined in blueprints
	# and registered like so
	from . import auth
	app.register_blueprint(auth.bp)

	# and then register our blog blueprint
	from . import blog
	app.register_blueprint(blog.bp)
	app.add_url_rule('/', endpoint='index')
	# since the blog is the main feature, it gets to live at '/' and 'blog.index'

	return app
