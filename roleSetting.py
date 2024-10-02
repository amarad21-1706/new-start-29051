from functools import wraps
from flask import redirect, url_for, session, render_template

class AccessControl:
    def __init__(self):
        # Define user roles
        self.ADMIN_ROLE = 'Admin'
        self.AUTHORITY_ROLE = 'Authority'
        self.EMPLOYEE_ROLE = 'Employee'
        self.MANAGER_ROLE = 'Manager'

        # Define menu branches for each role
        self.ADMIN_MENU_BRANCHES = ['AdminDashboard', 'ManageUsers', 'ManageSettings', 'Authority', 'Company', 'Public']
        self.AUTHORITY_MENU_BRANCHES = ['AuthorityDashboard', 'ViewReports', 'AuthorityBranch', 'Public']
        self.EMPLOYEE_MENU_BRANCHES = ['EmployeeDashboard', 'Company', 'Public']
        self.MANAGER_MENU_BRANCHES = ['ManagerDashboard', 'Company', 'SubmenuA', 'SubmenuB', 'Public']

    # Custom decorator to check user roles and menu access
    def requires_role(self, required_roles, required_menu_branches):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Check if the user is logged in
                if 'user' not in session:
                    return redirect(url_for('login'))

                user = session['user']
                user_roles = user.get('roles', [])
                user_menu_branches = user.get('menu_branches', [])

                # Check if the user has the required roles and menu branches
                if any(role in user_roles for role in required_roles) and \
                        any(branch in user_menu_branches for branch in required_menu_branches):
                    return func(*args, **kwargs)
                else:
                    return render_template('unauthorized.html')

            return wrapper

        return decorator


'''
# Example of using the class
access_control = AccessControl()

# Example usage of the decorator for Admin
@app.route('/admin/dashboard')
@access_control.requires_role([access_control.ADMIN_ROLE], access_control.ADMIN_MENU_BRANCHES)
def admin_dashboard():
    return render_template('admin_dashboard.html')

# Example usage of the decorator for Authority
@app.route('/authority/dashboard')
@access_control.requires_role([access_control.AUTHORITY_ROLE], access_control.AUTHORITY_MENU_BRANCHES)
def authority_dashboard():
    return render_template('authority_dashboard.html')

# Example usage of the decorator for Employee
@app.route('/employee/dashboard')
@access_control.requires_role([access_control.EMPLOYEE_ROLE], access_control.EMPLOYEE_MENU_BRANCHES)
def employee_dashboard():
    return render_template('employee_dashboard.html')

# Example usage of the decorator for Manager
@app.route('/manager/dashboard')
@access_control.requires_role([access_control.MANAGER_ROLE], access_control.MANAGER_MENU_BRANCHES)
def manager_dashboard():
    return render_template('manager_dashboard.html')'''
