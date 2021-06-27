from flask import Blueprint, request, session, render_template, flash, redirect
from api.users import get_all_users
from api.user_permissions import get_user_permissions

admin_bp = Blueprint(
    'admin', __name__,
    template_folder = 'templates'
)

@admin_bp.route('/users')
def user_control():
    users = []
    for user_id, user_name in get_all_users():
        users.append([user_name, [perm[0] for perm in get_user_permissions(user_id)]])
    return render_template('users.html', users = users)