from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Bookings, Vendor
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, mail
from flask_login import login_user, login_required, logout_user, current_user
from .forms import RegistrationForm, LoginForm, ChangePassword
from .forms import BookingForm, VendorForm, UpgradeToAdmin, DownGradeFromAdmin
from .forms import UserToVendor, VendorEditBooking, EditVendorDetailsForm
from .forms import ConfirmBooking, DeleteBooking, RequestReset, ResetPassword
from datetime import datetime, timedelta
from sqlalchemy import func
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
import os


auth = Blueprint('auth', __name__)


ADMIN_USERS = [1]


s = URLSafeTimedSerializer('h7ghyG66G78d33s3')


######################################################################################################################################################################################


@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Create an instance of the LoginForm
    form = LoginForm()
    request_reset = RequestReset()

    # Extract email and password from the form data
    email = form.email.data
    password = form.password.data

    if form.validate_on_submit():
        # Query the database for a user with the given email
        user = User.query.filter_by(email=email).first()

        if user:
            # Check if the provided password matches the hashed password in the database
            if check_password_hash(user.password, password):
                # Log in the user
                login_user(user)

                # Redirect the user based on their role
                if user.id in ADMIN_USERS or user.is_admin:
                    return redirect(url_for('auth.profile', user=user))
                else:
                    return redirect(url_for('auth.vendor', user=user))
            else:
                # Display an error message for invalid email or password
                flash("Invalid email or password", category="error")
        else:
            # Display an error message for invalid email or password
            flash("Invalid email or password", category="error")

    # Render the login template with the form
    return render_template("login.html", form=form, request_reset=request_reset)


######################################################################################################################################################################################


@auth.route('/logout')
@login_required
def logout():
    # Log out the current user
    logout_user()

    # Render the home template after logging out
    return render_template("home.html")


######################################################################################################################################################################################


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    # Create an instance of the RegistrationForm
    form = RegistrationForm()

    # Extract data from the form
    first_name = form.first_name.data
    last_name = form.last_name.data
    phone = form.phone.data
    email = form.email.data
    password = form.password.data

    if form.validate_on_submit():
        # Check if the email already exists in the database
        result = User.query.filter_by(email=form.email.data).first()

        if result:
            flash(f"{form.email.data} already exists", category="error")
        else:
            # Create a new user and add it to the database
            new_user = User(
                email=email,
                phone=phone,
                first_name=first_name,
                last_name=last_name,
                password=generate_password_hash(
                    password,
                    method='pbkdf2:sha1',
                    salt_length=8
                )
            )
            db.session.add(new_user)
            db.session.commit()

            # Display a success message and log in the new user
            flash(f"Account created for {form.first_name.data}", category="success")

            # Clear form data
            form.first_name.data = ''
            form.last_name.data = ''
            form.phone.data = ''
            form.email.data = ''
            form.password.data = ''

            # Log in the new user and redirect based on user type
            login_user(new_user)

            if new_user.id in ADMIN_USERS:
                return redirect(url_for('auth.profile', user=new_user))
            else:
                return redirect(url_for('auth.vendor', user=new_user))

    return render_template('sign_up.html',
                           form=form,
                           first_name=first_name,
                           last_name=last_name,
                           email=email,
                           password=password)

    
######################################################################################################################################################################################


@auth.route('/profile/confirm-booking', methods=["POST", "GET"])
@login_required
def confirm_booking():
    # Create an instance of the ConfirmBooking form
    confirm_booking = ConfirmBooking()

    # Print form data for debugging purposes
    print(confirm_booking.data)

    if confirm_booking.validate_on_submit():
        # Extract data from the form
        mis_ref = confirm_booking.mis_ref.data
        collection_date = confirm_booking.collection_date.data
        booking_date = confirm_booking.delivery_date.data
        booking_time = confirm_booking.booking_time.data
        booking_ref = confirm_booking.booking_ref.data
        tod = confirm_booking.tod.data
        comments = confirm_booking.comments.data
        status = "Confirmed"

        # Check if dates are in the past
        if collection_date < datetime.today().date() or booking_date == datetime.today().date():
            flash("Collection cannot be in the past / Booking date cannot be today", category='error')
        else:
            # Query the database to find the booking record
            record = Bookings.query.filter_by(mis_reference=mis_ref).first()

            if record:
                # Update the booking record with new data
                record.delivery_date = booking_date
                record.collection_date = collection_date
                record.booking_date = booking_date
                record.booking_time = booking_time
                record.tod = tod
                record.status = status
                record.booking_ref = booking_ref
                record.comments = comments

                db.session.commit()
                flash("Booking Confirmed!", category='success')
                return redirect(url_for('auth.profile'))
            else:
                flash("Ref not found.", category='error')
    else:
        flash(confirm_booking.errors)

    return redirect(url_for('auth.profile'))


