from datetime import datetime
from extensions import db
from sqlalchemy import func

class UserQuery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    receiver_email = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_sent = db.Column(db.DateTime, default=datetime.utcnow)
    sender_role = db.Column(db.String(25), nullable=True)
    sender_email = db.Column(db.String(120), nullable=False)

class ServiceProfessional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    service_type = db.Column(db.String(50), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    date_verified = db.Column(db.DateTime, nullable=True)
    is_blocked = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    address = db.Column(db.Text(50), nullable=True)
    ph = db.Column(db.Integer,nullable=True)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    is_blocked = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    admin_access = db.Column(db.Boolean, default=False)
    address = db.Column(db.String(100), nullable=True)
    ph = db.Column(db.Integer,nullable=True)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    time_required = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    provider = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20),default='Requested')
    rating = db.Column(db.Integer, default=0)
    rating_count = db.Column(db.Integer, default=0)

class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('service_professional.id'), nullable=True)
    date_of_request = db.Column(db.DateTime, default=datetime.utcnow)
    date_of_completion = db.Column(db.DateTime, nullable=True)
    service_status = db.Column(db.String(20), nullable=False, default='Requested')
    remarks = db.Column(db.Text, nullable=True)
    offered_amount = db.Column(db.Float, nullable=False)
    payment_status=db.Column(db.String(40), default='pending')

class ServiceReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(db.Integer, db.ForeignKey('service_request.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Text, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)