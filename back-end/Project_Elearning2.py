from asyncio import run
from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import requests, base64
from flask_cors import CORS, cross_origin
import jwt
import datetime as dt


app = Flask(__name__)
db = SQLAlchemy(app)
CORS (app, supports_credentials=True)

app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:serenade@localhost:5432/Project_Elearning?sslmode=disable'

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, index=True)
    fullname = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)
    coursestatus = db.relationship('Transaction', backref='userrel', lazy='dynamic')

class Teacher(db.Model):
    teacher_id = db.Column(db.Integer, primary_key=True, index=True)
    fullname = db.Column(db.String(40), nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)

class Course(db.Model):
    course_id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String())
    institution = db.Column(db.String(20))
    level = db.Column(db.String(20))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.teacher_id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.subject_id'))
    coursestatus = db.relationship('Transaction', backref='courserel', lazy='dynamic')
    precourse_id = db.Column(db.Integer, nullable=True)

class Subject(db.Model):
    subject_id = db.Column(db.Integer, primary_key=True, index=True)
    subject_name = db.Column(db.String(255), nullable=False)
    course = db.relationship('Course', backref='subjectrel', lazy='dynamic')

class Prerequisite(db.Model):
    prerequisite_id = db.Column(db.Integer, primary_key=True, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)
    precourse_id = db.Column(db.Integer, db.ForeignKey('course.course_id'))

class Status(db.Model):
    status_id = db.Column(db.Integer, primary_key=True, index=True)
    status = db.Column(db.String(20))
    coursestatus = db.relationship('CourseStatus', backref='statusrel', lazy='dynamic')

class CourseStatus(db.Model):
    coursestatus_id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'))
    status_id = db.Column(db.Integer, db.ForeignKey('status.status_id'))

class Transaction(db.Model):
    coursestatus_id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.course_id'))
    status_id = db.Column(db.Integer, db.ForeignKey('status.status_id'))




db.create_all()
db.session.commit()

@app.route('/')
def home():
    return {
        'message' : 'Welcome to Coursela' 
    }

def BasicAuth() :
    pass_str = request.headers.get('Authorization')
    pass_bersih = pass_str.replace('Basic',"")
    hasil_decode = base64.b64decode(pass_bersih)
    hasil_decode_bersih = hasil_decode.decode('utf-8')
    username_aja = hasil_decode_bersih.split(":")[0]
    pass_aja = hasil_decode_bersih.split(":")[1]
    arr = []
    nama = User.query.filter_by(username=username_aja, password=pass_aja).first()
    if nama:
        arr = [nama.username, nama.password, nama.fullname, nama.user_id, "True", nama.email]
        return arr
    else:
        arr = ["False", "none"]
        return arr


def BasicAuth2() :
    pass_str = request.headers.get('Authorization')
    pass_bersih = pass_str.replace('Basic ',"")
    hasil_decode = base64.b64decode(pass_bersih)
    hasil_decode_bersih = hasil_decode.decode('utf-8')
    username_aja = hasil_decode_bersih.split(":")[0]
    pass_aja = hasil_decode_bersih.split(":")[1]
    arr = []
    nama2 = Teacher.query.filter_by(username=username_aja).filter_by(password=pass_aja).first()
    if nama2:
        arr = ["True", nama2.fullname, nama2.teacher_id, nama2.email, nama2.username, nama2.password]
        return arr
    else:
        arr = ["False", "none"]
        return arr 

@app.route('/signup', methods=['POST']) #register new user [DONE]
def create_user():
    data = request.get_json()
    b = User(
        fullname = data['fullname'],
        email = data['email'],
        username = data['username'],
        password = data['password']
    )

    # print(b)

    try:
        db.session.add(b)
        db.session.commit()
    except:
        return {
            'message' : "Gagal Menyimpan Data",
        }, 400
    return {
        'message' : "Data Berhasil Tersimpan"
        }, 201