######################################################################################################################################################################################


@auth.route('/profile/upgrade-to-admin', methods=["POST", "GET"])
@login_required
def upgrade_to_admin():
    upgrade_to_admin_form = UpgradeToAdmin()
    # Checking if the upgrade form is submitted and the 'submit_upgrade' button is pressed
    if upgrade_to_admin_form.validate_on_submit():
        # Extracting email from the form
        email = upgrade_to_admin_form.email.data
        # Querying the user with the provided email
        user = User.query.filter_by(email=email).first()
        if user:
            # Extracting user ID
            user_id = user.id
            # Checking if the user is already an admin
            if user_id in ADMIN_USERS or user.is_admin == True:
                flash(f"{user.email} is already an admin", category='info')
            else:
                # Upgrading the user to admin status
                user.is_admin = True
                db.session.commit()
                flash("User has been upgraded to admin privileges",
                      category="success")
                return redirect(url_for('auth.profile'))
        else:
            flash("User not found", category='error')
    else:
        flash(upgrade_to_admin_form.errors, category='error')

    return redirect(url_for('auth.profile'))


######################################################################################################################################################################################


@auth.route('/profile/downgrade-admin', methods=["POST", "GET"])
@login_required
def downgrade_admin():
    downgrade_from_admin_form = DownGradeFromAdmin()
    if downgrade_from_admin_form.validate_on_submit():
        # Extracting email from the form
        email = downgrade_from_admin_form.email.data
        # Querying the user with the provided email
        user = User.query.filter_by(email=email).first()
        if user:
            # Extracting user ID
            user_id = user.id
            # Checking if the user is not an admin
            if user_id not in ADMIN_USERS and user.is_admin == False:
                flash(f"{user.email} is not an admin", category='info')
            else:
                # Revoking admin rights from the user
                user.is_admin = False
                db.session.commit()
                flash("User has been revoked of admin rights",
                      category="success")

                return redirect(url_for('auth.profile'))
        else:
            flash("User not found", category='error')
    else:
        flash(downgrade_from_admin_form.errors, category='error')

    return redirect(url_for('auth.profile'))


######################################################################################################################################################################################


@auth.route('/profile/allocate-vendor', methods=["POST", "GET"])
@login_required
def allocate_vendor():
    # Create an instance of the UserToVendor form
    user_to_vendor_form = UserToVendor()

    if user_to_vendor_form.validate_on_submit():
        # Extract data from the form
        email = user_to_vendor_form.user_email.data
        vendor = user_to_vendor_form.vendor_name.data

        # Query the database to check if the user and vendor exist
        vendors = Vendor.query.filter_by(name=vendor).first()
        user = User.query.filter_by(email=email).first()

        if user and vendors:
            # Allocate the user to the vendor
            user.vendor_id = vendors.id
            db.session.commit()

            flash(f"User added to vendor: {vendors.name}", category='success')
            return redirect(url_for('auth.profile'))
        else:
            flash("Email/Vendor not found", category='error')

    return redirect(url_for('auth.profile'))


######################################################################################################################################################################################


