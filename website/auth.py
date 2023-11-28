from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from .models import User, Bookings, Vendor
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from sqlalchemy.orm import Session
from flask_login import login_user, login_required, logout_user, current_user, user_unauthorized
from .forms import DeleteBooking, RegistrationForm, LoginForm, ForgotPassword, BookingForm, VendorForm, UpgradeToAdmin, DownGradeFromAdmin, UserToVendor, VendorEditBooking, EditVendorDetailsForm, ChangePassword, ConfirmBooking, DeleteBooking
from datetime import datetime, time, timedelta
from sqlalchemy import func, select, literal_column
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message


auth = Blueprint('auth', __name__)

ADMIN_USERS = [1]


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    email = form.email.data
    password = form.password.data
    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                if user.id in ADMIN_USERS or user.is_admin:
                    return redirect(url_for('auth.profile', user=user))
                else:
                    return redirect(url_for('auth.vendor', user=user))
            else:
                flash("Invalid email or password", category="error")
        else:
            flash("Invalid email or password", category="error")

    return render_template("login.html", form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template("home.html")


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    form = RegistrationForm()
    first_name = form.first_name.data
    last_name = form.last_name.data
    phone = form.phone.data
    email = form.email.data
    password = form.password.data
    if form.validate_on_submit():
        result = User.query.filter_by(email=form.email.data).first()
        if result:
            flash(f"{form.email.data} already exists", category="error")
        else:
            new_user = User(email=email,
                            phone=phone,
                            first_name=first_name,
                            last_name=last_name,
                            password=generate_password_hash(password,
                                                            method='pbkdf2:sha1',
                                                            salt_length=8))
            db.session.add(new_user)
            db.session.commit()
            flash(f"Account created for {form.first_name.data}", category="success")
            form.first_name.data = ''
            form.last_name.data = ''
            form.phone.data = ''
            form.email.data = ''
            form.password.data = ''
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
    

@auth.route('/profile/confirm-booking', methods=["POST", "GET"])
@login_required
def confirm_booking():
    confirm_booking = ConfirmBooking()
    print(confirm_booking.data)
    if confirm_booking.validate_on_submit():
        mis_ref = confirm_booking.mis_ref.data
        collection_date = confirm_booking.collection_date.data
        booking_date = confirm_booking.delivery_date.data
        booking_time = confirm_booking.booking_time.data
        booking_ref = confirm_booking.booking_ref.data
        tod = confirm_booking.tod.data
        comments = confirm_booking.comments.data
        status = "Confirmed"
        # am_threshold = time(17,59)
        # pm_threshold = time(23,59)
        # if booking_time < pm_threshold and booking_time > am_threshold:
        #     tod = "AM"
        # else:
        #     tod = "PM"
        # if booking_date.weekday() == (6):
        #     collection_date = booking_date - timedelta(days=2)
        # elif booking_date.weekday() == (0) and tod == "AM":
        #     collection_date = booking_date - timedelta(days=3)
        # elif booking_date.weekday() != (5, 6, 0) and tod == "AM":
        #     collection_date = collection_date - timedelta(days=1)
        # else:
        #     collection_date = booking_date
        
        record = Bookings.query.filter_by(mis_reference=mis_ref).first()
        
        if record:
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
            if user_id in ADMIN_USERS and user.is_admin == True:
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
                flash("User has been revoked of admin rights", category="success")
                return redirect(url_for('auth.profile'))
        else:
            flash("User not found", category='error')
    else:
        flash(downgrade_from_admin_form.errors, category='error')
    
    return redirect(url_for('auth.profile'))


@auth.route('/profile/allocate-vendor', methods=["POST", "GET"])
@login_required
def allocate_vendor():
    user_to_vendor_form = UserToVendor()
    if user_to_vendor_form.validate_on_submit():
        email = user_to_vendor_form.user_email.data
        vendor = user_to_vendor_form.vendor_name.data
        vendors = Vendor.query.filter_by(name=vendor).first()
        user = User.query.filter_by(email=email).first()
        if user and vendors:
            user.vendor_id = vendors.id
            db.session.commit()
            flash(f"User added to vendor: {vendors.name}", category='success')
            return redirect(url_for('auth.profile'))
        else:
            flash("Email/Vendor not found", category='error')
            
    return redirect(url_for('auth.profile'))


@auth.route('/profile/create-vendor', methods=["POST", "GET"])
@login_required
def create_vendor():
    vendorform = VendorForm()
    if vendorform.validate_on_submit():
        vendor_name = vendorform.vendor_name.data
        address = vendorform.address.data
        paragon_name = vendorform.paragon_name.data
        opening_time = vendorform.opening_time.data
        closing_time = vendorform.closing_time.data
        trailer_requirement = vendorform.trailer_requirement.data
        nearby_stores = vendorform.nearby_stores.data
        ATM_Comments = vendorform.ATM_Comments.data
        charge_to_cambuslang = vendorform.charge_to_cambuslang.data
        charge_to_redhouse = vendorform.charge_to_redhouse.data
        charge_to_swindon = vendorform.charge_to_swindon.data
        charge_to_worksop = vendorform.charge_to_worksop.data
        vendor = Vendor.query.filter_by(name=vendor_name).first()
        if vendor:
            flash(f"{vendor_name} already exists", category="error")
        else:
            new_vendor = Vendor(name=vendor_name,
                                address=address,
                                paragon_name=paragon_name,
                                opening_hours=opening_time,
                                closing_hours=closing_time,
                                trailer_requirement=trailer_requirement,
                                nearby_store=nearby_stores,
                                ATM_comments=ATM_Comments,
                                charge_to_cambuslang=charge_to_cambuslang,
                                charge_to_redhouse=charge_to_redhouse,
                                charge_to_swindon=charge_to_swindon,
                                charge_to_worksop=charge_to_worksop)
            db.session.add(new_vendor)
            db.session.commit()
            flash(f"Account created for {vendor_name}", category="success")
            return redirect(url_for('auth.profile'))
    else:
        flash(vendorform.errors, category='error')
    
    return redirect(url_for('auth.profile'))


@auth.route('/profile/cancel-booking', methods=['GET', 'POST'])
@login_required
def delete_booking():
    delete_booking = DeleteBooking()
    if delete_booking.validate_on_submit():
        mis_ref = delete_booking.mis_ref.data
        booking = Bookings.query.filter_by(mis_reference=mis_ref).first()
        if booking:
            db.session.delete(booking)
            db.session.commit()
            flash("Booking Deleted Successfully", category='success')
            return redirect(url_for('auth.profile'))
        else:
            flash("MIS Reference not found please try again.", category='error')
    else:
        flash(delete_booking.errors)
    return redirect(url_for('auth.profile'))


@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # Importing the WTForms for downgrade and upgrade forms
    vendorform = VendorForm()
    user_to_vendor_form = UserToVendor()
    downgrade_from_admin_form = DownGradeFromAdmin()
    upgrade_to_admin_form = UpgradeToAdmin()
    confirm_booking = ConfirmBooking()
    delete_booking = DeleteBooking()
    bookings = Bookings.query.filter_by().all()
    result = (
    db.session.query(
        Bookings.vendor.label('vendor_name'),
        func.sum(Bookings.charge).label('total_charge')
    )
    .group_by(Bookings.vendor)
    .all()
    )
    
    todays_bookings = Bookings.query.filter(Bookings.collection_date == datetime.today().date()).all()
    
    
    vendors = Vendor.query.filter_by().all()
    users = User.query.filter_by().all()

    

    return render_template('profile.html', users=users, user=current_user,
                           bookings=bookings,
                           vendorform=vendorform,
                           vendors=vendors,
                           result=result,
                           todays_bookings=todays_bookings,
                           upgrade_to_admin_form=upgrade_to_admin_form,
                           downgrade_from_admin_form=downgrade_from_admin_form,
                           user_to_vendor_form=user_to_vendor_form,
                           confirm_booking=confirm_booking,
                           delete_booking=delete_booking)


######################################################################################################################################################################################


@auth.route('vendor/cancel-booking', methods=['GET','POST'])
@login_required
def cancel_booking():
    delete_booking = DeleteBooking()
    if delete_booking.validate_on_submit():
        mis_ref = delete_booking.mis_ref.data
        booking = Bookings.query.filter_by(mis_reference=mis_ref).first()
        if booking:
            booking.status = "**Cancellation Requested**"
            db.session.commit()
            flash("Booking cancellation has been requested", category='success')
            return redirect(url_for('auth.vendor'))
        else:
            flash("Booking no found", category='error')
    else:
        flash(delete_booking.errors)
    return redirect(url_for('auth.vendor'))


@auth.route('/vendor/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    change_password = ChangePassword()
    if change_password.validate_on_submit():
        password = change_password.password.data
        user = User.query.filter_by(id=current_user.id).first()
        if user:
            user.password = generate_password_hash(password, method='pbkdf2:sha1',
                                                                    salt_length=8)
            db.session.commit()
            flash("Password changed successfully.")
            return redirect(url_for('auth.vendor'))
    else:
        flash("Password must match and contain at least one digit, one lowercase letter, one uppercase letter, and be at least 8 characters long.", category='error')
    return redirect(url_for('auth.vendor'))


######################################################################################################################################################################################


@auth.route('/vendor/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    edit_vendor_form = EditVendorDetailsForm()
    if edit_vendor_form.validate_on_submit():
        first_name = edit_vendor_form.first_name.data
        last_name = edit_vendor_form.last_name.data
        email = edit_vendor_form.email.data
        phone = edit_vendor_form.phone.data

        user = User.query.filter_by(id=current_user.id).first()

        if user:
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.phone = phone
            db.session.commit()
            flash("Changes saved successfully", category='success')
            redirect(url_for('auth.vendor'))
    else:
        flash(edit_vendor_form.errors, category='error')
    return redirect(url_for('auth.vendor'))


######################################################################################################################################################################################


@auth.route('/vendor/request_booking', methods=['GET', 'POST'])
@login_required
def request_booking():
    
    booking_form = BookingForm()
    if booking_form.validate_on_submit():
        mis_reference = "MIS:"
        status = "Awaiting Confirmation"
        vendor = current_user.vendor.name
        destination = booking_form.destination.data
        pallets = booking_form.pallets.data
        po = booking_form.po.data
        comments = booking_form.comments.data
        user_id = current_user.id
        charge_vendor = Vendor.query.filter_by(name=vendor).first()
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

        get_id = new_booking.id
        mis_ref = f'MIS{get_id}'

        new_booking.mis_reference = mis_ref
        db.session.commit()

        flash(f"Booking has been requested with {mis_ref}")
        return redirect(url_for('auth.vendor'))

    return redirect(url_for('auth.vendor'))


#######################################################################################################################################################################################


@auth.route('/vendor/edit-booking', methods=['GET', 'POST'])
@login_required
def edit_booking():
    vendor_edit_booking_form = VendorEditBooking()
    if vendor_edit_booking_form.validate_on_submit():
        mis_ref = vendor_edit_booking_form.mis_ref.data
        destination = vendor_edit_booking_form.destination.data
        pallets = vendor_edit_booking_form.pallets.data
        po = vendor_edit_booking_form.po.data
        comments = vendor_edit_booking_form.comments.data
        booking = Bookings.query.filter_by(mis_reference=mis_ref).first()
        if booking:
            booking.status = "Awaiting Confirmation"
            booking.destination = destination
            booking.pallets = pallets
            booking.po = po
            booking.comments = comments
            db.session.commit()
            flash(f"Booking has been requested with new changes")
            return redirect(url_for('auth.vendor'))
        else:
            flash(f"{mis_ref} not found, try again.", category='error')
    return redirect(url_for('auth.vendor'))


#######################################################################################################################################################################################


@auth.route('/vendor/search_mis_ref', methods=['GET', 'POST'])
@login_required
def search_bookings():
    if request.method == "POST":
        mis_ref = request.form.get('mis_ref')
        search_ref = Bookings.query.filter_by(mis_reference=mis_ref).first()
        return redirect(url_for('auth.vendor', search_ref=search_ref))



#######################################################################################################################################################################################


@auth.route('/vendor', methods=['GET', 'POST'])
@login_required
def vendor():
    result = None
    delete_booking = DeleteBooking()
    change_password = ChangePassword()
    edit_vendor_form = EditVendorDetailsForm()
    booking_form = BookingForm()
    vendor_edit_booking_form = VendorEditBooking()

    if current_user.vendor and hasattr(current_user.vendor, 'name'):
        result = Bookings.query.filter_by(
            vendor=current_user.vendor.name).all()

    bookings = current_user.id

    return render_template('vendor.html',
                           user=current_user,
                           vendor_edit_booking_form=vendor_edit_booking_form,
                           booking_form=booking_form,
                           edit_vendor_form=edit_vendor_form,
                           change_password=change_password,
                           result=result,
                           bookings=bookings,
                           delete_booking=delete_booking)


# @auth.route('/forgot_password', methods=['GET','POST'])
# def forgot_password():
#     form = ForgotPasswordResetForm()
#     if form.validate_on_submit():
#         send_reset_email(form.email.data)
#     return render_template('forgot_password.html', user=current_user, form=form)