#login user
@app.route('/login', methods=['POST'])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"], supports_credentials=True)
def login():
        # token = jwt.encode({
        #             'user': "idd",
        #             'passkey' : "pwd",
        #             'exp': 
        # datetime.now()
        # + dt.timedelta(hours=24)
        #             },'secret' ,algorithm='HS256'
        #             )
        # # response = make_response( render_template() ) 
        # # resp = make_response("token generated")
        # # resp.set_cookie('token',value=token,expires=datetime.now()+ dt.timedelta(hours=24), path='/',samesite='Lax',domain="127.0.0.1")
        # return {
        #     "token" : token 
        # }

        login = BasicAuth()
        uname = login[0]
        passw = login[1]
        email = login[5]
        fname = login[2]
        user_id = login[3]
        cek = User.query.filter_by(username=uname).filter_by(password=passw).first()
        if cek:
            # return "True"
            # jwt encode untuk meng-encode hasil inputan
            token = jwt.encode({
                    'user': uname,
                    'passkey' : passw,
                    'email' : email,
                    'fullname' : fname,
                    'user_id' : user_id
                    # 'exp': 
            # secret untuk melakukan encode, algorithm buat metode yang dipakai(format)
            # datetime.now()
            # + dt.timedelta(hours=24)
                    },'secret' ,algorithm='HS256'
                    )
            return {"token" : token,
                    "message" : "Success!"}
        else:
            return {"message" : "False"}

        # email = login[4]
        # password = login[3]
        # cek = User.query.filter_by(email=email, password=password).first()
        # if cek:
        #     return "True"
        # else:
        #     return "False"

@app.route('/login_teacher', methods=['POST'])
@cross_origin(origin="*", headers=["Content-Type", "Authorization"], supports_credentials=True)
def login2():
        # token = jwt.encode({
        #             'user': "idd",
        #             'passkey' : "pwd",
        #             'exp': 
        # datetime.now()
        # + dt.timedelta(hours=24)
        #             },'secret' ,algorithm='HS256'
        #             )
        # # response = make_response( render_template() ) 
        # # resp = make_response("token generated")
        # # resp.set_cookie('token',value=token,expires=datetime.now()+ dt.timedelta(hours=24), path='/',samesite='Lax',domain="127.0.0.1")
        # return {
        #     "token" : token 
        # }

        logint = BasicAuth2()
        unamet = logint[4]
        passwt = logint[5]
        emailt = logint[3]
        fnamet = logint[1]
        cek = Teacher.query.filter_by(username=unamet).filter_by(password=passwt).first()
        if cek:
            # return "True"
            # jwt encode untuk meng-encode hasil inputan
            tokent = jwt.encode({
                    'user': unamet,
                    'passkey' : passwt,
                    'email' : emailt,
                    'fullname' : fnamet
                    # 'exp': 
            # secret untuk melakukan encode, algorithm buat metode yang dipakai(format)
            # datetime.now()
            # + dt.timedelta(hours=24)
                    },'secret' ,algorithm='HS256'
                    )
            return {"token" : tokent,
                    "message" : "Success!"}
        else:
            return {"message" : "False"}

        # email = login[4]
        # password = login[3]
        # cek = User.query.filter_by(email=email, password=password).first()
        # if cek:
        #     return "True"
        # else:
        #     return "False"

#revisi: cuma bisa update data dirinya sendiri(sesuai login)
# @app.route('/user/<id>', methods=['PUT']) #update user data [DONE]
# def update_user(id):
#     login = BasicAuth()
#     r = login[0]
#     if r == "True":
#         user = User.query.get(id)
#         fullname = request.json['fullname'] 
#         email = request.json['email']
#         password = request.json['password']
#         user.fullname = fullname
#         user.email = email
#         user.password = password
#         try:
#             db.session.commit()
#         except:
#             return { 
#                     "Pesan" : "Gagal Memperbarui Data"
#                     }, 400
#         return {
#                     "Pesan" : "Berhasil Memperbarui Data"
#             }, 200

# @app.route('/user', methods=['PUT']) #update user data [DONE]
# def update_user():
#     login = BasicAuth()
#     ru = login[4]
#     useru = login[0]
#     passu = login[1]
#     emailu = login[5]
#     fnameu = login[2] 
#     if ru == "True":
#         user = User.query.filter_by(username=useru).filter_by(password=passu).first()
#         fullname = request.json['fullname'] 
#         email = request.json['email']
#         password = request.json['password']
#         username = request.json['useru']
#         user.fullname = fullname
#         user.email = email
#         user.password = password
#         user.username = username
#         try:
#             db.session.commit()
#         except:
#             return { 
#                     "Pesan" : "Gagal Memperbarui Data"
#                     }, 400
#         return {
#                     "Pesan" : "Berhasil Memperbarui Data"
#             }, 200

@app.route('/updateuser', methods=['PUT']) #update teacher data [DONE]
def update_user():
    login = BasicAuth()
    r = login[4]
    a = login[3]
    if r == "True":
        user = User.query.get(a)
        fullname = request.json['fullname']
        username = request.json['username']
        email = request.json['email']
        user.fullname = fullname
        user.email = email
        user.username = username
        try:
            db.session.commit()
        except:
            return { 
                    "Pesan" : "Gagal Memperbarui Data"
                    }, 400
        return {
                    "Pesan" : "Berhasil Memperbarui Data"
            }, 200

