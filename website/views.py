from flask import Blueprint, render_template
from .forms import RequestReset, ResetPassword


views = Blueprint('views', __name__)


@views.route('/', methods=['GET','POST'])
def home_page():
    return render_template("home.html")