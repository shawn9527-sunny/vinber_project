from flask import Blueprint, render_template
from .auth import login_required

index_blueprint = Blueprint('index', __name__, template_folder='templates')

@index_blueprint.route('/')
@login_required
def index():
    return render_template('index.html')