@app.route('/deleteuser', methods=['DELETE']) #delete user [DONE]
def delete_user():
    login = BasicAuth()
    r = login[4]
    a = login[2]
    if r == "True":
        try:
            b = User.query.filter_by(user_id=a).first()
            db.session.delete(b)
            db.session.commit()
        except:
            return {
                'message' : "Coba Lagi"
            }, 400
        return {
            'message' : "Berhasil, Hore!"
            }, 201

@app.route('/signup_teacher', methods=['POST']) #register teacher [DONE]
def signup_teacher():
    data = request.get_json()
    list = Teacher(
        fullname = data['fullname'],
        username = data['username'],
        email = data['email'],
        password = data['password']
    )
    try:
        db.session.add(list)
        db.session.commit()
    except:
        return {
            'message' : "Gagal Menyimpan Data"
        }, 400
    return {
        'message' : "Data Berhasil Tersimpan"
        }, 201

@app.route('/updateteacher', methods=['PUT']) #update teacher data [DONE]
@cross_origin(origin="*", headers=["Content-Type", "Authorization"], supports_credentials=True)
def update_teacher():
    login = BasicAuth2()
    r = login[0]
    a = login[2]
    if r == "True":
        teacher = Teacher.query.get(a)
        fullname = request.json['fullname'] 
        email = request.json['email']
        username = request.json['username']
        teacher.fullname = fullname
        teacher.email = email
        teacher.username = username
        try:
            db.session.commit()
        except:
            return { 
                    "Pesan" : "Gagal Memperbarui Data"
                    }, 400
        return {
                    "Pesan" : "Berhasil Memperbarui Data"
            }, 200

@app.route('/deleteteacher', methods=['DELETE']) #delete teacher [DONE]
def delete_teacher():
    login = BasicAuth2()
    r = login[0]
    a = login[2]
    if r == "True":
        try:
            b = Teacher.query.filter_by(teacher_id=a).first()
            db.session.delete(b)
            db.session.commit()
        except:
            return {
                'message' : "Coba Lagi"
            }, 400
        return {
            'message' : "Berhasil, Hore!"
            }, 201

@app.route('/subject', methods=['POST']) #create subject [DONE]
def create_subject():
    login = BasicAuth2()
    r = login[0]
    if r == "True":
        data = request.get_json()
        b = Subject(
        subject_name = data['subject_name']
    )
    try:
        db.session.add(b)
        db.session.commit()
    except:
        return {
            'message' : "Gagal Menyimpan Data"
        }, 400
    return {
        'message' : "Data Berhasil Tersimpan"
        }, 201

@app.route('/updatesubject/<id>', methods=['PUT']) #update subject [DONE]
def update_subject(id):
    login = BasicAuth2()
    r = login[0]
    if r == "True":
        subject = Subject.query.get(id)
        subject_name = request.json['subject_name'] 
        subject.subject_name = subject_name
        try:
            db.session.commit()
        except:
            return { 
                    "Pesan" : "Gagal Memperbarui Data"
                    }, 400
        return {
                    "Pesan" : "Berhasil Memperbarui Data"
            }, 200

@app.route('/deletesubject/<id>', methods=['DELETE']) #delete subject [DONE]
def delete_subject(id):
    login = BasicAuth2()
    r = login[0]
    if r == "True":
        try:
            b = Subject.query.filter_by(subject_id=id).first()
            db.session.delete(b)
            db.session.commit()
        except:
            return {
                'message' : "Coba Lagi"
            }, 400
        return {
            'message' : "Berhasil, Hore!"
            }, 201

@app.route('/course', methods=['POST']) #create new course [DONE]
def create_course():
    login = BasicAuth2()
    r = login[0]
    if r == "True":
        data = request.get_json()
        b = Course(
            name = data['name'],
            description = data['description'],
            institution = data['institution'],
            level = data['level'],
            teacher_id = login[2],
            subject_id = data['subject_id'],
            precourse_id = data['precourse']
        )

        try:
            db.session.add(b)
            db.session.commit()
        except:
            return {
                'message' : "Gagal Menyimpan Data"
            }, 400
        return {
            'message' : "Data Berhasil Tersimpan"
            }, 201