@auth.route('/profile/create-vendor', methods=["POST", "GET"])
@login_required
def create_vendor():
    # Create an instance of the VendorForm
    vendor_form = VendorForm()

    if vendor_form.validate_on_submit():
        # Extract data from the form
        vendor_name = vendor_form.vendor_name.data
        address = vendor_form.address.data
        paragon_name = vendor_form.paragon_name.data
        opening_time = vendor_form.opening_time.data
        closing_time = vendor_form.closing_time.data
        trailer_requirement = vendor_form.trailer_requirement.data
        nearby_stores = vendor_form.nearby_stores.data
        ATM_comments = vendor_form.ATM_Comments.data
        charge_to_cambuslang = vendor_form.charge_to_cambuslang.data
        charge_to_redhouse = vendor_form.charge_to_redhouse.data
        charge_to_swindon = vendor_form.charge_to_swindon.data
        charge_to_worksop = vendor_form.charge_to_worksop.data

        # Query the database to check if the vendor already exists
        existing_vendor = Vendor.query.filter_by(name=vendor_name).first()

        if existing_vendor:
            flash(f"{vendor_name} already exists", category="error")
        else:
            # Create a new vendor
            new_vendor = Vendor(
                name=vendor_name,
                address=address,
                paragon_name=paragon_name,
                opening_hours=opening_time,
                closing_hours=closing_time,
                trailer_requirement=trailer_requirement,
                nearby_store=nearby_stores,
                ATM_comments=ATM_comments,
                charge_to_cambuslang=charge_to_cambuslang,
                charge_to_redhouse=charge_to_redhouse,
                charge_to_swindon=charge_to_swindon,
                charge_to_worksop=charge_to_worksop
            )

            # Add the new vendor to the database
            db.session.add(new_vendor)
            db.session.commit()

            flash(f"Account created for {vendor_name}", category="success")
            return redirect(url_for('auth.profile'))
    else:
        flash(vendor_form.errors, category='error')

    return redirect(url_for('auth.profile'))


######################################################################################################################################################################################


@auth.route('/profile/cancel-booking', methods=['GET', 'POST'])
@login_required
def delete_booking():
    # Create an instance of the DeleteBooking form
    delete_booking_form = DeleteBooking()

    if delete_booking_form.validate_on_submit():
        # Get MIS reference from the form
        mis_ref = delete_booking_form.mis_ref.data
        # Query the booking with the provided MIS reference
        booking = Bookings.query.filter_by(mis_reference=mis_ref).first()

        if booking:
            # Delete the booking from the database
            db.session.delete(booking)
            db.session.commit()
            flash("Booking Deleted Successfully", category='success')
        else:
            flash("MIS Reference not found, please try again.", category='error')
    else:
        flash(delete_booking_form.errors)

    return redirect(url_for('auth.profile'))


######################################################################################################################################################################################


@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # Import WTForms for various forms used in the profile view
    vendor_form = VendorForm()
    user_to_vendor_form = UserToVendor()
    downgrade_from_admin_form = DownGradeFromAdmin()
    upgrade_to_admin_form = UpgradeToAdmin()
    confirm_booking_form = ConfirmBooking()
    delete_booking_form = DeleteBooking()

    # Query all bookings from the database
    bookings = Bookings.query.filter_by().all()

    # Calculate total charges per vendor
    result = (
        db.session.query(
            Bookings.vendor.label('vendor_name'),
            func.sum(Bookings.charge).label('total_charge')
        )
        .group_by(Bookings.vendor)
        .all()
    )

    # Query today's bookings
    todays_bookings = Bookings.query.filter(
        Bookings.collection_date == datetime.today().date()).all()

    # Query all vendors and users from the database
    vendors = Vendor.query.filter_by().all()
    users = User.query.filter_by().all()

    return render_template('profile.html',
                           users=users,
                           user=current_user,
                           bookings=bookings,
                           vendor_form=vendor_form,
                           vendors=vendors,
                           result=result,
                           todays_bookings=todays_bookings,
                           upgrade_to_admin_form=upgrade_to_admin_form,
                           downgrade_from_admin_form=downgrade_from_admin_form,
                           user_to_vendor_form=user_to_vendor_form,
                           confirm_booking_form=confirm_booking_form,
                           delete_booking_form=delete_booking_form)


######################################################################################################################################################################################


