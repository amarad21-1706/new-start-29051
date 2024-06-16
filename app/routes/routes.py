# app/routes/routes.py
import json
from flask import Blueprint, render_template, redirect, url_for, flash, session, request, current_app
from flask_login import login_user, current_user, logout_user
from app.models.user import Users, UserRoles
from app.modules.menu_builder import MenuBuilder
from app.forms.forms import LoginForm, RegistrationForm
from app.modules.db import db  # Ensure the correct db import
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import pyotp
from app.utils.utils import (generate_captcha, redirect_based_on_role, get_current_directory, get_parent_directory,
    generate_menu_tree, role_required)

from app.modules.userManager101 import UserManager
from config.config import get_cet_time
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

routes = Blueprint('routes', __name__)
limiter = Limiter(get_remote_address, app=current_app, default_limits=["200/day", "96/hour", "12/minute"])

@routes.route('/back')
def back():
    return redirect(url_for('routes.index'))

def menu_item_allowed(menu_item, user_roles):
    return any(role in menu_item['allowed_roles'] for role in user_roles)


@routes.route('/')
def index():
    current_user_roles = session.get('user_roles', [])
    current_user = session.get('user_id')
    menu_builder = MenuBuilder(current_app.parsed_menu_data, current_user_roles)
    generated_menu = menu_builder.generate_menu(user_roles=current_user_roles, is_authenticated=True, include_protected=False)

    # Determine which template to use based on user roles
    if "Admin" in current_user_roles:
        template = 'admin/admin_page.html'
    elif "Authority" in current_user_roles:
        template = 'authority/authority_page.html'
    elif "Manager" in current_user_roles:
        template = 'manager/manager_page.html'
    elif "Employee" in current_user_roles:
        template = 'employee/employee_page.html'
    elif "Provider" in current_user_roles:
        template = 'provider/provider_page.html'
    else:
        template = 'guest/guest_page.html'

    return render_template(template, main_menu_items=generated_menu,
                           user_roles=current_user_roles, menu_item_allowed=menu_item_allowed)

@routes.route('/access/login', methods=['GET', 'POST'])
@limiter.limit("200/day;96/hour;12/minute")
def login():
    current_user_roles = session.get('user_roles', [])
    menu_builder = MenuBuilder(current_app.parsed_menu_data, current_user_roles)
    generated_menu = menu_builder.generate_menu(user_roles=current_user_roles, is_authenticated=True, include_protected=False)

    if request.method == 'POST':
        user_captcha = request.form['captcha']
        if 'captcha' in session and session['captcha'] == user_captcha:
            username = request.form.get('username')
            password = request.form.get('password')
            user_manager = UserManager(db)
            user = user_manager.authenticate_user(username, password)
            if user:
                if not current_user.is_authenticated:
                    login_user(user)
                    flash('Login Successful')
                    cet_time = get_cet_time()
                    try:
                        create_message(db.session, user_id=user.id, message_type='email', subject='Security check',
                                       body='È stato rilevato un nuovo accesso al tuo account il ' +
                                            cet_time.strftime('%Y-%m-%d') + '. Se eri tu, non devi fare nulla. ' +
                                            'In caso contrario, ti aiuteremo a proteggere il tuo account; ' +
                                            "non rispondere a questa mail e contatta l'amministratore del sistema.",
                                       sender='System', company_id=None,
                                       lifespan='one-off', allow_overwrite=True)
                    except Exception as e:
                        print('Error creating logon message:', e)

                    session['user_roles'] = [role.name for role in user.roles] if user.roles else []
                    session['user_id'] = user.id
                    session['username'] = username

                    try:
                        company_user = CompanyUsers.query.filter_by(user_id=user.id).first()
                        company_id = company_user.company_id if company_user else None
                    except Exception as e:
                        print('Error retrieving company ID:', e)
                        company_id = None

                    if company_id is not None and isinstance(company_id, int):
                        try:
                            subfolder = datetime.now().year
                        except Exception as e:
                            print('Error setting subfolder:', e)

                return redirect_based_on_role(user)

            else:
                flash('Invalid username or password. Please try again.', 'error')
                captcha_text, captcha_image = generate_captcha(300, 100, 5)
                session['captcha'] = captcha_text
                return render_template('access/login.html', captcha=captcha_text, captcha_image=captcha_image, main_menu_items=generated_menu,
                                       user_roles=current_user_roles, menu_item_allowed=menu_item_allowed)
        else:
            flash('Incorrect CAPTCHA! Please try again.', 'error')
            captcha_text, captcha_image = generate_captcha(300, 100, 5)
            session['captcha'] = captcha_text
            return render_template('access/login.html', captcha=captcha_text, captcha_image=captcha_image, main_menu_items=generated_menu,
                                   user_roles=current_user_roles, menu_item_allowed=menu_item_allowed)

    captcha_text, captcha_image = generate_captcha(300, 100, 5)
    session['captcha'] = captcha_text
    print('login -login- now')
    return render_template('access/login.html', captcha=captcha_text, captcha_image=captcha_image, main_menu_items=generated_menu,
                           user_roles=current_user_roles, menu_item_allowed=menu_item_allowed)