@app.route('/updatecourse/<id>', methods=['PUT']) #update course data [DONE]
def update_course(id):
    login = BasicAuth2()
    r = login[0]
    if r == "True":
        course = Course.query.get(id)
        name = request.json['name'] 
        description = request.json['description']
        institution = request.json['institution']
        level = request.json['level']
        subject_id = request.json['subject_id']
        precourse = request.json['precourse']
        course.name = name
        course.description = description
        course.institution = institution
        course.level = level
        course.subject_id = subject_id
        precourse = precourse
        try:
            db.session.commit()
        except:
            return { 
                    "Pesan" : "Gagal Memperbarui Data"
                    }, 400
        return {
                    "Pesan" : "Berhasil Memperbarui Data"
            }, 200

# @app.route('/updatecourse/<id>', methods=['PUT']) #update course data [DONE]
# def update_course(id):
#     login = BasicAuth2()
#     r = login[5]
#     if r == "True":
#         course = Course.query.filter_by(course_id=id).first()
#         # name = request.json['name'] 
#         # description = request.json['description']
#         # institution = request.json['institution']
#         # level = request.json['level']
#         # subject_id = request.json['subject_id']
#         # precourse = request.json['precourse_id']
#         # course.name = name
#         # course.description = description
#         # course.institution = institution
#         # course.level = level
#         # course.subject_id = subject_id
#         # precourse = precourse
#         try:
#             db.session.commit()
#         except:
#             return { 
#                     "Pesan" : "Gagal Memperbarui Data"
#                     }, 400
#         return {
#                     "Pesan" : course.course_id
#             }, 200

@app.route('/deletecourse/<id>', methods=['DELETE']) #delete course [DONE]
def delete_course(id):
    login = BasicAuth2()
    r = login[0]
    if r == "True":
        try:
            b = Course.query.filter_by(course_id=id).first()
            db.session.delete(b)
            db.session.commit()
        except:
            return {
                'message' : "Coba Lagi"
            }, 400
        return {
            'message' : "Berhasil, Hore!"
            }, 201

@app.route('/prequisite', methods=['POST']) #post prequisite [DONE]
def create_prequisite():
    login = BasicAuth2()
    r = login[0]
    if r == "True":
        data = request.get_json()
        b = Prerequisite(
        course_id = data['course_id'],
        precourse_id = data['precourse_id']
    )
    try:
        db.session.add(b)
        db.session.commit()
    except:
        return {
            'message' : "Gagal Menyimpan Data"
        }, 400
    return {
        'message' : "Data Berhasil Tersimpan"
        }, 201

@app.route('/updatepre/<id>', methods=['PUT']) #put prequisite [DONE]
def update_prequisite(id):
    login = BasicAuth2()
    r = login[0]
    if r == "True":
        prequisite = Prerequisite.query.get(id)
        course_id = request.json['course_id']
        precourse_id = request.json['precourse_id'] 
        prequisite.course_id = course_id
        prequisite.precouse_id = precourse_id
        try:
            db.session.commit()
        except:
            return { 
                    "Pesan" : "Gagal Memperbarui Data"
                    }, 400
        return {
                    "Pesan" : "Berhasil Memperbarui Data"
            }, 200

@app.route('/deletepre/<id>', methods=['DELETE']) #delete prequisite [DONE]
def delete_pre(id):
    login = BasicAuth2()
    r = login[0]
    if r == "True":
        try:
            b = Prerequisite.query.filter_by(prerequisite_id=id).first()
            db.session.delete(b)
            db.session.commit()
        except:
            return {
                'message' : "Coba Lagi"
            }, 400
        return {
            'message' : "Berhasil, Hore!"
            }, 201

@app.route('/createstatus', methods=['POST']) #create status [DONE]
def create_status():
    login = BasicAuth2()
    r = login[0]
    if r == "True":
        data = request.get_json()
        b = Status(
            status = data['status']
        )
        try:
            db.session.add(b)
            db.session.commit()
        except:
            return {
                'message' : "Gagal Menyimpan Data"
            }, 400
    return {
        'message' : "Data Berhasil Tersimpan"
        }, 201

@app.route('/deletestatus/<id>', methods=['DELETE']) #delete status [DONE]
def delete_status(id):
    login = BasicAuth2()
    r = login[0]
    if r == "True":
        try:
            b = Status.query.filter_by(status_id=id).first()
            db.session.delete(b)
            db.session.commit()
        except:
            return {
                'message' : "Coba Lagi"
            }, 400
        return {
            'message' : "Berhasil, Hore!"
            }, 201

