from flask import Flask,Blueprint,redirect,session,render_template,url_for,request,jsonify
from extensions import db
from models import *
from sqlalchemy import func,and_
import json

main = Blueprint('main',__name__)






#Authorization Routes

@main.route("/", methods=["GET"])
def roleselect():
    if 'role' in session:
        return redirect(url_for('main.login'))
    return render_template('index.html')

@main.route("/login", methods=['GET', 'POST'])
def login():
    if 'role' not in session and request.method == 'GET':
        return redirect(url_for('main.roleselect'))

    if 'email' in session:
        role = session['role']
        email = session['email']
        password = session['password']

        if role == "service professional":
            sp = ServiceProfessional.query.filter_by(email=email).first()
            if sp and sp.password == password and not sp.is_blocked:
                return redirect(url_for('main.spdb'))
            elif sp and sp.password == password and sp.is_blocked:
                return render_template('userblocked.html')
            else:
                return render_template('invalid.html')

        elif role == "customer":
            customer = Customer.query.filter_by(email=email).first()
            if customer and customer.password == password and not customer.is_blocked :
                return redirect(url_for('main.customerdb'))
            elif customer and customer.password == password and customer.is_blocked:
                return render_template('userblocked.html')
            else:
                return render_template('invalid.html')

        else:
            admin = Customer.query.filter_by(email=email).first()
            if admin and admin.password == password and admin.admin_access==True:
                customers = Customer.query.all()
                sps = ServiceProfessional.query.all()
                services= Service.query.all()
                service_requests = ServiceRequest.query.all()
                return redirect(url_for('main.admindb',customers=customers,sps=sps,services=services,service_requests=service_requests))
            else:
                return render_template('invalid.html')

    elif 'role' in session:
        role = session['role']
        return render_template('login.html')

    if request.method == 'POST':
        session['role'] = role = request.form.get('selectRole')
        return render_template('login.html')
    
@main.route('/direct', methods=["GET", "POST"])
def direct():
    if request.method == 'POST' and 'role' in session:
        role = session['role']
        name = request.form.get('name')
        email = request.form.get('loginemail')
        session['password'] = password = request.form.get('loginpassword')
        session['email'] = email

        if role == "service professional":
            sp = ServiceProfessional.query.filter_by(email=email).first()

            if sp:
                return redirect(url_for('main.login'))
            if name is None:
                return redirect(url_for('main.login'))
            service_type = request.form.get('service_type')
            experience = request.form.get('experience')
            new_service_pro = ServiceProfessional(name=name, username=name, service_type=service_type, experience=experience, email=email, password=password)
            db.session.add(new_service_pro)
            db.session.commit()

            return redirect(url_for('main.spdb'))

        elif role == "customer":
            customer = Customer.query.filter_by(email=email).first()

            if customer:
                return redirect(url_for('main.login'))
            if name is None:
                return redirect(url_for('main.login'))
            new_customer = Customer(name=name,username=name, email=email, password=password)
            db.session.add(new_customer)
            db.session.commit()

            return redirect(url_for('main.customerdb'))

        elif role == "admin":
            admin = Customer.query.filter_by(email=email).first()
            customers = Customer.query.all()
            sps = ServiceProfessional.query.all()
            services= Service.query.all()
            service_requests = ServiceRequest.query.all()


            if admin:
                return redirect(url_for('main.login',customers=customers,sps=sps,services=services,service_requests=service_requests))
            if name is None:
                return redirect(url_for('main.login'))
            new_admin = Customer(username=name,name=name ,email=email, password=password)
            db.session.add(new_admin)
            db.session.commit()

            return redirect(url_for('main.admindb'))

    return redirect(url_for("main.roleselect"))

