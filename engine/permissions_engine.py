
ROLE_PERMISSIONS = {
    "admin": ["create_course","edit_course","view_analytics","manage_users"],
    "instructor": ["create_course","edit_course","view_analytics"],
    "student": ["view_course","track_progress"]
}

def get_permissions(role):
    return ROLE_PERMISSIONS.get(role, [])
