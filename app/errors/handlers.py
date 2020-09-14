from flask import render_template

from app.errors import bp

@bp.errorhandler(404)
def page_not_found(event):
    return render_template('404.html'), 404