from . import Base
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, Float, DateTime, Date, Time, ForeignKey, Boolean
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref


class User(UserMixin, Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    is_admin: Mapped[str] = mapped_column(Boolean, default=False)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[int] = mapped_column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), default=func.now())
    vendor_id: Mapped[int] = mapped_column(Integer, ForeignKey('vendor.id'), nullable=True)
    vendor = relationship('Vendor', backref=backref('users'))
    
    def __repr__(self):
        return f"User('{self.email}')"
    
    

class Bookings(Base):
    __tablename__ = 'bookings'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    vendor: Mapped[str] = mapped_column(String, nullable=False)
    mis_reference: Mapped[str] = mapped_column(String, nullable=True)
    destination: Mapped[str] = mapped_column(String, nullable=False)
    pallets: Mapped[int] = mapped_column(Integer, nullable=False)
    collection_date: Mapped[str] = mapped_column(Date, nullable=True)
    delivery_date: Mapped[str] = mapped_column(Date, nullable=True)
    tod: Mapped[str] = mapped_column(String, nullable=True)
    booking_time: Mapped[str] = mapped_column(Time, nullable=True)
    booking_ref: Mapped[str] = mapped_column(String, nullable=True)
    po: Mapped[int] = mapped_column(Integer, nullable=False)
    comments: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    charge: Mapped[float] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    user = relationship('User', backref=backref('bookings'))
    
    def __repr__(self):
        return f"Bookings('{self.vendor}')"
    

class Vendor(Base):
    __tablename__ = 'vendor'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str] = mapped_column(String, nullable=False)
    paragon_name: Mapped[str] = mapped_column(String, nullable=False)
    opening_hours: Mapped[str] = mapped_column(Time, nullable=False)
    closing_hours: Mapped[str] = mapped_column(Time, nullable=False)
    trailer_requirement: Mapped[str] = mapped_column(String, nullable=False)
    nearby_store: Mapped[str] = mapped_column(String, nullable=True)
    ATM_comments: Mapped[str] = mapped_column(String, nullable=True)
    charge_to_worksop: Mapped[float] = mapped_column(Float, nullable=False)
    charge_to_swindon: Mapped[float] = mapped_column(Float, nullable=False)
    charge_to_cambuslang: Mapped[float] = mapped_column(Float, nullable=False)
    charge_to_redhouse: Mapped[float] = mapped_column(Float, nullable=False)
    assigned_users = relationship('User', back_populates='vendor', overlaps="users")
    
    
    def __repr__(self):
        return f"Vendor('{self.name}')"
    