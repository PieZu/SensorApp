from flask import Blueprint, request, session, render_template, flash, redirect
from api.sensors import get_all_sensors
from api.logs import get_logs_from_sensor
import numpy as np

visualisation_bp = Blueprint(
    'visualisation', __name__,
    template_folder = 'templates'
)
@visualisation_bp.route('/chart/')
def chart():
    formatted = []
    metadata = []
    return render_template('chart.html', datasets=get_all_sensors())