@auth.route('/login/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    request_reset = RequestReset()
    if request_reset.validate_on_submit():
        email = request_reset.email.data
        token = s.dumps(email, salt='recover-key')
        reset_link = url_for('auth.reset_password', token=token, _external=True)
        send_password_reset_email(email, reset_link)
        flash('Password reset link has been sent to your email, this may take sevral minutes')
    return redirect(url_for('auth.login', request_reset=request_reset))


######################################################################################################################################################################################


@auth.route('/login/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    request_reset = RequestReset()
    reset_password = ResetPassword()
    try:
        email = s.loads(token, salt='recover-key', max_age=3600)  # Link valid for 1 hour
    except:
        flash('The reset link is invalid or has expired.', 'error')
        return redirect(url_for('auth.forgot_password'))

    if reset_password.validate_on_submit():
        # Update the user's password in the database
        new_password = reset_password.password.data
        email = User.query.filter_by(email=email).first()
        email.password = generate_password_hash(new_password,method='pbkdf2:sha1',
                    salt_length=8)
        db.session.commit()
        flash('Password has been reset successfully.')
        return redirect(url_for('auth.login'))

    return render_template('reset_pass.html', email=email, request_reset=request_reset, reset_password=reset_password)


######################################################################################################################################################################################


def send_password_reset_email(email, reset_link):
    subject = 'Password Reset Request'
    html_body = render_template('reset_password_email.html', reset_link=reset_link)
    message = Message(subject, recipients=[email], html=html_body)
    mail.send(message)


######################################################################################################################################################################################
#                                                                                 VENDOR ROUTES                                                                                      #
######################################################################################################################################################################################


@auth.route('/vendor/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    # Create an instance of the ChangePassword form
    change_password_form = ChangePassword()

    # Check if the form is submitted and valid
    if change_password_form.validate_on_submit():
        # Extract the new password from the form
        password = change_password_form.password.data

        # Query the user by ID
        user = User.query.filter_by(id=current_user.id).first()

        if user:
            # Update the user's password in the database
            user.password = generate_password_hash(
                password, method='pbkdf2:sha1', salt_length=8)
            db.session.commit()

            # Flash success message
            flash("Password changed successfully.")

            # Redirect to the vendor page
            return redirect(url_for('auth.vendor'))

    else:
        # Flash password requirements error if the form is not valid or not submitted
        flash("""Password must match and contain at least one digit, 
                 one lowercase letter, one uppercase letter, 
                 and be at least 8 characters long.""", category='error')

    # Redirect to the vendor page
    return redirect(url_for('auth.vendor'))


######################################################################################################################################################################################


@auth.route('/vendor/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    # Create an instance of the EditVendorDetailsForm
    edit_vendor_form = EditVendorDetailsForm()

    # Check if the form is submitted and valid
    if edit_vendor_form.validate_on_submit():
        # Extract form data
        first_name = edit_vendor_form.first_name.data
        last_name = edit_vendor_form.last_name.data
        email = edit_vendor_form.email.data
        phone = edit_vendor_form.phone.data
        address = edit_vendor_form.address.data
        profile_picture = edit_vendor_form.profile_picture.data

        # Query the user by ID
        user = User.query.filter_by(id=current_user.id).first()

        if user:
            # Update user details in the database
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.phone = phone
            user.vendor.address = address
            user.profile_picture = profile_picture.filename
            profile_picture.save(os.path.join('website/static/profile_pictures', profile_picture.filename))
            db.session.commit()
            
            

            # Flash success message
            flash("Changes saved successfully", category='success')

            # Redirect to the vendor page
            return redirect(url_for('auth.vendor'))

    else:
        # Flash form validation errors
        flash(edit_vendor_form.errors, category='error')

    # Redirect to the vendor page if form is not valid or not submitted
    return redirect(url_for('auth.vendor'))


######################################################################################################################################################################################


@auth.route('/vendor/request_booking', methods=['GET', 'POST'])
@login_required
def request_booking():
    # Create an instance of the BookingForm
    booking_form = BookingForm()
    
    # Check if the form is submitted and valid
    if booking_form.validate_on_submit():
        # Initialize default values for new booking
        mis_reference = "MIS:"
        status = "Awaiting Confirmation"
        vendor = current_user.vendor.name
        destination = booking_form.destination.data
        pallets = booking_form.pallets.data
        po = booking_form.po.data
        comments = booking_form.comments.data
        user_id = current_user.id
        
        # Query the charge for the selected destination from the Vendor model
        charge_vendor = Vendor.query.filter_by(name=vendor).first()
        
        # Determine the charge based on the destination
        if destination == "Redhouse" or destination == "Redhouse RCC":
            charge = float(charge_vendor.charge_to_redhouse)
        elif destination == "Swindon" or destination == "Swindon RCC":
            charge = float(charge_vendor.charge_to_swindon)
        elif destination == "Cambuslang" or destination == "Cambuslang RCC":
            charge = float(charge_vendor.charge_to_cambuslang)
        elif destination == "Worksop":
            charge = float(charge_vendor.charge_to_worksop)
        else:
            charge = 0.0
        
        # Create a new booking record in the database
        new_booking = Bookings(user_id=user_id,
                               mis_reference=mis_reference,
                               status=status, vendor=vendor,
                               destination=destination,
                               pallets=pallets,
                               po=po,
                               charge=charge,
                               comments=comments)
        db.session.add(new_booking)
        db.session.commit()

        # Update MIS reference with the booking ID
        get_id = new_booking.id
        mis_ref = f'MIS{get_id}'
        new_booking.mis_reference = mis_ref
        db.session.commit()

        # Flash a success message
        flash(f"Booking has been requested with {mis_ref}")
        
        # Redirect to the vendor page
        return redirect(url_for('auth.vendor'))

    # Redirect to the vendor page if form is not valid or not submitted
    return redirect(url_for('auth.vendor'))


#######################################################################################################################################################################################


@auth.route('/vendor/edit-booking', methods=['GET', 'POST'])
@login_required
def edit_booking():
    # Create an instance of the VendorEditBooking form
    vendor_edit_booking_form = VendorEditBooking()
    
    # Check if the form is submitted and valid
    if vendor_edit_booking_form.validate_on_submit():
        # Retrieve data from the form
        mis_ref = vendor_edit_booking_form.mis_ref.data
        destination = vendor_edit_booking_form.destination.data
        pallets = vendor_edit_booking_form.pallets.data
        po = vendor_edit_booking_form.po.data
        comments = vendor_edit_booking_form.comments.data
        
        # Query the database for the booking with the given MIS reference
        booking = Bookings.query.filter_by(mis_reference=mis_ref).first()
        
        # Check if the booking exists
        if booking:
            # Update booking details
            booking.status = "Awaiting Confirmation"
            booking.destination = destination
            booking.pallets = pallets
            booking.po = po
            booking.comments = comments
            db.session.commit()
            
            # Flash a success message
            flash("Booking has been requested with new changes")
            
            # Redirect to the vendor page
            return redirect(url_for('auth.vendor'))
        else:
            # Flash an error message if the booking is not found
            flash(f"{mis_ref} not found, try again.", category='error')
    
    # Redirect to the vendor page
    return redirect(url_for('auth.vendor'))


#######################################################################################################################################################################################


@auth.route('/vendor', methods=['GET', 'POST'])
@login_required
def vendor():
    # Initialize variables and forms
    result = None
    delete_booking = DeleteBooking()
    change_password = ChangePassword()
    edit_vendor_form = EditVendorDetailsForm()
    booking_form = BookingForm()
    vendor_edit_booking_form = VendorEditBooking()

    # Check if the current user has a vendor and a 'name' attribute
    if current_user.vendor and hasattr(current_user.vendor, 'name'):
        # Retrieve bookings for the current user's vendor
        result = Bookings.query.filter_by(
            vendor=current_user.vendor.name).all()

    # Get the ID of the current user
    bookings = current_user.id

    if current_user.vendor is None:
        todays_bookings = None
        tomorrows_bookings = None
    else:
        # Get todays bookings for current user
        todays_bookings = Bookings.query.filter(Bookings.vendor == current_user.vendor.name).filter(Bookings.collection_date == datetime.today().date()).all()
        tomorrows_bookings = Bookings.query.filter(Bookings.vendor == current_user.vendor.name).filter(Bookings.collection_date == datetime.today().date() + timedelta(days=1)).all()

    # Render the 'vendor.html' template with the necessary data
    return render_template('vendor.html',
                           user=current_user,
                           vendor_edit_booking_form=vendor_edit_booking_form,
                           booking_form=booking_form,
                           edit_vendor_form=edit_vendor_form,
                           change_password=change_password,
                           result=result,
                           bookings=bookings,
                           delete_booking=delete_booking,
                           todays_bookings=todays_bookings,
                           tomorrows_bookings=tomorrows_bookings)