@main.route("/register")
def register():
    if 'role' not in session:
        return redirect(url_for("main.roleselect"))

    if 'email' in session:
        role = session['role']
        if role == "service professional":
            return redirect(url_for('main.spdb'))
        elif role == "customer":
            return redirect(url_for('main.customerdb'))
        else:
            return redirect(url_for('main.admindb'))
    else:
        role = session['role']
        if role == "service professional":
            return render_template("spregister.html")
        elif role == "customer":
            return render_template("customerregister.html")
        elif role == "admin":
            return render_template("adminregister.html")

    return redirect(url_for('login'))

@main.route('/blocked')
def blocked():
    return render_template('userblocked.html')

@main.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.roleselect"))

@main.route("/post_query", methods=['POST','GET'])
def postquery():
    if 'email' in session:
        if request.method=='GET':
            return render_template('query.html')
        if request.method=='POST':
            sender_email = session['email']
            subject = request.form.get('topic')
            receiver_email='admin1@gmail.com'
            message = request.form.get('description')
            sender_role=session['role']
            new_query = UserQuery(receiver_email=receiver_email,subject=subject,message=message,sender_role=sender_role,sender_email=sender_email)
            db.session.add(new_query)
            db.session.commit()

        return redirect(url_for('main.login'))
    return redirect(url_for('main.roleselect'))

    
@main.route("/view_query", methods=['POST','GET'])
def viewquery():
    if 'email' in session :
        if request.method=='GET':
            queries=UserQuery.query.filter_by(receiver_email=session['email']).all()
            return render_template('viewqueries.html',queries=queries)
        
@main.route('/reply/<int:q_id>>', methods=['POST','GET'])
def reply(q_id):
    if 'email' in session:
        q = UserQuery.query.filter_by(id=q_id).first()
        reply=request.form.get('reply')
        sender=q.receiver_email
        receiver=q.sender_email
        topic=f'Reply from {sender}'
        new_query = UserQuery(sender_email=sender,subject=topic,message=reply,sender_role=session['role'],receiver_email=receiver)
        db.session.add(new_query)
        db.session.commit()
        return redirect(url_for('main.viewquery'))
    return redirect(url_for('main.roleselect'))

@main.route('/delete_query/<int:q_id>>', methods=['POST','GET'])
def deletequery(q_id):
    if 'email' in session:
        q = UserQuery.query.filter_by(id=q_id).first()
        db.session.delete(q)
        db.session.commit()
        return redirect(url_for('main.viewquery'))
    return redirect(url_for('main.roleselect'))







#Admin Routes
from sqlalchemy import func

@main.route("/admin_dashboard", methods=['GET', 'POST'])
def admindb():
    if session.get('role') == 'admin':
        if 'email' not in session and request.method == 'GET':
            return redirect(url_for('main.login'))

        elif request.method == 'POST':
            session['email'] = request.form.get('loginemail')
        
        customers = Customer.query.all()
        sps = ServiceProfessional.query.all()
        verified_customer = Customer.query.filter(Customer.address.isnot(None)).all()
        verified_sp = ServiceProfessional.query.filter_by(is_verified=True).all()
        
        verified = len(verified_customer) + len(verified_sp)
        total = len(customers) + len(sps)
        
        values = [
            len(customers),
            len(sps),
            len(ServiceRequest.query.filter_by(service_status='Requested').all()),
            len(ServiceRequest.query.filter_by(service_status='Accepted').all()),
            len(ServiceRequest.query.filter_by(service_status='Completed').all()),
            verified,
            (total - verified -1)
        ]
        
        top_sps = (
            db.session.query(
                ServiceProfessional.name,
                func.avg(Service.rating).label('avg_rating'),
            )
            .join(ServiceRequest, ServiceRequest.professional_id == ServiceProfessional.id)
            .join(Service, Service.id == ServiceRequest.service_id)
            .filter(Service.rating > 0)
            .group_by(ServiceProfessional.id)
            .order_by(func.avg(Service.rating).desc())
            .limit(5)
            .all()
        )

        top_sps_labels = [sp.name for sp in top_sps]
        top_sps_ratings = [sp.avg_rating for sp in top_sps]

        top_customers = (
            db.session.query(
                Customer.name,
                func.count(ServiceRequest.id).label('request_count')
            )
            .join(ServiceRequest, ServiceRequest.customer_id == Customer.id)
            .group_by(Customer.id)
            .order_by(func.count(ServiceRequest.id).desc())
            .limit(3)
            .all()
        )

        top_customers_labels = [customer.name for customer in top_customers]
        top_customers_counts = [customer.request_count for customer in top_customers]
        return render_template('admindb.html', 
                               values=values, 
                               top_sps_labels=top_sps_labels, 
                               top_sps_ratings=top_sps_ratings,
                               top_customers_labels=top_customers_labels, 
                               top_customers_counts=top_customers_counts)

    return redirect(url_for('main.roleselect'))




