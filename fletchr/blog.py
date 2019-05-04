from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort

from fletchr.auth import login_required # the wrapper we made to check if logged in
from fletchr.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db() # connect to database
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)