@routes.route('/access/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = Users(
            username=form.username.data,
            email=form.email.data,
            user_2fa_secret=pyotp.random_base32(),
            first_name=form.first_name.data,
            mid_name=form.mid_name.data,
            last_name=form.last_name.data,
            address=form.address.data,
            address1=form.address1.data,
            city=form.city.data,
            province=form.province.data,
            region=form.region.data,
            zip_code=form.zip_code.data,
            country=form.country.data,
            tax_code=form.tax_code.data,
            mobile_phone=form.mobile_phone.data,
            work_phone=form.work_phone.data,
            created_on=datetime.now(),
            updated_on=datetime.now()
        )

        try:
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()

            new_user_id = new_user.id

            user_role_guest = UserRoles(user_id=new_user_id, role_id=5)
            db.session.add(user_role_guest)
            db.session.commit()
            flash('Your account has been created! You can now log in.', 'success')
            return redirect(url_for('routes.login'))

        except IntegrityError as e:
            db.session.rollback()
            flash('Username already exists. Please choose a different username.', 'error')

    return render_template('access/signup.html', title='Sign Up', form=form)


# Update other routes similarly

@routes.route('/home/aboutus_1',  methods=['GET', 'POST'])
def aboutus_1():
    return render_template('home/aboutus_1.html')



@routes.route('/home/site_map', methods=['GET', 'POST'])

def site_map():

    # ... (your existing code)

    # Load and read the content of menuStructure.json
    json_file_path = get_parent_directory() / 'static' / 'js' / 'menuStructure101.json'
    with open(json_file_path, 'r') as file:
        menu_structure = json.load(file)

    # Generate the menu tree
    menu_tree = generate_menu_tree(menu_structure)

    # Pass the menu_tree to the template
    return render_template('home/site_map.html', menu_tree=menu_tree)



@routes.route('/home/contact/email')
def contact_email():
    return render_template('home/contact_one.html')

@routes.route('/home/contact/phone',  methods=['GET', 'POST'])
def contact_phone():
    return render_template('home/contact_two.html')


@routes.route('/home/privacy_policy',  methods=['GET', 'POST'])
def privacy_policy():
    return render_template('home/privacy_policy.html')


@routes.route('/home/mission',  methods=['GET', 'POST'])
def mission():
    return render_template('home/mission.html')

@routes.route('/home/services',  methods=['GET', 'POST'])
def services():
    return render_template('home/services.html')

@routes.route('/home/history',  methods=['GET', 'POST'])
def history():
    return render_template('home/history.html')


@routes.route('/access/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('routes.login'))

@routes.route('/admin/admin_page')
@role_required('Admin')
def admin_page():
    current_user_roles = session.get('user_roles', [])
    current_user = session.get('user_id')
    print(f"admin page accessed, user and role are {current_user} {current_user_roles}")

    menu_builder = MenuBuilder(current_app.parsed_menu_data, current_user_roles)
    generated_menu = menu_builder.generate_menu(user_roles=current_user_roles, is_authenticated=True, include_protected=False)

    return render_template('admin/admin_page.html', main_menu_items=generated_menu, user_roles=current_user_roles, menu_item_allowed=menu_item_allowed)

@routes.route('/authority/authority_page')
def authority_page():
    return render_template('authority/authority_page.html')


@routes.route('/manager/manager_page')
def manager_page():
    return render_template('manager/manager_page.html')

@routes.route('/employee/employee_page')
def employee_page():
    return render_template('employee/employee_page.html')

@routes.route('/provider/provider_page')
def provider_page():
    return render_template('provider/provider_page.html')


@routes.route('/guest/guest_page')
def guest_page():
    return render_template('guest/guest_page.html')