# @app.route('/enroll', methods=['POST'])
# def user_enroll():
#     login = BasicAuth()
#     data = request.get_json()
#     r = login[4]
#     if r == "True":
#             user = User.query.filter_by(fullname=login[2]).first()
#             course = Course.query.filter_by(course_id=data["course_id"]).first()
#             preq = Prerequisite.query.filter_by(course_id=course.course_id).all()
#             preq2 = Prerequisite.query.filter_by(course_id=course.course_id).count()
#             arr = []
#             a = Transaction.query.filter_by(user_id=user.user_id).filter_by(status_id=1).count()
#             if a >= 5:
#                 return "Gagal"
#             else:
#                 for i in preq:
#                     c = Transaction.query.filter_by(user_id=user.user_id).filter_by(course_id=i.precourse_id).first()
#                     if c.status_id == 3:
#                         arr.append(c.status_id)                
#                 if preq2 != len(arr):
#                     return "Belum Memenuhi Syarat"
#                 else:
#                     # status = Status.query.filter_by(status="Enrolled").first()
#                     b = Transaction(
#                     user_id = user.user_id,
#                     course_id = course.course_id,
#                     status_id = 1
#                     )
#                     db.session.add(b) 
#                     db.session.commit()
#                     return "Enrolled"
#     else :
#         return "Username/Password is incorrect"

@app.route('/enroll', methods=['POST'])
def user_enroll():
    login = BasicAuth()
    data = request.get_json()
    r = login[4]
    if r == "True":
            a = Transaction.query.filter_by(user_id=login[3]).filter_by(status_id=1).count()
            b = Transaction.query.filter_by(user_id=login[3]).filter_by(course_id=data['course_id']).first()
            preq = Course.query.filter_by(course_id=data['course_id']).first()
            if str(preq.precourse_id)=="None":
                if a >= 5:
                    return "Maximum course has been reached"
                if not b:
                    b=Transaction(
                        course_id = data['course_id'],
                        user_id = login[3],
                        status_id = 1
                    )
                    db.session.add(b) 
                    db.session.commit()
                    return "Enrolled"
                if b.status_id == 1:
                    return "Already enrolled"
                if b.status_id == 2:
                    return "You've completed the course"
            else:
                preq2 = Transaction.query.filter_by(user_id=login[3]).filter_by(course_id=preq.precourse_id).filter_by(status_id=2).first()
                # if not preq2:
                #     return "Belum memenuhi syarat"
                if preq2:
                    if a >= 5:
                        return "Maximum course has been reached"
                    if not b:
                        b=Transaction(
                            course_id = data['course_id'],
                            user_id = login[3],
                            status_id = 1
                        )
                        db.session.add(b) 
                        db.session.commit()
                        return "Enrolled"
                    if b.status_id == 1:
                        return "Already enrolled"
                    if b.status_id == 2:
                        return "You've completed the course"
                    
                # else:
                #     return "Bisa"
            # return str(preq.precourse_id)
            # if a >= 5:
            #     return "Maximum course has been reached"
            # if not b:
            #     b=Transaction(
            #         course_id = data['course_id'],
            #         user_id = login[3],
            #         status_id = 1
            #     )
            #     db.session.add(b) 
            #     db.session.commit()
            #     return "Enrolled"
            # if b.status_id == 1:
            #     return "Already enrolled"
            # if b.status_id == 2:
            #     return "You've completed the course"
    #         return str(a)
 
    # else:
    #     return "Username/Password is incorrect"


#revisi: gaboleh enroll lebih dari 1x di course yg sama (kalau mau, harus unenroll dulu)
# @app.route('/enroll', methods=['POST']) #enroll to course 
# def user_enroll():
#     login = BasicAuth()
#     data = request.get_json()
#     r = login[0]
#     if r == "True":
#             user = User.query.filter_by(fullname=login[1]).first()
#             course = Course.query.filter_by(name=data["name"]).first()
#             preq = Prerequisite.query.filter_by(course_id=course.course_id).all()
#             preq2 = Prerequisite.query.filter_by(course_id=course.course_id).count()
#             arr = []
#             a = CourseStatus.query.filter_by(user_id=user.user_id).filter_by(status_id=1).count()
#             # b = CourseStatus.query.filter_by(user_id=user.user_id).filter_by(status_id=1).first()
#             # c = CourseStatus.query.filter_by(user_id=user.user_id).filter_by(status_id=2).first()
#             # d = CourseStatus.query.filter_by(user_id=user.user_id).filter_by(status_id=3).first()
#             # if a == 0 :
#             if a >= 5:
#                 return "Gagal"
#             else:
#                 for i in preq:
#                     a = CourseStatus.query.filter_by(user_id=user.user_id).filter_by(course_id=i.precourse_id).first()
#                     if a.status_id == 3:
#                         arr.append(a.status_id)                
#                 if preq2 != len(arr):
#                     return "Belum Memenuhi Syarat"
#                 else:
#                     b = CourseStatus(
#                     user_id = user.user_id,
#                     course_id = course.course_id,
#                     status_id = 1
#                     )
#                     db.session.add(b) 
#                     db.session.commit()
#                     return "Enrolled"
#             # else:
#             #     return "Error"
#     else:
#         return "Username/Password is incorrect"