@main.route("/customers",methods=['GET','POST'])
def customers():
    if 'email' in session and session['role']=='admin':
        customer=Customer.query.all()
        return render_template('viewcustomers.html',Customer=customer)
    return redirect(url_for('main.roleselect'))

@main.route("/service_professionals",methods=['GET','POST'])
def sps():
    if 'email' in session and session['role']=='admin':
        Sp=ServiceProfessional.query.all()
        return render_template('viewsp.html',sp=Sp)
    return redirect(url_for('main.roleselect'))


@main.route("/verify_user/<int:user_id>", methods=['POST'])
def verify_user(user_id):
    user = ServiceProfessional.query.get(user_id)
    if user:
        user.is_verified = True
        user.date_verified=datetime.utcnow()
        db.session.commit()
    return redirect(url_for('main.sps'))

@main.route("/invalidate_user/<int:user_id>", methods=['POST'])
def invalidate_user(user_id):
    user = ServiceProfessional.query.get(user_id)
    if user:
        user.is_verified = False
        user.date_verified=None
        db.session.commit()
    return redirect(url_for('main.sps'))

@main.route("/block_customer/<int:customer_id>", methods=['POST'])
def block_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if customer:
        customer.is_blocked = True
        db.session.commit()
    return redirect(url_for('main.customers'))

@main.route("/unblock_customer/<int:customer_id>", methods=['POST'])
def unblock_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if customer:
        customer.is_blocked = False
        db.session.commit()
    return redirect(url_for('main.customers'))

@main.route("/block_sp/<int:sp_id>", methods=['POST'])
def block_sp(sp_id):
    sp = ServiceProfessional.query.get(sp_id)
    if sp:
        sp.is_blocked = True
        db.session.commit()
    return redirect(url_for('main.sps'))

@main.route("/unblock_sp/<int:sp_id>", methods=['POST'])
def unblock_sp(sp_id):
    sp = ServiceProfessional.query.get(sp_id)
    if sp:
        sp.is_blocked = False
        db.session.commit()
    return redirect(url_for('main.sps'))

@main.route("/create_services/<int:id>", methods=['GET', 'POST'])
def createservices(id=0):
    if 'email' in session and session['role'] == 'admin':
        sr = db.session.query(Service, ServiceProfessional).join(ServiceProfessional, ServiceProfessional.email == Service.provider).all()
        if request.method == 'GET':
            return render_template('createservices.html', srv=sr)
        elif request.method == 'POST':
            srv1 = Service.query.filter_by(id=id).first()
            if srv1:
                if srv1.status != 'Approved':
                    srv1.status = 'Approved'
                else:
                    srv1.status = 'Disapproved'
                
                db.session.commit()
            return redirect(url_for('main.createservices',id=0))
    return redirect(url_for('main.login'))

@main.route('/notifysp/<string:email>',methods=['POST'])
def notifysp(email):
    subject = 'Profile Incomplete'
    message = 'Dear Service Professional, We have received a new service verification request from you. But it seems that your profile is not complete yet. We recommend you to complete your profile first.'
    query = UserQuery(sender_email='Admin',subject=subject,message=message,sender_role='Admin',receiver_email=email)
    db.session.add(query)
    db.session.commit()
    return redirect(url_for('main.createservices',id=0))









