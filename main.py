from sql import get_db_session
from sql.orm_models.config_model import Division_Student, Student, Teacher, Division, Division_Teacher, Subject, Attendance
from sqlalchemy import and_
from flask import Flask, render_template, url_for, request, redirect, session, flash
from datetime import datetime
from sqlalchemy import func


app = Flask(__name__)

app.secret_key = 'abc-test1' # for flask session

@app.route('/', methods = ['GET'])
def home_page():
    if 'user' not in session:
        return render_template('home_page.html')
    else:
        return redirect('/logout')

@app.route('/teacher_signup', methods = ['GET', 'POST'])
def teacher_signup():
    if request.method == 'GET':
        if 'user' not in session:
            return render_template('teacher_signup_page.html')
        else:
            return redirect('/logout')

    elif request.method == 'POST':
        name = request.form['name']
        division = request.form['division'].upper()
        sub = request.form['sub'].upper()
        year = request.form['year']
        sem = request.form['sem']
        email = request.form['email']
        password = request.form['password']
        password2 = request.form['password2']
        # check if passwords match
        if password != password2:
            flash('The passwords do not match...', 'error')
            return redirect('/teacher_signup')
        # check length of pass
        if len(password) < 6:
            flash('The password has to be more than 5 characters long...', 'error')
            return redirect('/teacher_signup')
        
        # auth user
        try:
            config_req_teacher = {
                "email" : email,
                "name": name,
                "password": password,
                "division": division,
                "sem": sem,
                "year": year,
                "subject": sub
            }
            teacher_user = Teacher(**config_req_teacher)
            with get_db_session() as transaction_session:
                transaction_session.add(teacher_user)
                transaction_session.commit()
                transaction_session.refresh(teacher_user)

            with get_db_session() as transaction_session:
                obj: Division = (
                    transaction_session.query(Division)
                    .filter(and_(Division.division == division, Division.sem == sem, Division.year == year))
                    .first()
                )
                if obj is not None:
                    div_user = obj.__dict__
                else:
                    config_req_div = {
                    "division": division,
                    "sem": sem,
                    "year": year
                    }
                    div_user = Division(**config_req_div)

                    transaction_session.add(div_user)
                    transaction_session.commit()
                    transaction_session.refresh(div_user)

            config_req_div_teacher = {
                "division": division,
                "teacher_email" : email
            }
            div_teacher = Division_Teacher(**config_req_div_teacher)
            print("div_teacher" , config_req_div_teacher)
            with get_db_session() as transaction_session:
                transaction_session.add(div_teacher)
                transaction_session.commit()
                transaction_session.refresh(div_teacher)

            config_req_sub = {
                "teacher_email" : email,
                "division": division,
                "name" : sub,
                "sem" : sem,
                "year": year
            }
            
            sub_user = Subject(**config_req_sub)
            with get_db_session() as transaction_session:
                transaction_session.add(sub_user)
                transaction_session.commit()
                transaction_session.refresh(sub_user)
            
        except Exception as error:
            print(error)
            flash('Something went wrong, please try again...', 'error')
            return redirect('/teacher_signup')

        flash('Registration successful! Please check your e-mail for verification and then log in...', 'info')
        return redirect('/teacher_login')

@app.route('/teacher_login', methods = ['GET', 'POST'])
def teacher_login():
    if request.method == 'GET':
        if 'user' not in session:
            return render_template('teacher_login_page.html')
        else:
            return redirect('/logout')

    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        division = request.form['division'].upper()
        subject = request.form['subject'].upper()

        try:
            with get_db_session() as transaction_session:
                obj: Teacher = (
                    transaction_session.query(Teacher)
                    .filter(and_(Teacher.email == email, Teacher.division == division, Teacher.password == password, Teacher.subject==subject))
                    .first()
                )
            if obj is not None:
                session['division'] = division
                session['user'] = email
                session['person_type'] = 'teacher'
                session['subject']= subject
                return redirect('/teacher_dashboard')
            else:
                flash('Incorrect, unverified or non-existent e-mail, division or password...', 'error')
                return redirect('/teacher_login')
        except Exception as e:
            print(e)
            flash('Incorrect, unverified or non-existent e-mail, division or password...', 'error')
            return redirect('/teacher_login')
        