@app.route('/statuscourse/<id>', methods=['GET']) #get list of course and the status of user a
def statuscourse(id):
    user = User.query.filter_by(user_id=id).first()
    list = CourseStatus.query.filter_by(user_id=id).all() #dapat user id
    # course = Course.query.filter_by(course_id=list.course_id).all() #dpt course id
    return jsonify({
        "1_Nama" : user.fullname,
        "2_Courses" : [{
            "Course Name" : i.courserel.name,
            "Status" : i.statusrel.status
        } for i in list]
    })

@app.route('/subject', methods=['GET']) #get all subjects and the courses
def get_subject():  
    result = Subject.query.all()
    sub=[]
    for x in result:
        sub.append({
            "1_Name" : x.subject_name,
            "2_SubjectId" : x.subject_id,
            "3_Courses" : [{ 
                "Description" : y.description,
                "Nama" : y.name
            
                
            }for y in Course.query.filter_by(subject_id = x.subject_id).all()]
            })
    return jsonify(sub)

@app.route('/allcourse', methods=['GET'])
def allcourses():
    courses = Course.query.all()
    wadah=[]
    for x in courses:
        nm = Teacher.query.filter_by(teacher_id=x.teacher_id).first()
        wadah.append({
            "Course" : x.name,
            "ID" : x.course_id,
            "Teacher" : x.teacher_id,
            "Description" : x.description,
            "Institution" : x.institution,
            "Level" : x.level,
            "Subject" : x.subject_id,
            "Nama" : nm.fullname
        })
    return (wadah)

@app.route('/usercourse/<id>', methods=['GET'])
def usercourse(id):
    courses = Course.query.all()
    wadah=[]
    for x in courses:
        nm = Teacher.query.filter_by(teacher_id=x.teacher_id).first()
        trans = Transaction.query.filter_by(course_id=x.course_id).filter_by(user_id=id).first()
        if not trans:
            wadah.append({
                "Course" : x.name,
                "ID" : x.course_id,
                "Teacher" : x.teacher_id,
                "Description" : x.description,
                "Institution" : x.institution,
                "Level" : x.level,
                "Subject" : x.subject_id,
                "Nama" : nm.fullname,
                "Precourse" : x.precourse_id
            })
    return (wadah)


@app.route('/coursedetail/<id>', methods=['GET'])
def courseDetail(id):
    courses = Course.query.filter_by(course_id=id).first()
    if courses:
        return jsonify({
            "Course" : courses.name,
            "ID" : courses.course_id,
            "Teacher" : courses.teacher_id,
            "Description" : courses.description,
            "Institution" : courses.institution,
            "Level" : courses.level,
            "Subject" : courses.subject_id,
            "Precourse" : courses.precourse_id
        })
    else:
        return "Course is not founded"

@app.route('/search/course', methods=['POST']) #search course by name
def search_course():
    data = request.get_json()
    inputan = data['search']
    query_course = Course.query.filter(Course.name.ilike("%"+inputan+"%")).all()
    return jsonify([
        {
            "Course" : course.name,
            "Description" : course.description,
            "Institution" : course.institution, 
            "Level" : course.level,
            "ID" : course.course_id
        } for course in query_course
    ])

@app.route('/search/description', methods=['POST']) #search course by description
def search_desc():
    data = request.get_json()
    inputan = data['search']
    query_course = Course.query.filter(Course.description.ilike("%"+inputan+"%")).all()
    return jsonify([
        {
            "Course" : course.name,
            "Description" : course.description,
            "Institution" : course.institution, 
            "Level" : course.level,
            "ID" : course.course_id
        } for course in query_course
    ])

#search course by prequisite (jadi nanti tuh kalau misal kita ngetik Python nah course apa aja yang prequisite nya pake itu)
# @app.route('/search/prequisite', methods=['GET'])
# def search_pre():
#     data = request.get_json()
#     course_id = Course.query.filter_by(name=data['search']).first()
#     query_course = Prerequisite.query.filter_by(precourse_id=course_id.course_id).all()
#     arr = []
#     for i in query_course:
#         course = Course.query.filter_by(course_id=i.course_id).first()
#         arr.append( {
#             "Course" : course.name,
#             "Description" : course.description,
#             "Institution" : course.institution, 
#             "Level" : course.level
#         }
#         )
#     return jsonify(arr)