#Customer Routes
@main.route("/customer_dashboard", methods=['GET', 'POST'])
def customerdb():
    if session.get('role') == 'customer':
        customer=sp=Customer.query.filter_by(email=session['email']).first()
        if sp.is_blocked:
            return redirect(url_for('main.blocked'))
        if 'email' not in session and request.method == 'GET':
            return redirect(url_for('main.login'))

        elif request.method == 'POST':
            session['email'] = request.form.get('loginemail')

        complete = ServiceRequest.query.filter(
            and_(
                ServiceRequest.customer_id == sp.id,
                ServiceRequest.service_status == 'Completed'
            )
        ).all()

        requested = ServiceRequest.query.filter(
            and_(
                ServiceRequest.customer_id == sp.id,
                ServiceRequest.service_status == 'Requested'
            )
        ).all()

        accepted = ServiceRequest.query.filter(
            and_(
                ServiceRequest.customer_id == sp.id,
                ServiceRequest.service_status == 'Accepted'
            )
        ).all()
        values = [len(requested), len(accepted), len(complete)]

        top_sps = (
        db.session.query(
            ServiceProfessional.name,
            func.count(ServiceRequest.id).label('request_count')
        )
        .join(ServiceRequest, ServiceRequest.professional_id == ServiceProfessional.id)
        .join(Service, Service.id == ServiceRequest.service_id)
        .filter(
            and_(
                ServiceRequest.customer_id == sp.id,
                Service.rating > 0
            )
        )
        .group_by(ServiceProfessional.id)
        .order_by(func.count(ServiceRequest.id).desc())
        .limit(3)
        .all()
        )


        return render_template('customerdb.html',c=customer,complete=False,values=values,top_sps=top_sps)
    return redirect(url_for('main.roleselect'))

@main.route('/complete_customer_profile',methods=['GET', 'POST'])
def complete_customer_profile():
    if 'email' in session and session['role'] == 'customer':
        c = Customer.query.filter_by(email=session['email']).first()

        if request.method == 'GET':
            return render_template('customerdb.html',c=c,complete=True)

        elif request.method == 'POST':
            if c:
                if not c.address:
                    c.address = request.form.get('customeraddress')
                if not c.ph:
                    c.ph = request.form.get('customerph')
                db.session.commit()
                return redirect(url_for('main.customerdb'))
    return redirect(url_for('main.login'))

@main.route("/services", methods=['GET', 'POST'])
def services():
    if 'email' in session and session['role'] == 'customer':
        customer_email = session['email']
        customer = Customer.query.filter_by(email=customer_email).first()
        
        sr = db.session.query(Service, ServiceProfessional).join(ServiceProfessional, ServiceProfessional.email == Service.provider).all()
        active_requests = ServiceRequest.query.filter_by(customer_id=customer.id).filter(ServiceRequest.service_status != 'Completed').all()
        active_service_ids = [req.service_id for req in active_requests]
        active_requests = ServiceRequest.query.filter_by(customer_id=customer.id).filter(ServiceRequest.payment_status == 'pending').all()
        active_service_ids1 = [req.service_id for req in active_requests]
        active_service_ids.extend(active_service_ids1)
        
        return render_template('services.html', service=sr, active_service_ids=active_service_ids)
    return redirect(url_for('main.login'))


