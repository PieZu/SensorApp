from flask import Blueprint, request, session, render_template, flash, redirect
from api.users import get_all_users, get_user_info
from api.user_permissions import get_user_permissions, user_has_permission
from api.permissions import get_all_permissions, get_permissionid
from user.auth import authenticate

admin_bp = Blueprint(
    'admin', __name__,
    template_folder = 'templates'
)

@admin_bp.route('/users')
@authenticate()
def user_control():
    users = []
    for user_id, user_name in get_all_users():
        users.append([user_name, [perm[0] for perm in get_user_permissions(user_id)]])
    permissions = get_all_permissions()
    return render_template('users.html',
        users = users, 
        permissions = permissions, 
        canCreateUsers = user_has_permission(session['userid'], get_permissionid("CREATE_USERS")),
        canRemoveUsers = user_has_permission(session['userid'], get_permissionid("DELETE_USERS")),
        canManagePerms = user_has_permission(session['userid'], get_permissionid("MANAGE_PERMISSIONS")),
        username = get_user_info(session['userid'])[1]
    )