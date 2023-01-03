from flask_mail import Mail, Message
from app import mail,db, app,crontab
from app.models import User,SentEmail
from datetime import datetime
import traceback
from flask import render_template



base_url = 'Your base url'


@crontab.job(minute="30", hour="6", day="*", month="*", day_of_week="*")
def send_daily_mail():
   
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
            db.session.commit()
        except:
            db.session.rollback()
            print(traceback.format_exc())
            failed = True
        
        
        if not failed:

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
            mail.send(msg)
            print("Mail Sent For the User---",user.id)
    
        