@main.route('/service_list')
def service_list():
    if 'email' in session and session['role']=='customer':
        search_query = request.args.get('search', '').lower()
    
        if search_query:
            filtered_services = db.session.query(Service, ServiceProfessional).join(
                ServiceProfessional, ServiceProfessional.email == Service.provider
            ).filter(
                (Service.name.ilike(f'%{search_query}%')) |
                (Service.description.ilike(f'%{search_query}%')) |
                (ServiceProfessional.name.ilike(f'%{search_query}%')) |
                (ServiceProfessional.address.ilike(f'%{search_query}%')) |
                (Service.provider.ilike(f'%{search_query}%'))
            ).all()
        else:
            filtered_services = db.session.query(Service, ServiceProfessional).join(
                ServiceProfessional, ServiceProfessional.email == Service.provider
            ).all()

        return render_template('services.html', service=filtered_services)
    return redirect(url_for('main.login'))

@main.route('/request_service/<int:id>')
def requestservice(id):
    customer=Customer.query.filter_by(email=session['email']).first()
    sr = db.session.query(ServiceProfessional, Service)\
    .join(Service, ServiceProfessional.email == Service.provider)\
    .filter(Service.id == id)\
    .all()

    cid=customer.id

    for sp,srv in sr:
        sid=srv.id
        sp_id=sp.id
        sp_name=sp.name
        srv_name=srv.name
        offered_amount=srv.price
    remarks = f'Hi {sp_name}, I am interested in your {srv_name} service. Can you please accept my request?'
    new_req=ServiceRequest(service_id=sid,customer_id=cid,professional_id=sp_id,remarks=remarks,offered_amount=offered_amount)
    db.session.add(new_req)
    db.session.commit()

    return redirect(url_for('main.services'))

@main.route("/my_requests", methods=['GET', 'POST'])
def my_requests():
    if 'email' in session and session['role'] == 'customer':
        customer_email = session['email']
        customer = Customer.query.filter_by(email=customer_email).first()

        service_requests = db.session.query(ServiceRequest, Service, ServiceProfessional)\
            .join(Service, Service.id == ServiceRequest.service_id)\
            .join(ServiceProfessional, ServiceProfessional.id == ServiceRequest.professional_id)\
            .filter(ServiceRequest.customer_id == customer.id).all()

        return render_template('my_requests.html', requests=service_requests)
    return redirect(url_for('main.login'))


@main.route("/cancel_request/<int:request_id>", methods=['POST'])
def cancel_request(request_id):
    if 'email' in session and session['role'] == 'customer':
        service_request = ServiceRequest.query.get(request_id)
        
        if service_request and service_request.customer_id == Customer.query.filter_by(email=session['email']).first().id:
            db.session.delete(service_request)
            db.session.commit()
        
        return redirect(url_for('main.my_requests'))
    return redirect(url_for('main.login'))

@main.route('/service_details/<int:id>')
def servicedetails(id):
    if 'email' in session and session['role'] == 'customer':
        sr = db.session.query(ServiceProfessional, Service)\
            .join(ServiceProfessional, ServiceProfessional.email == Service.provider)\
            .filter(Service.id == id)\
            .first()
        
        customer = Customer.query.filter_by(email=session['email']).first()
        active_requests = ServiceRequest.query.filter_by(customer_id=customer.id).filter(ServiceRequest.service_status != 'Completed').all()
        active_service_ids = [req.service_id for req in active_requests]
        active_requests = ServiceRequest.query.filter_by(customer_id=customer.id).filter(ServiceRequest.payment_status == 'pending').all()
        active_service_ids1 = [req.service_id for req in active_requests]
        active_service_ids.extend(active_service_ids1)
        return render_template ('service_details.html',sd=sr,active_service_ids=active_service_ids)
    return redirect(url_for('main.roleselect'))

