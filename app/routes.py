from flask import Flask, request, jsonify, make_response,send_file,render_template
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
from app import app, db, api, mail
from flask_restful import Resource
from app.models import User, SentEmail
import traceback
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required
)

from flask_mail import Mail, Message

base_url = 'https://0872-2405-201-401f-1161-9046-94cf-85-c7ff/'




@app.route("/mails_sent", methods=["GET"])
@jwt_required()
def mails_sent():
    current_user = get_jwt_identity()
    user:User = User.query.filter(User.id == current_user).first()
    if not user.jwt_token:
        return make_response(jsonify({'message' :'Logged Out'}),200)
    response_data = []
    sent_mails:SentEmail = SentEmail.query.filter(SentEmail.user_id == current_user ).all()
    for sent_mail in sent_mails:
        data = {
            'subject':sent_mail.subject,
            'body': sent_mail.body,
            'received_time':sent_mail.sent_time
        }
        response_data.append(data)
    return make_response(jsonify({'data' :response_data}),200)

   
@app.route("/logout", methods=["GET"])
@jwt_required()
def logout():
    current_user = get_jwt_identity()
    try:
        User.query.filter(User.id == current_user).update({"jwt_token":None}, False)
        return make_response(jsonify({"message":"Logged Out"}), 200)
    except:
        print(traceback.format_exc())
        return make_response(jsonify({"message":"Some Error occured"}), 400)



@app.route("/image", methods=["GET"])
def render_image():
    mailID = int(request.args.get('type'))

    sent_email = SentEmail.query.filter(SentEmail.id == mailID).first()

    if sent_email:
        sent_email.received = True
        try:
            db.session.commit()
        except:
            print(traceback.format_exc())
    print("Mail Id", mailID)

    return send_file('news.png', mimetype='image/gif')




@app.route("/mail", methods=["GET"])
def send_daily_mail():
   
   # html = '''
    # <html>
    #     <body>
    #         <h1>Daily S&P 500 prices report</h1>
    #         <p>Hello, welcome to your report!</p>
    #     </body>
    # </html>
    # '''
    users:User = User.query.all()
    for user in users:
        failed = False
        print(user)
        sent_email = SentEmail()
        sent_email.user_id = user.id
        sent_email.subject = 'Tech Blog'
        sent_email.body = f'<img src={base_url}image?type={user.id}></img>'
        sent_email.sent_time = datetime.utcnow()

        try:
            db.session.add(sent_email)
            db.session.flush()
            mail_id = sent_email.id
            print(mail_id)
            db.session.commit()
        except:
            db.session.rollback()
            print(traceback.format_exc())
            failed = True
        
        
        if not failed:
            print("sss")
            context={
                "image": f'{base_url}image?type={mail_id}'
                }
            msg = Message(
                        'Tech Blog',
                        sender = 'mailsendertestdaily@gmail.com',
                        recipients = [user.email],
                        extra_headers={'Disposition-Notification-To': "chaturvedi.sshubhangi@gmail.com"}
                    )
            msg.html = render_template('template.html',**context)
            # msg.body = f'<img src={base_url}image?type={user.id}></img>'
            mail.send(msg)

    return make_response(jsonify({'data' :'Hello'}),200)




class Signup(Resource):
    def post(self):
        data = request.json
        print(data)

        if 'name' not in data or 'email' not in data or 'password' not in data:
            return make_response(jsonify({"message": "Missing parameters"}), 400)

        existing_user = User.query.filter(User.email == data['email']).first()
        if existing_user:
            return make_response(jsonify({"message": "User Exists with this email"}), 400)

        hashed_password = generate_password_hash(data['password'], method='sha256')
        new_user = User(public_id=str(uuid.uuid4()), name=data['name'], email = data['email'],password=hashed_password, admin=False)

        try:
            db.session.add(new_user)
            db.session.commit()
            return make_response(jsonify({"message": "New user Created Successfully"}), 200)
        except:
            db.session.rollback()
            print(traceback.format_exc())
            return make_response(jsonify({"message": "Some error occured,Please Try later"}), 500)


class userLogin(Resource):
    def post(self):
        data = request.json

        if 'email' not in data or 'password' not in data:
            return make_response(jsonify({"message": "Missing parameters"}), 400)
        
        user = User.query.filter(User.email == data['email']).first()

        if not user:
            return make_response(jsonify({"message": "No User With the given email"}), 400)

        if check_password_hash(user.password, data['password']):
            access_token = create_access_token(identity=user.id, fresh=True)
            User.query.filter(User.email == data['email']).update({"jwt_token":access_token},False)
            try:
                db.session.commit()
            except:
                print(traceback.format_exc())
            refresh_token = create_refresh_token(user.id)
            return make_response(jsonify( {
                'access_token': access_token,
                'is_admin': user.admin
            }), 200)

        return make_response(jsonify({"message": "Invalid credentials"}), 400)



@app.route("/mail-analytics", methods=["GET"])
@jwt_required()
def mail_analytics():
    sent_mails = SentEmail.query.all()
    response_data = {
        'opened_mails':[],
        'not_opened_mails':[],
        'received_count':0,
        'not_received_count':0

    }
    for sent_mail in sent_mails:
        user_name:User = User.query.filter(User.id == sent_mail.user_id).with_entities(User.name).first()
        data = {
            'subject': sent_mail.subject,
            'body': sent_mail.body,
            'sent_time': sent_mail.sent_time,
            'user_name': user_name.name
        }
        if sent_mail.received:
            response_data['opened_mails'].append(data)
            response_data['received_count']+= 1

        else:
            response_data['not_opened_mails'].append(data)
            response_data['not_received_count']+= 1

    
    return make_response(jsonify(
                                {'opened_mails': response_data['opened_mails'],
                                    'not_opened_mails': response_data['not_opened_mails'],
                                    'data_breakup':[
                                      {
                                        'name': 'Not Received/Opened Mails',
                                       'value':  response_data['received_count']
                                       },
                                      {
                                       'name': 'Received/Opened Mails',
                                       'value': response_data['not_received_count']
                                      }
                                  ]}), 200)

    
api.add_resource(Signup,'/signup')
api.add_resource(userLogin,'/login')