@app.route('/teacher_dashboard', methods = ['GET'])
def teacher_dashboard():
    if 'user' in session and session['person_type'] == 'teacher':
        try:
            with get_db_session() as transaction_session:
                obj: Teacher = (
                    transaction_session.query(Teacher)
                    .filter(and_(Teacher.email == session['user'], Teacher.division == session['division']))
                    .first()
                )
            if obj is not None:
                teacher_details = obj.__dict__
            else:
                teacher_details = {}
                
            with get_db_session() as transaction_session:
                obj: Subject = (
                    transaction_session.query(Subject)
                    .filter(and_(Subject.teacher_email == session['user'], Subject.division == session['division'], Subject.name == session['subject']))
                    .first()
                )
            subject_details= obj.__dict__
            subject_id = subject_details["id"]
            
            with get_db_session() as transaction_session:
                student_email_count: Attendance = (
                    transaction_session.query(Attendance)
                    .filter(and_(Attendance.teacher_email == session['user'], Attendance.subject_id == subject_id))
                    .with_entities(Attendance.student_email, func.count(Attendance.date).label('count'))
                    .group_by(Attendance.student_email).all()
                )
                
                number_lecture: Attendance = (
                    transaction_session.query(Attendance)
                    .filter(and_(Attendance.teacher_email == session['user'], Attendance.subject_id == subject_id))
                    .with_entities(Attendance.date)
                    .distinct().count()
                )        
                
            students=[]
            for student in student_email_count:                
                with get_db_session() as transaction_session:
                    student_details: Student = (
                        transaction_session.query(Student)
                        .filter(Student.email == student[0])
                        .first()
                    )
                    student_details = student_details.__dict__
                    rollno = student_details["rollno"]
                    name = student_details["name"]
                    percentage = (student[1]/number_lecture)*100
                    lec_attended = student[1]
                    
                    stud_obj = {
                       "rollno":rollno,
                        "name": name,
                        "percentage": percentage,
                        "lec_attended":lec_attended
                    }
                    students.append(stud_obj)
                    
                
        except Exception as e:
            print(e)
            flash('Error occured!', 'error')
        return render_template('teacher_dashboard_page.html', teacher_details = teacher_details, lec_conducted_count = number_lecture, students = students)
    else:
        return redirect('/logout')

@app.route('/student_login', methods = ['GET', 'POST'])
def student_login():
    if request.method == 'GET':
        if 'user' not in session:
            return render_template('student_login_page.html')
        else:
            return redirect('/logout')

    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        division = request.form['division'].upper()
        
        try:
            with get_db_session() as transaction_session:
                obj: Student = (
                    transaction_session.query(Student)
                    .filter(and_(Student.email == email, Student.division == division, Student.password == password))
                    .first()
                )
            if obj is not None:
                session['division'] = division
                session['user'] = email
                session['person_type'] = 'student'
                return redirect('/student_dashboard')
            else:
                flash('Incorrect, unverified or non-existent e-mail, division or password...', 'error')
                return redirect('/student_login')
        except Exception as e:
            print(e)
            flash('Incorrect, unverified or non-existent e-mail, division or password...', 'error')
            return redirect('/student_login')

@app.route('/student_dashboard', methods = ['GET'])
def student_dashboard():
    if 'user' in session and session['person_type'] == 'student':
        try:
            with get_db_session() as transaction_session:
                obj: Student = (
                    transaction_session.query(Student)
                    .filter(and_(Student.email == session['user'], Student.division == session['division']))
                    .first()
                )
            if obj is not None:
                student_details = obj.__dict__
            else:
                student_details = {}
                
            with get_db_session() as transaction_session:
                student_attendance: Attendance = (
                    transaction_session.query(Attendance)
                    .filter(and_(Attendance.student_email == session['user'])).with_entities(Attendance.teacher_email, Attendance.subject_id , func.count(Attendance.date).label('count')).group_by(Attendance.subject_id).all()
                )

                number_lecture: Attendance = (
                    transaction_session.query(Attendance)
                    .with_entities(Attendance.date, Attendance.subject_id)
                    .with_entities(Attendance.subject_id , func.count(Attendance.date.distinct()).label('count'))
                    .group_by(Attendance.subject_id).all()
                )

                # number_lecture: Attendance = (
                #     transaction_session.query(func.count(distinct(tuple_(Attendance.subject_id, Attendance.date)))).scalar()
                # )


            print("number_lecture" , number_lecture)
            
            att_details = []
            for student in student_attendance:
                subject_id = student[1]
                teacher_email= student[0]
                lec_attended =  student[2]
                lec_cond = [i for i in number_lecture if i[0] == subject_id][0][1]                                
                percentage = (lec_attended/lec_cond)*100
                
                with get_db_session() as transaction_session:
                    obj: Subject = (
                        transaction_session.query(Subject)
                        .filter(and_(Subject.teacher_email == teacher_email, Subject.division == session['division'], Subject.id == subject_id))
                        .first()
                    )
                    subject_details= obj.__dict__
                subject_name= subject_details["name"]
                
                stud_obj = {
                    "subject":subject_name,
                    "teacher_email": teacher_email,
                    "lec_attended": lec_attended,
                    "lec_cond":lec_cond,
                    "percentage":percentage
                }
                
                att_details.append(stud_obj)                
        except Exception as e:
            print(e)
            flash('Error occured!', 'error')
        
        return render_template('student_dashboard_page.html', student_details = student_details, division = session['division'], attendance = att_details)
    else:
        return redirect('/logout')