@main.route('/negotiate/<int:id>', methods=['POST','GET'])
def negotiate(id):
    if 'email' in session and session['role'] == 'customer':
        if request.method=='GET':
            sr = db.session.query(ServiceProfessional, Service)\
            .join(ServiceProfessional, ServiceProfessional.email == Service.provider)\
            .filter(Service.id == id)\
            .first()

            return render_template ('negotiate.html',sd=sr)
        elif request.method=='POST':


            customer=Customer.query.filter_by(email=session['email']).first()
            sr = db.session.query(ServiceProfessional, Service)\
            .join(Service, ServiceProfessional.email == Service.provider)\
            .filter(Service.id == id)\
            .all()

            cid=customer.id

            for sp,srv in sr:
                sid=srv.id
                sp_id=sp.id
                sp_name=sp.name
                srv_name=srv.name
                offered_amount=request.form.get('new_price')
            remarks = f'Hi {sp_name}, I am interested in your {srv_name} service. Can you please accept my request?'
            new_req=ServiceRequest(service_id=sid,customer_id=cid,professional_id=sp_id,remarks=remarks,offered_amount=offered_amount)
            db.session.add(new_req)
            db.session.commit()
            
            return redirect(url_for('main.services',id=id))
    return redirect(url_for('main.roleselect'))

@main.route('/complete_payment/<int:id>', methods=['GET', 'POST'])
def complete_payment(id):
    if 'email' in session and session['role']=='customer':
        sr = ServiceRequest.query.filter_by(id=id).first()
        if request.method=='POST':
            sr.payment_status = 'Payment Complete'
            srv = Service.query.filter_by(id=sr.service_id).first()
            srv.rating += int(request.form.get('rating'))
            srv.rating_count += 1
            db.session.commit()
            return redirect(url_for('main.my_requests'))

        elif request.method=='GET':
            sp=ServiceProfessional.query.filter_by(id=sr.professional_id).first()
            return render_template('complete_payment.html',sp=sp,sr=sr)
    











#Service Professional Routes
@main.route("/service_professional_dashboard", methods=['GET', 'POST'])
def spdb(editing_service=False):
    if session.get('role') == 'service professional':
        sp = ServiceProfessional.query.filter_by(email=session['email']).first()
        
        if sp.is_blocked:
            return redirect(url_for('main.blocked'))
        
        if 'email' not in session and request.method == 'GET':
            return redirect(url_for('main.login'))

        elif request.method == 'POST':
            session['email'] = request.form.get('loginemail')

        service_p = ServiceProfessional.query.filter_by(email=session['email']).first()
        srv = Service.query.filter_by(provider=session['email']).first()

        complete = ServiceRequest.query.filter(
            and_(
                ServiceRequest.professional_id == sp.id,
                ServiceRequest.service_status == 'Completed'
            )
        ).all()

        requested = ServiceRequest.query.filter(
            and_(
                ServiceRequest.professional_id == sp.id,
                ServiceRequest.service_status == 'Requested'
            )
        ).all()

        accepted = ServiceRequest.query.filter(
            and_(
                ServiceRequest.professional_id == sp.id,
                ServiceRequest.service_status == 'Accepted'
            )
        ).all()

        values = [len(requested), len(accepted), len(complete)]

        top_customers = (
            db.session.query(
                Customer.name,
                func.count(ServiceRequest.id).label('request_count')
            )
            .join(ServiceRequest, ServiceRequest.customer_id == Customer.id)
            .group_by(Customer.id)
            .filter_by(professional_id = service_p.id)
            .order_by(func.count(ServiceRequest.id).desc())
            .limit(3)
            .all()
        )

        top_customers_labels = [customer.name for customer in top_customers]
        top_customers_counts = [customer.request_count for customer in top_customers]

        
        return render_template(
            'spdb.html',
            sp=service_p, 
            service=srv, 
            editing_service=editing_service,
            complete=False, 
            values=values, 
            top_customers=top_customers
        )
    
    return redirect(url_for('main.roleselect'))

@main.route("/add_service",methods=['GET','POST'])
def addservice():
    if 'email' in session and session['role']=='service professional':
        sp = ServiceProfessional.query.filter_by(email=session['email'])
        if sp:
            provider=session['email']
            name=request.form.get('serviceName')
            price=request.form.get('price')
            time=request.form.get('time')
            description=request.form.get('description')
            new_service = Service(provider=provider,name=name,price=price,time_required=time,description=description)
            db.session.add(new_service)
            db.session.commit()
            return redirect(url_for('main.spdb'))
    return redirect(url_for('main.login'))