#complete course
@app.route('/completecourse/<id>', methods=['PUT'])
def completecourse(id):
    login = BasicAuth()
    r = login[4]
    if r == "True":
        complete = Transaction.query.filter_by(course_id=id).filter_by(user_id=login[3]).first()
        if complete:
            complete.status_id = 2
            db.session.commit()
            return {
                    "Message" : "Success"
                }, 201
        return {
                "Message" : "Error",
            }, 401

#unenroll from course
# @app.route('/unenroll/<id>', methods=['PUT'])
# def unenrollcourse(id):
#     login = BasicAuth()
#     r = login[0]
#     if r == "True":
#         unenroll = CourseStatus.query.filter_by(course_id=id).filter_by(user_id=login[2]).first()
#         if unenroll:
#             unenroll.status_id = 3
#             db.session.commit()
#             return {
#                     "Message" : "Success"
#                 }, 201
#         return {
#                 "Message" : "Error",
#             }, 401

#unenroll from course
@app.route('/unenroll/<id>', methods=['DELETE'])
def unenroll(id):
    login = BasicAuth()
    r = login[4]
    if r == "True":
        b = Transaction.query.filter_by(course_id=id).filter_by(user_id=login[3]).first()
        try:
            db.session.delete(b)
            db.session.commit()
        except:
            return {
                'message' : "Coba Lagi"
            }, 400
        return {
                'message' : "Berhasil, Hore!"
                }, 201

# #get list users enrolled to course
# @app.route('/totalenrolled/<id>', methods=['GET'])
# def totalenrolled(id):
#     coursename = Course.query.filter_by(course_id=id).first() #buat nampilin course
#     list = Transaction.query.filter_by(course_id=id).filter_by(status_id=1).all() #buat nampilin apa aja yang sedang dienroll
#     arr = []
#     judul = []
#     email = []
#     judul.append(coursename.name)
#     for i in list: #untuk mencari email yang meng-enroll si course itu
#         user = User.query.filter_by(user_id=i.user_id).first()
#         arr.append(user.fullname)
#         email.append(user.email)
  
#     return jsonify({
#         "Course Name" : judul[0],
#         "Student Name" : [{
#             "1.Nama" : arr[user],
#             "2.Email" : email[user]
#         } for user in range(len(arr))]
#     })




#get list users enrolled to course
# @app.route('/totalenrolled/<id>', methods=['GET'])
# def totalenrolled(id):
#     login = BasicAuth2()
#     teacher_id = login[2]
#     coursename = Course.query.filter_by(course_id=id).first() #buat nampilin course
#     list = Transaction.query.filter_by(course_id=id).filter_by(status_id=1).all() #buat nampilin apa aja yang sedang dienroll
#     arr = []
#     judul = []
#     email = []
#     judul.append(coursename.name)
#     for i in list: #untuk mencari email yang meng-enroll si course itu
#         user = User.query.filter_by(user_id=i.user_id).first()
#         arr.append(user.fullname)
#         email.append(user.email)
  
#     return jsonify({
#         "Course Name" : judul[0],
#         "Student Name" : [{
#             "1.Nama" : arr[user],
#             "2.Email" : email[user]
#         } for user in range(len(arr))]
#     })

#get list users enrolled to course
# @app.route('/totalenrolled', methods=['GET'])
# def totalenrolled():
#     login = BasicAuth2()
#     teacher_id = login[2]
#     coursename = Course.query.filter_by(teacher_id=teacher_id).all() #buat nampilin course
#     list = Transaction.query.filter_by(status_id=1).all() #buat nampilin apa aja yang sedang dienroll
#     arr = []
    # arr = []
    # judul = []
    # email = []
    # judul.append(coursename.name)
    # for i in list: #untuk mencari email yang meng-enroll si course itu
    #     user = User.query.filter_by(user_id=i.user_id).first()
    #     arr.append(user.fullname)
    #     email.append(user.email)
    # return jsonify({
    #     "Course Name" : judul[0],
    #     "Student Name" : [{
    #         "1.Nama" : arr[user],
    #         "2.Email" : email[user]
    #     } for user in range(len(arr))]
    # })

