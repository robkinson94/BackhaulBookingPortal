from flask import Blueprint, render_template
from .forms import RequestReset, ResetPassword


views = Blueprint('views', __name__)


@views.route('/', methods=['GET','POST'])
def home_page():
    return render_template("home.html")


@views.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
