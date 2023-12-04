- Backhaul Portal

- First of all thank you for taking your time to look at my web application.

- This is a Backhaul Booking Portal, is a web application designed to streamline and optimize the
- process of scheduling and managing backhaul slots for transportation and logistics purposes. 
- This portal facilitates the coordination between vendors and transporters, allowing them to 
- efficiently book time slots for the transportation of goods.

- Key Features:

- Slot Booking: Vendors can request a collection from there depot and the admin team then reserve specific time slots for the transportation of goods, ensuring a systematic and organized workflow.
- Vendor Management: The portal includes features for managing vendor details, such as contact information, preferences, and historical booking data.
- User Authentication: Secure user authentication ensures that only authorized personnel can access and make bookings.
- Real-time Updates: Users receive real-time updates on slot confirmation, helping them make informed decisions and plan logistics effectively.
- Reporting and Analytics: The portal may offer reporting tools and analytics to track and analyze transportation trends, helping businesses make data-driven decisions such as costs.
- Accessibility: The portal is accessible online, allowing users to access it from anywhere with an internet connection, enhancing convenience and flexibility.

- The Backhaul Portal aims to enhance operational efficiency, reduce delays, and improve communication within the supply chain by providing a centralized platform for managing backhaul logistics.


- List the main dependencies:

- bcrypt==4.1.1
- Flask==3.0.0
- Flask-Login==0.6.3
- Flask-LoginManager==1.1.6
- Flask-Mail==0.9.1
- Flask-Migrate==4.0.5
- Flask-SQLAlchemy==3.1.1
- Flask-WTF==1.2.1
- gunicorn==21.2.0
- itsdangerous==2.1.2
- Jinja2==3.1.2
- SQLAlchemy==2.0.23
- Werkzeug==3.0.1
- WTForms==3.1.1

- Installation

- Visit: https://backhaul-portal.onrender.com/

- High level overview

- If there is no users or data in the database or if the database does not exists:
    - Database is created and then user admin@admin.com is created to ensure
      there is always at least 1 admin user to manage to system.
    - Admin can login, create a vendor, make other users admins, view/book/edit bookings, view/edit users.
    - When the admin has created a vendor if not already in the database they can allocate a user to it.
    - User can register an account by entering generic information such as name, email and password.
    - User will not be able to perform any actions until an admin user has allocated the user a vendor.
    - Admin can view a list of users and if the user requires action then it will be shown within the list.
    - When admin has allocated the user to a vendor they are then able to add/edit bookings.
    - User can request a booking and a status and reference number is created status = Awaiting Confirmation as they 
      should not assume that just because they have requested a booking that it is automatically accepted.
    - Admin would then see this on there view bookings and have the option to edit and fill in the rest of the form giving them a date and time.

- Contact

- Robert Kinson
- Robert.Kinson@gxo.com