@app.route('/student_signup', methods = ['GET', 'POST'])
def student_signup():
    if request.method == 'GET':
        if 'user' not in session:
            return render_template('student_signup_page.html')
        else:
            return redirect('/logout')

    elif request.method == 'POST':
        name = request.form['name']
        rollno = request.form['roll_no']
        division = request.form['division'].upper()
        year = request.form['year']
        sem = request.form['sem']
        email = request.form['email']
        password = request.form['password']
        password2 = request.form['password2']
        
        # check if passwords match
        if password != password2:
            flash('The passwords do not match...', 'error')
            return redirect('/student_signup')
        # check length of pass
        if len(password) < 6:
            flash('The password has to be more than 6 characters long...', 'error')
            return redirect('/student_signup')
        
        try: 
            config_req_stud = {
                "email" : email,
                "name": name,
                "rollno": rollno,
                "password": password,
                "division": division,
                "sem": sem,
                "year": year
            }
            student_user = Student(**config_req_stud)
            with get_db_session() as transaction_session:
                transaction_session.add(student_user)
                transaction_session.commit()
                transaction_session.refresh(student_user)

            config_req_div_student = {
                "division": division,
                "student_email" : email
            }
            print("config req division student", config_req_div_student)
            div_student = Division_Student(**config_req_div_student)
            with get_db_session() as transaction_session:
                transaction_session.add(div_student)
                transaction_session.commit()
                transaction_session.refresh(div_student)

            student_details = student_user.__dict__
            flash('Registration successful! Please check your e-mail for verification and then log in...', 'info')
            return redirect('/student_login')
        except Exception as error:
            print(error)
            flash('Registration unsuccessful!', 'info')
            return redirect('/student_signup')

@app.route('/logout', methods = ['GET'])
def logout():
    if 'user' in session:
        session.pop('user', None)
        session.pop('person_type', None)
        session.pop('division', None)

        flash('You have been logged out...', 'warning')
        return redirect('/')
    else:
        return redirect('/') 

@app.route('/add_edit_lecture', methods = ['GET', 'POST'])
def add_edit_lecture():
    if request.method == 'GET':
        if 'user' in session and session['person_type'] == 'teacher':
            # get teacher details
            # teacher_details = db.collection('teacher').document(session['user']).get()
            try: 
                with get_db_session() as transaction_session:
                    teacher: Teacher = (
                        transaction_session.query(Teacher)
                        .filter(Teacher.email == session['user'])
                        .first()
                    )
                    teacher_details = teacher.__dict__
                    
                    students: Student = (
                    transaction_session.query(Student)
                        .filter(Student.division == session['division'])
                        .all()
                    )
                    student_details= [row.__dict__ for row in students]
                    
                count = 0
                for student in student_details:
                    count += 1
                if count == 0:
                    flash('No students in division to add lecture...', 'info')
                    return redirect('/teacher_dashboard')
                return render_template('add_edit_lecture_page.html', students = student_details, teacher_details = teacher_details)
            
            except Exception as e:
                flash("Error,")
                return redirect('/logout')
            
        else:
            return redirect('/logout')

    elif request.method == 'POST':
        # get date and attendance
        date = request.form['date']
        student_email = request.form.getlist('check-box')
        
        with get_db_session() as transaction_session:
            obj: Subject = (
                transaction_session.query(Subject)
                .filter(and_(Subject.teacher_email == session['user'], Subject.division == session['division'], Subject.name == session['subject']))
                .first()
            )
            subject_details= obj.__dict__
        subject_id = subject_details["id"]
            
        date = datetime.strptime(date, "%Y-%m-%d").date()
        
        for student in student_email:
            config_req = {
                "subject_id": subject_id,
                "date": date,
                "student_email" : student,
                "teacher_email": session['user']
            }
            
            attendance_item = Attendance(**config_req)
            with get_db_session() as transaction_session:
                transaction_session.add(attendance_item)
                transaction_session.commit()
                transaction_session.refresh(attendance_item)
        

        flash('Lecture added/edited successfully...', 'info')
        return redirect('/teacher_dashboard')
    
if __name__ == '__main__':
    app.run(debug = True)