@main.route("/edit_service",methods=['GET','POST'])
def editservice():
    if 'email' in session and session['role']=='service professional':
        if request.method=='GET':
            service_p = ServiceProfessional.query.filter_by(email=session['email']).first()
            srv = Service.query.filter_by(provider=session['email']).first()
            return render_template('spdb.html', sp=service_p, service=srv, editing_service=True,complete=False)

        if request.method=='POST':
            service_p = ServiceProfessional.query.filter_by(email=session['email']).first()
            srv = Service.query.filter_by(provider=session['email']).first()

            if srv:
                srv.name = request.form.get('serviceName')
                srv.price = request.form.get('price')
                srv.time_required = request.form.get('time')
                srv.description = request.form.get('description')
                db.session.commit()
                return redirect(url_for('main.spdb'))
            
    return redirect(url_for('main.login'))

@main.route('/discontinue_service/<string:sp_id>', methods=['GET', 'POST'])
def discontinueservice(sp_id):
    srv = Service.query.filter_by(provider=sp_id).first()
    
    if srv:
        service_requests = ServiceRequest.query.filter_by(service_id=srv.id).all()
        
        for request in service_requests:
            db.session.delete(request)
        
        db.session.delete(srv)
        db.session.commit()

        return redirect(url_for('main.spdb'))
    
    return redirect(url_for('main.spdb'))

@main.route('/complete_sp_profile', methods=['GET', 'POST'])
def completespprofile():
    if 'email' in session and session['role'] == 'service professional':
        service_p = ServiceProfessional.query.filter_by(email=session['email']).first()
        srv = Service.query.filter_by(provider=session['email']).first()

        if request.method == 'GET':
            return render_template('spdb.html', sp=service_p, service=srv, editing_service=False, complete=True)

        elif request.method == 'POST':
            if service_p:
                if not service_p.address:
                    service_p.address = request.form.get('spaddress')
                if not service_p.ph:
                    service_p.ph = request.form.get('spph')
                db.session.commit()
                return redirect(url_for('main.spdb'))
    return redirect(url_for('main.login'))

@main.route('/service_requests', methods=['GET', 'POST'])
def servicerequests():
    if session['role'] == 'service professional':
        sp = ServiceProfessional.query.filter_by(email=session['email']).first()

        sr = db.session.query(ServiceRequest, Customer, Service)\
            .join(Customer, ServiceRequest.customer_id == Customer.id)\
            .join(Service, ServiceRequest.service_id == Service.id)\
            .filter(ServiceRequest.professional_id == sp.id)\
            .all()

        return render_template('servicerequests.html', sr=sr, sp=sp)
    return redirect(url_for('main.roleselect'))

@main.route('/accept_request/<int:id>',methods=['POST'])
def accept_request(id):
    if 'email' in session and session['role']=='service professional':
        sr=ServiceRequest.query.filter_by(id=id).first()
        sr.service_status='Accepted'
        db.session.commit()
        sp=ServiceProfessional.query.filter_by(email=session['email']).first()

        s=Service.query.filter_by(id=sr.service_id).first()
        
        c=Customer.query.filter_by(id=sr.customer_id).first()

        sender_email=session['email']
        receiver_email=c.email
        subject='Service requested accepted !'
        sender_role=session['role']
        message = f"Dear {c.name},\n\nWe are pleased to inform you that your request for the {s.name} has been accepted. We will get in touch with you shortly to finalize the details and schedule.\n\nThank you for choosing our service!\n\nBest regards,\n{sp.name}"
        notify=UserQuery(sender_email=sender_email,subject=subject,message=message,sender_role=sender_role,receiver_email=receiver_email)
        db.session.add(notify)
        db.session.commit()

        return redirect(url_for('main.servicerequests'))
    return redirect(url_for('main.roleselect'))


