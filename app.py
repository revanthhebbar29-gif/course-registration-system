from flask import Flask, render_template, request
import mysql.connector

app = Flask(__name__)

# MySQL Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="ReVu@2509",
    database="course_registration"
)

cursor = db.cursor()

# ---------------- HOME PAGE ----------------
@app.route('/')
def home():
    return render_template('index.html')


# ---------------- REGISTER STUDENT ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        department = request.form['department']
        semester = request.form['semester']

        sql = """
        INSERT INTO students
        (name, email, department, semester)
        VALUES (%s, %s, %s, %s)
        """

        values = (name, email, department, semester)

        cursor.execute(sql, values)
        db.commit()

        return "<h2>Student Registered Successfully!</h2><a href='/'>Go Home</a>"

    return render_template('register.html')


# ---------------- VIEW STUDENTS ----------------
@app.route('/students')
def students():

    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()

    return render_template('students.html', students=data)


# ---------------- VIEW COURSES ----------------
@app.route('/courses')
def courses():

    cursor.execute("SELECT * FROM courses")
    data = cursor.fetchall()

    return render_template('courses.html', courses=data)


# ---------------- ENROLLMENT FORM ----------------
@app.route('/enrollment', methods=['GET', 'POST'])
def enrollment():

    # dropdown data
    cursor.execute("SELECT student_id, name FROM students")
    students = cursor.fetchall()

    cursor.execute("SELECT course_id, course_name FROM courses")
    courses = cursor.fetchall()

    if request.method == 'POST':

        student_id = request.form['student_id']
        course_id = request.form['course_id']

        sql = "INSERT INTO enrollment(student_id, course_id) VALUES (%s, %s)"
        values = (student_id, course_id)

        cursor.execute(sql, values)
        db.commit()

        return "<h2>Enrollment Successful!</h2><a href='/enrollment'>Back</a>"

    return render_template('enrollment.html', students=students, courses=courses)


# ---------------- ENROLLMENT VIEW (JOIN QUERY) ----------------
@app.route('/enrollment_view')
def enrollment_view():

    query = """
    SELECT students.name, courses.course_name
    FROM enrollment
    JOIN students ON enrollment.student_id = students.student_id
    JOIN courses ON enrollment.course_id = courses.course_id
    """

    cursor.execute(query)
    data = cursor.fetchall()

    return render_template('enrollment_view.html', data=data)


# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM courses")
    total_courses = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM enrollment")
    total_enrollments = cursor.fetchone()[0]

    return render_template(
        'dashboard.html',
        students=total_students,
        courses=total_courses,
        enrollments=total_enrollments
    )


    

@app.route('/delete_student/<int:id>')
def delete_student(id):

    # Step 1: delete from child table first
    cursor.execute("DELETE FROM enrollment WHERE student_id=%s", (id,))

    # Step 2: delete from parent table
    cursor.execute("DELETE FROM students WHERE student_id=%s", (id,))

    db.commit()

    return "<h3>Student Deleted Successfully</h3><a href='/students'>Back</a>"

@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):

    # GET existing data
    cursor.execute("SELECT * FROM students WHERE student_id=%s", (id,))
    student = cursor.fetchone()

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        department = request.form['department']
        semester = request.form['semester']

        sql = """
        UPDATE students
        SET name=%s, email=%s, department=%s, semester=%s
        WHERE student_id=%s
        """

        values = (name, email, department, semester, id)

        cursor.execute(sql, values)
        db.commit()

        return "<h3>Student Updated Successfully</h3><a href='/students'>Back</a>"

    return render_template('edit_student.html', student=student)


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)