#get top 5 course
@app.route('/topcourse', methods=['GET'])
def topcourse():
    a = db.engine.execute("SELECT course_id, COUNT(course_id) as cid from transaction where status_id = 1 group by course_id order by cid desc limit 6")
    b = []
    c = []
    e = []
    for i in a:
        b.append(i.course_id)
        e.append(i.cid)
    for j in range(len(b)):
        d = Course.query.filter_by(course_id=b[j]).first()
        c.append({
            "Name" : d.name,
            "TotalEnrolled" : e[j],
            "ID" : d.course_id
            })
    return c
    
#get top 5 students
@app.route('/topstudents', methods=['GET'])
def topstudents():
    a = db.engine.execute("SELECT user_id, count(user_id) from transaction where status_id = 2 group by user_id order by count desc limit 5")
    b = []
    c = []
    e = []

    for i in a:
        b.append(i.user_id)
        c.append(i.count)
    for j in range(len(b)):
        d = User.query.filter_by(user_id=b[j]).first()
        e.append({
            "Name" : d.fullname,
            "TotalCompleted" : c[j]
        })
    # return [{"user_id": i.user_id}for i in a]
    return e 

# get student info 
# @app.route('/get', methods=['GET'])
# def topcourse():
#     a = db.engine.execute("SELECT course_id, COUNT(course_id) as cid from transaction where status_id = 1 group by course_id order by cid desc limit 5")
#     b = []
#     c = []
#     e = []
#     for i in a:
#         b.append(i.course_id)
#         e.append(i.cid)
#     for j in range(len(b)):
#         d = Course.query.filter_by(course_id=b[j]).first()
#         c.append({
#             "Name" : d.name,
#             "Total Enrolled" : e[j]
#             })
#     return c

@app.route('/profile', methods=['GET'])
def getinfo():
    login = BasicAuth()
    uname = login[0]
    passw = login[1]
    email = login[5]
    fname = login[2]
    cek = User.query.filter_by(username=uname).filter_by(password=passw).first()
    if cek:
        # return "True"
        # jwt encode untuk meng-encode hasil inputan
        
                # 'exp': 
        # secret untuk melakukan encode, algorithm buat metode yang dipakai(format)
        # datetime.now()
        # + dt.timedelta(hours=24)
        return [cek.fullname, cek.username, cek.email]
    else:
        return {"message" : "False"}

#get course that has been enrolled by user a
@app.route('/statusenroll/<id>', methods=['GET'])
def statusenroll(id):
    a = db.engine.execute('SELECT a.coursestatus_id, a.user_id, a.course_id, b.status, c.name FROM transaction as a, status as b, course as c WHERE b.status_id = a.status_id and c.course_id = a.course_id and a.user_id='+str(id)+' and a.status_id = 1')
    arr = []
    for i in a:
        arr.append({'coursestatus_id':i[0], 'user_id':i[1], 'course_id':i[2], 'status':i[3], 'name':i[4]})
    return arr
    # arr = []
    # judul = []
    # email = []
    # judul.append(coursename.name)
    # for i in list: #untuk mencari email yang meng-enroll si course itu
    #     user = User.query.filter_by(user_id=i.user_id).first()
    #     arr.append(user.fullname)
    #     email.append(user.email)

    # return jsonify({
    #     "Course Name" : judul[0],
    #     "Student Name" : [{
    #         "1.Nama" : arr[user],
    #         "2.Email" : email[user]
    #     } for user in range(len(arr))]
    # })

@app.route('/teachercourse', methods=['GET'])
def tcourse():
    login = BasicAuth2()
    uname = login[4]
    passw = login[5]
    cek = Teacher.query.filter_by(username=uname).filter_by(password=passw).first()
    cek2 = Course.query.filter_by(teacher_id=login[2]).all()
    if cek:
        arr = []
        for x in cek2:
            arr.append({
            "Course" : x.name,
            "Institution" : x.institution,
            "Level" : x.level,
            "Topics" : x.subject_id,
            "Precourse" : x.precourse_id,
            "Description" : x.description,
            "ID" : x.course_id
            })
        return jsonify(arr)
    else:
        return {"message" : "False"} 


@app.route('/dataenrolled', methods=['GET'])
def dataenrolled():
    login = BasicAuth2()
    r = login[2]
    a = db.engine.execute('SELECT a.course_id,a.name,a.teacher_id,b.user_id FROM course as a,transaction as b WHERE a.course_id=b.course_id AND a.teacher_id= '+str(r)+'')
    arr = []
    
    for i in a:
         
        user = User.query.filter_by(user_id=i[3]).first()
        
        arr.append({
            'teacher_id':i[2],'course_id':i[0],'nama':i[1],'usr_id':str(user.user_id),'name':str(user.fullname),'email':str(user.email)
        })
    return jsonify(arr)