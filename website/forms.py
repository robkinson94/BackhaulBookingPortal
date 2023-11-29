from datetime import datetime
from wtforms import (Form, BooleanField, 
                     StringField, validators, 
                     SubmitField, PasswordField)

from wtforms import (IntegerField, DateField, 
                     TimeField, SelectField, 
                     FloatField, TelField, DateTimeField)

from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length, Email, EqualTo
from .models import Vendor

# Form classes


class RegistrationForm(FlaskForm):
    first_name = StringField("First name", validators=[
                             DataRequired(), Length(min=3, max=15)])
    last_name = StringField("Last name", validators=[
                            DataRequired(), Length(min=3, max=15)])
    email = StringField("Email Address", validators=[
                        DataRequired(), Email(), Length(min=5, max=25)])
    phone = TelField("Contact Nummber", validators=[Length(min=11, max=15)])
    super_user = BooleanField("Super User")
    password = PasswordField("Password", validators=[DataRequired(),
                                                     validators.regexp(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$',
                                                     message="Password must contain at least one digit, one lowercase letter, one uppercase letter, and be at least 8 characters long.")])
    password_repeat = PasswordField("Password Repeat", validators=[
                                    DataRequired(), EqualTo('password')])
    submit = SubmitField("Register")


class EditVendorDetailsForm(FlaskForm):
    first_name = StringField("First name", validators=[
                             DataRequired(), Length(min=3, max=15)])
    last_name = StringField("Last name", validators=[
                            DataRequired(), Length(min=3, max=15)])
    email = StringField("Email Address", validators=[
                        DataRequired(), Email(), Length(min=5, max=25)])
    phone = TelField("Contact Nummber", validators=[Length(min=11, max=15)])
    submit_vendor_details = SubmitField("Submit Vendor Changes")


class ChangePassword(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired(),
                                                     validators.regexp(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$',
                                                     message="Password must contain at least one digit, one lowercase letter, one uppercase letter, and be at least 8 characters long.")])
    password_repeat = PasswordField("Password Repeat", validators=[
                                    DataRequired(), EqualTo('password')])
    submit_password_change = SubmitField("Save Changes")


class VendorEditBooking(FlaskForm):
    mis_ref = StringField("MIS Reference", validators=[DataRequired()])
    destination = StringField("Destination", validators=[DataRequired()])
    pallets = IntegerField("Pallet Count", validators=[DataRequired()])
    po = IntegerField("PO Number", validators=[DataRequired()])
    comments = StringField("Comments")
    submit_edit_booking = SubmitField("Submit Changes")


class UpgradeToAdmin(FlaskForm):
    email = StringField("Email Address", validators=[
                        DataRequired(), Email("Must be a valid email!")])
    submit_upgrade = SubmitField("Make Admin")


class DownGradeFromAdmin(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    submit_downgrade = SubmitField("Remove Admin")


class LoginForm(FlaskForm):
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log in")


class BookingForm(FlaskForm):
    vendor = StringField("Vendor")
    mis_ref = StringField("MIS Reference")
    destination = SelectField("Destination", choices=[('Redhouse', 'Redhouse'),
                                                      ('Redhouse RCC',
                                                       'Redhouse RCC'),
                                                      ('Swindon', 'Swindon'),
                                                      ('Swindon RCC',
                                                       'Swindon RCC'),
                                                      ('Worksop', 'Worksop')
                                                      ], validators=[DataRequired()])
    pallets = IntegerField("Pallet Count", validators=[DataRequired()])
    collection_date = DateField("Collection Date")
    delivery_date = DateField("Delivery Date")
    tod = StringField("AM/PM")
    booking_time = TimeField("Booking time")
    booking_ref = StringField("Booking Reference")
    po = IntegerField("PO Number", validators=[DataRequired()])
    comments = StringField("Comments")
    submit_booking = SubmitField("Send Booking Request")


class VendorForm(FlaskForm):
    vendor_name = StringField("Vendor:", validators=[DataRequired()])
    address = StringField("Address", validators=[DataRequired()])
    paragon_name = StringField("Paragon Name", validators=[DataRequired()])
    opening_time = TimeField("Opening Time", validators=[DataRequired()])
    closing_time = TimeField("Closing Time", validators=[DataRequired()])
    trailer_requirement = SelectField("Trailer Requirement:", choices=[('Single Deck', 'Single Deck'),
                                                                       ('Double Deck',
                                                                        'Double Deck'),
                                                                       ('Any', 'Any')], validators=[DataRequired()])
    nearby_stores = SelectField("Nearby Stores:", choices=[('Tamworth', 'Tamworth'),
                                                           ('Derby', 'Derby'),
                                                           ('Northampton',
                                                            'Northampton'),
                                                           ('Southampton',
                                                            'Southampton'),
                                                           ('Wolverhampton', 'Wolverhampton')])
    ATM_Comments = StringField("ATM Comments")
    charge_to_worksop = FloatField(
        "Cost to Worksop (£)", validators=[DataRequired()])
    charge_to_swindon = FloatField(
        "Cost to Swindon (£)", validators=[DataRequired()])
    charge_to_cambuslang = FloatField(
        "Cost to Cambuslang (£)", validators=[DataRequired()])
    charge_to_redhouse = FloatField(
        "Cost to Redhouse (£)", validators=[DataRequired()])
    submit = SubmitField("Submit Changes")


class ConfirmBooking(FlaskForm):
    vendor = StringField("Vendor", validators=[
                         DataRequired()], render_kw={"readonly": True})
    mis_ref = StringField("MIS Reference", render_kw={"readonly": True})
    destination = StringField("Destination", render_kw={"readonly": True})
    pallets = IntegerField("Pallet Count", validators=[
                           DataRequired()], render_kw={"readonly": True})
    collection_date = DateField("Collection Date", validators=[
                                DataRequired()], format="%Y-%m-%d")
    delivery_date = DateField("Delivery Date", validators=[
                              DataRequired()], format="%Y-%m-%d")
    tod = SelectField("AM/PM", choices=[("AM", "AM"), ("PM", "PM")])
    booking_time = TimeField("Booking time", format="%H:%M")
    booking_ref = StringField("Booking Reference")
    po = IntegerField("PO Number", validators=[
                      DataRequired()], render_kw={"readonly": True})
    comments = StringField("Comments")
    confirm_booking = SubmitField("Confirm Booking")


class UserToVendor(FlaskForm):
    user_email = StringField("Email", validators=[DataRequired(), Email()])
    vendor_name = StringField("Vendor", validators=[DataRequired()])
    submit_allocation = SubmitField("Allocate User to Vendor")


class ForgotPassword(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Send Email")


class DeleteBooking(FlaskForm):
    mis_ref = StringField("MIS Reference", validators=[DataRequired()])
    delete_booking = SubmitField("Delete Booking")
