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

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['ID'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is requred'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title=?, body=? WHERE id=?', (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post = post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    print('id is : ' + str(id))
    db = get_db()
    print('connected to db')
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    print('deleted ' + str(id))
    return redirect(url_for('blog.index'))

# Helpers

def get_post(id, check_author=True):
    # check author is in case we ever want to get a post without checking the author.
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()
    print('got ' + str(post['id']))

    if post is None:
        abort(404, "Post id {0} doesn't exist".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post