@main.route('/decline_request/<int:id>',methods=['POST'])
def decline_request(id):
    
    if 'email' in session and session['role']=='service professional':
        sr=ServiceRequest.query.filter_by(id=id).first()
        
        sp=ServiceProfessional.query.filter_by(email=session['email']).first()

        s=Service.query.filter_by(id=sr.service_id).first()
        
        c=Customer.query.filter_by(id=sr.customer_id).first()

        sender_email=session['email']
        receiver_email=c.email
        subject='Service requested denied !'
        sender_role=session['role']
        message = f"Dear {c.name},\n\nWe regret to inform you that, unfortunately, we are unable to accept your request for the {s.name} at this time. We apologize for any inconvenience caused and appreciate your understanding. Please feel free to reach out if you have any other queries or need assistance with other services.\n\nThank you for considering us.\n\nBest regards,\n{sp.name}"
        notify=UserQuery(sender_email=sender_email,subject=subject,message=message,sender_role=sender_role,receiver_email=receiver_email)
        db.session.add(notify)
        db.session.delete(sr)
        db.session.commit()

        return redirect(url_for('main.servicerequests'))
    return redirect(url_for('main.roleselect'))

@main.route('/sp_negotiate/<int:id>', methods=['POST', 'GET'])
def spnegotiate(id):
    if 'email' in session and session['role'] == 'service professional':
        if request.method == 'GET':
            sr = db.session.query(ServiceRequest, Service)\
                .join(Service, ServiceRequest.service_id == Service.id)\
                .filter(ServiceRequest.id == id)\
                .first()

            if sr is None:
                return "Service Request not found", 404

            return render_template('sp_negotiation.html', sd=sr)
        
        elif request.method == 'POST':
            sr = db.session.query(ServiceRequest, Customer, Service)\
                .join(Customer, ServiceRequest.customer_id == Customer.id)\
                .join(Service, ServiceRequest.service_id == Service.id)\
                .filter(ServiceRequest.id == id)\
                .first()

            if sr is None:
                return "Service Request not found"

            sr.ServiceRequest.offered_amount = request.form.get('new_price')
            sr.ServiceRequest.service_status = 'Accepted'

            sp = ServiceProfessional.query.filter_by(email=session['email']).first()
            subject = 'Response to Your Negotiation Request'
            message = f"Hi {sr.Customer.name},\n\nThanks for choosing our service. We noticed you've offered an amount of {sr.ServiceRequest.offered_amount}, but unfortunately, we couldn't manage to agree at that price. We would be happy to provide the service at {request.form.get('new_price')}.\n\nBest regards,\n{sp.name}"
            
            notify = UserQuery(sender_email=sp.email, subject=subject, message=message, sender_role=session['role'], receiver_email=sr.Customer.email)
            db.session.add(notify)
            
            db.session.commit()
            
            return redirect(url_for('main.servicerequests'))
    return redirect(url_for('main.roleselect'))



@main.route('/mark_complete/<int:id>', methods=['POST', 'GET'])
def mark_complete(id):
    if 'email' in session and session['role'] == 'service professional':
        sr = ServiceRequest.query.filter_by(id=id).first()
        srv=Service.query.filter_by(id=sr.service_id).first()
        c = Customer.query.filter_by(id=sr.customer_id).first()
        subject = 'Service Completed'
        message = f'Dear {c.name}, we have completed your service request of {srv.name} please complete the further steps as well. Thanks for chosing us.'
        query = UserQuery(sender_email=session['email'],subject=subject,message=message,sender_role=session['role'],receiver_email=c.email)
        db.session.add(query)


        sr.service_status = 'Completed'
        sr.date_of_completion = datetime.utcnow()
        db.session.commit()
        return redirect(url_for('main.servicerequests'))
    return redirect(url_for('main.roleselect'))

